"""DAPAgent — main interface for the OpenClaw DAP skill."""

import asyncio
import base64
import json
import logging

import httpx
from nacl.signing import SigningKey, VerifyKey

from dap import (
    generate_keypair,
    generate_recovery_keypair,
    derive_agent_id,
    create_agent_description,
    sign_message,
    verify_signature,
    ed25519_to_x25519_private,
    ed25519_to_x25519_public,
    x25519_key_exchange,
    derive_session_key,
    encrypt_payload,
    decrypt_payload,
    MessageType,
    Payload,
    Envelope,
    create_conversation_id,
    create_envelope,
    sign_envelope,
    verify_envelope,
    TranscriptStore,
    TOFUStore,
    KeyStatus,
)
from dap_registry.pow import generate_pow

from dap_skill.config import DAPConfig, AutonomyLevel
from dap_skill.listener import RelayListener
from dap_skill.store import DAPStore

logger = logging.getLogger(__name__)


def _encode_key(key: VerifyKey) -> str:
    return base64.urlsafe_b64encode(bytes(key)).rstrip(b"=").decode()


def _encode_sig(sig: bytes) -> str:
    return base64.urlsafe_b64encode(sig).rstrip(b"=").decode()


class DAPAgent:
    """High-level agent interface wrapping dap-core for OpenClaw skills."""

    def __init__(self, config: DAPConfig, store: DAPStore):
        self.config = config
        self.store = store
        self._private_key: SigningKey | None = None
        self._public_key: VerifyKey | None = None
        self._recovery_private: SigningKey | None = None
        self._recovery_public: VerifyKey | None = None
        self._agent_id: str | None = None
        self._description: dict | None = None
        self._transcript = TranscriptStore(db_path=f"{config.data_dir}/transcripts.db")
        self._tofu = TOFUStore(db_path=f"{config.data_dir}/tofu.db")
        self._ws = None
        self._listener: RelayListener | None = None
        self._pending_messages: list[dict] = []

        # Try to load existing identity
        kp = store.load_keypair()
        if kp:
            self._private_key, self._public_key = kp
            self._agent_id = store.load_agent_id()
            self._description = store.load_agent_description()
            rkp = store.load_recovery_keypair()
            if rkp:
                self._recovery_private, self._recovery_public = rkp

    @property
    def agent_id(self) -> str | None:
        return self._agent_id

    @property
    def public_key(self) -> VerifyKey | None:
        return self._public_key

    async def initialize(self, name: str, description: str = "") -> dict:
        """Generate keypairs, derive agent_id, create agent description."""
        self._private_key, self._public_key = generate_keypair()
        self._recovery_private, self._recovery_public = generate_recovery_keypair()
        self._agent_id = derive_agent_id(self._public_key)

        self._description = create_agent_description(
            agent_id=self._agent_id,
            name=name,
            public_key=self._public_key,
            recovery_key=self._recovery_public,
            endpoint={"relay": self.config.relay_url},
            description=description,
        )

        # Persist
        self.store.save_keypair(self._private_key, self._public_key)
        self.store.save_recovery_keypair(self._recovery_private, self._recovery_public)
        self.store.save_agent_id(self._agent_id)
        self.store.save_agent_description(self._description)

        return self._description

    # --- Registry ---

    async def register(self, pow_difficulty: int = 16) -> bool:
        """Register with configured registry. Handles PoW."""
        if not self._agent_id or not self._private_key:
            raise RuntimeError("Agent not initialized")

        pub_key_b64 = _encode_key(self._public_key)

        # Sign registration payload
        payload = json.dumps(
            {"agent_id": self._agent_id, "public_key": pub_key_b64},
            separators=(",", ":"),
            sort_keys=True,
        )
        signature = sign_message(self._private_key, payload.encode())

        # Solve PoW
        pow_nonce = generate_pow(self._agent_id, pow_difficulty)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.config.registry_url}/agents",
                json={
                    "agent_id": self._agent_id,
                    "public_key": pub_key_b64,
                    "name": self._description.get("name", ""),
                    "signature": _encode_sig(signature),
                    "pow_nonce": pow_nonce,
                    "endpoint": {"relay": self.config.relay_url},
                    "description": self._description.get("description", ""),
                },
            )
        return resp.status_code == 201

    async def search(self, q: str = "") -> list[dict]:
        """Search registry for agents matching a free-text query."""
        params = {}
        if q:
            params["q"] = q

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.config.registry_url}/agents", params=params)
        if resp.status_code == 200:
            return resp.json().get("agents", [])
        return []

    # --- Connections ---

    async def connect(self, target_agent_id: str, message: str = "") -> dict:
        """Send connection request to another agent via relay. Returns the envelope."""
        if not self._agent_id or not self._private_key:
            raise RuntimeError("Agent not initialized")

        # Determine epoch — increment if reconnecting (check BEFORE _fetch_agent_key
        # which may create a "known" connection entry as a cache side-effect)
        existing = self.store.get_connection(target_agent_id)
        epoch = existing["epoch"] + 1 if existing else 1

        # Fetch target's public key from registry
        target_pub_key = await self._fetch_agent_key(target_agent_id)

        payload = Payload(type=MessageType.CONNECTION_REQUEST, content=message)
        envelope = create_envelope(
            from_id=self._agent_id,
            to_id=target_agent_id,
            payload=payload,
            disclosure_tier=0,
            connection_epoch=epoch,
        )

        # Encrypt and sign
        envelope = self._encrypt_envelope(envelope, payload, target_pub_key)
        envelope = sign_envelope(self._private_key, envelope)

        # Store outbound connection as pending
        self.store.save_connection(target_agent_id, "pending_outbound", public_key=_encode_key(target_pub_key), epoch=epoch)

        # Record in transcript
        self._transcript.append_message(envelope.conversation_id, envelope)

        return envelope.model_dump()

    async def accept_connection(self, from_agent_id: str) -> dict:
        """Accept a pending connection request.

        Works for both normal inbound requests (pending_requests table) and
        mutual requests (we have pending_outbound in connections table), and
        reconnection (we have connected status but peer re-requested).
        """
        pending = self.store.get_pending_request(from_agent_id)
        if not pending:
            # Check for mutual request or reconnection
            conn = self.store.get_connection(from_agent_id)
            if not conn or conn["status"] not in ("pending_outbound", "connected"):
                raise ValueError(f"No pending request from {from_agent_id}")

        # Get epoch from existing connection
        conn = self.store.get_connection(from_agent_id)
        epoch = conn["epoch"] if conn else 1

        # Get the requester's public key
        target_pub_key = await self._fetch_agent_key(from_agent_id)

        payload = Payload(type=MessageType.CONNECTION_ACCEPTED, content="")
        envelope = create_envelope(
            from_id=self._agent_id,
            to_id=from_agent_id,
            payload=payload,
            disclosure_tier=0,
            sequence=2,
            connection_epoch=epoch,
        )
        envelope = self._encrypt_envelope(envelope, payload, target_pub_key)
        envelope = sign_envelope(self._private_key, envelope)

        # Update connection status
        self.store.save_connection(from_agent_id, "connected", public_key=_encode_key(target_pub_key), epoch=epoch)
        if pending:
            self.store.remove_pending_request(from_agent_id)

        # Record in transcript
        self._transcript.append_message(envelope.conversation_id, envelope)

        return envelope.model_dump()

    async def decline_connection(self, from_agent_id: str) -> dict:
        """Decline a pending connection request."""
        pending = self.store.get_pending_request(from_agent_id)
        if not pending:
            raise ValueError(f"No pending request from {from_agent_id}")

        # Get epoch from existing connection
        conn = self.store.get_connection(from_agent_id)
        epoch = conn["epoch"] if conn else 1

        target_pub_key = await self._fetch_agent_key(from_agent_id)

        payload = Payload(type=MessageType.CONNECTION_DECLINED, content="")
        envelope = create_envelope(
            from_id=self._agent_id,
            to_id=from_agent_id,
            payload=payload,
            disclosure_tier=0,
            sequence=2,
            connection_epoch=epoch,
        )
        envelope = self._encrypt_envelope(envelope, payload, target_pub_key)
        envelope = sign_envelope(self._private_key, envelope)

        self.store.remove_pending_request(from_agent_id)

        self._transcript.append_message(envelope.conversation_id, envelope)

        return envelope.model_dump()

    async def revoke_connection(self, agent_id: str) -> dict:
        """Revoke an existing connection."""
        conn = self.store.get_connection(agent_id)
        if not conn or conn["status"] != "connected":
            raise ValueError(f"No active connection with {agent_id}")

        epoch = conn["epoch"]

        target_pub_key = await self._fetch_agent_key(agent_id)

        payload = Payload(type=MessageType.CONNECTION_REVOKED, content="")
        envelope = create_envelope(
            from_id=self._agent_id,
            to_id=agent_id,
            payload=payload,
            disclosure_tier=0,
            connection_epoch=epoch,
        )
        envelope = self._encrypt_envelope(envelope, payload, target_pub_key)
        envelope = sign_envelope(self._private_key, envelope)

        self.store.remove_connection(agent_id)

        self._transcript.append_message(envelope.conversation_id, envelope)

        return envelope.model_dump()

    # --- Messaging ---

    async def send_message(self, to_agent_id: str, content: str, tier: int = 1) -> dict:
        """Send encrypted, signed message to a connected agent."""
        if tier > self.config.max_disclosure_tier:
            raise ValueError(f"Tier {tier} exceeds max allowed {self.config.max_disclosure_tier}")

        conn = self.store.get_connection(to_agent_id)
        if not conn or conn["status"] != "connected":
            raise ValueError(f"No active connection with {to_agent_id}")

        target_pub_key = await self._fetch_agent_key(to_agent_id)

        # Get current sequence
        convo_id = create_conversation_id(self._agent_id, to_agent_id)
        transcript = self._transcript.get_transcript(convo_id)
        sequence = len(transcript) + 1

        epoch = conn["epoch"]

        payload = Payload(type=MessageType.CONVERSATION, content=content)
        envelope = create_envelope(
            from_id=self._agent_id,
            to_id=to_agent_id,
            payload=payload,
            disclosure_tier=tier,
            sequence=sequence,
            connection_epoch=epoch,
        )
        envelope = self._encrypt_envelope(envelope, payload, target_pub_key)
        envelope = sign_envelope(self._private_key, envelope)

        self._transcript.append_message(convo_id, envelope)

        return envelope.model_dump()

    async def get_messages(self, agent_id: str | None = None) -> list[dict]:
        """Get decrypted transcript of messages with a specific agent (or all)."""
        if agent_id:
            return await self._decrypt_transcript(agent_id)

        # All connections
        results = []
        for conn in self.store.list_connections():
            results.extend(await self._decrypt_transcript(conn["agent_id"]))
        return results

    async def _decrypt_transcript(self, agent_id: str) -> list[dict]:
        """Decrypt all messages in a conversation with the given agent."""
        convo_id = create_conversation_id(self._agent_id, agent_id)
        envelopes = self._transcript.get_transcript(convo_id)
        results = []
        for env in envelopes:
            other_id = env.to_id if env.from_id == self._agent_id else env.from_id
            try:
                other_key = await self._fetch_agent_key(other_id)
                payload = self._decrypt_envelope(env, other_key)
                results.append({
                    "from": env.from_id,
                    "to": env.to_id,
                    "type": payload.type,
                    "content": payload.content,
                    "timestamp": env.timestamp,
                    "sequence": env.sequence,
                })
            except Exception:
                logger.warning("Could not decrypt message %s", env.message_id)
                results.append({
                    "from": env.from_id,
                    "to": env.to_id,
                    "type": "encrypted",
                    "content": None,
                    "timestamp": env.timestamp,
                    "sequence": env.sequence,
                })
        return results

    # --- Relay ---

    async def connect_relay(self):
        """Connect to relay via WebSocket, authenticate with TOFU challenge-response."""
        import websockets

        self._ws = await websockets.connect(self.config.relay_url.replace("http", "ws") + "/ws")

        # REGISTER
        await self._ws.send(json.dumps({
            "type": "REGISTER",
            "agent_id": self._agent_id,
            "public_key": _encode_key(self._public_key),
        }))
        challenge = json.loads(await self._ws.recv())
        if challenge["type"] != "CHALLENGE":
            raise RuntimeError(f"Relay auth failed: {challenge}")

        # PROVE
        nonce = challenge["nonce"]
        sig = sign_message(self._private_key, nonce.encode())
        await self._ws.send(json.dumps({
            "type": "PROVE",
            "agent_id": self._agent_id,
            "signature": _encode_sig(sig),
        }))
        result = json.loads(await self._ws.recv())
        if result["type"] != "REGISTERED":
            raise RuntimeError(f"Relay auth failed: {result}")

    async def disconnect_relay(self):
        """Disconnect from relay."""
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def send_via_relay(self, envelope_dict: dict, to_agent_id: str):
        """Send an envelope through the relay."""
        if not self._ws:
            raise RuntimeError("Not connected to relay")

        await self._ws.send(json.dumps({
            "type": "FORWARD",
            "to": to_agent_id,
            "encrypted_payload": json.dumps(envelope_dict),
        }))

    async def receive_from_relay(self) -> dict | None:
        """Receive one message from the relay. Returns the parsed delivery dict."""
        if not self._ws:
            raise RuntimeError("Not connected to relay")
        raw = await self._ws.recv()
        return json.loads(raw)

    # --- Background listener ---

    async def start_listening(self) -> None:
        """Start a persistent background relay listener."""
        if not self._agent_id or not self._private_key:
            raise RuntimeError("Agent not initialized")
        if self._listener and self._listener.running:
            return

        self._listener = RelayListener(
            private_key=self._private_key,
            public_key=self._public_key,
            agent_id=self._agent_id,
            relay_url=self.config.relay_url,
            on_message=self._on_message_received,
        )
        await self._listener.start()

    async def stop_listening(self) -> None:
        """Stop the background relay listener."""
        if self._listener:
            await self._listener.stop()
            self._listener = None

    async def _on_message_received(self, deliver_data: dict) -> None:
        """Callback invoked by RelayListener when a DELIVER message arrives."""
        try:
            encrypted_payload = deliver_data.get("encrypted_payload", "")
            envelope_dict = json.loads(encrypted_payload)
            result = await self.process_incoming(envelope_dict)
            if result:
                # Send acceptance back via relay if auto-accepted
                accept_env = result.pop("accept_envelope", None)
                if accept_env and self._listener:
                    await self._listener.send({
                        "type": "FORWARD",
                        "to": result["from_agent_id"],
                        "encrypted_payload": json.dumps(accept_env),
                    })
                    logger.info("Sent acceptance back to %s via relay", result["from_agent_id"])
                self._pending_messages.append(result)
                logger.info("Processed incoming message: %s", result.get("action"))
        except Exception:
            logger.exception("Failed to process delivered message")

    def get_pending_messages(self) -> list[dict]:
        """Return and clear all pending messages received by the listener."""
        messages = list(self._pending_messages)
        self._pending_messages.clear()
        return messages

    async def process_incoming(self, envelope_dict: dict) -> dict | None:
        """Process an incoming envelope. Returns an action dict describing what happened.

        Accepts either a raw envelope dict or a relay DELIVER wrapper
        ({"type": "DELIVER", "from": ..., "encrypted_payload": "..."}).

        For connection requests (default autonomy=ASK_ALWAYS):
            {action: 'ask_owner', from_agent_id: ..., message: ...}
        For auto-accept:
            {action: 'auto_accepted', from_agent_id: ...}
        For conversation messages:
            {action: 'delivered', from_agent_id: ..., content: ...}
        """
        # Unwrap relay DELIVER wrapper if present
        if envelope_dict.get("type") == "DELIVER" and "encrypted_payload" in envelope_dict:
            envelope_dict = json.loads(envelope_dict["encrypted_payload"])

        envelope = Envelope.model_validate(envelope_dict)
        from_id = envelope.from_id

        # Fetch sender's public key and verify
        sender_pub_key = await self._fetch_agent_key(from_id)
        if not verify_envelope(sender_pub_key, envelope):
            return {"action": "error", "reason": "invalid signature"}

        # TOFU check
        key_status = self._tofu.verify_key(from_id, sender_pub_key)
        if key_status == KeyStatus.NEW:
            self._tofu.cache_key(from_id, sender_pub_key)
        elif key_status == KeyStatus.CHANGED:
            return {"action": "error", "reason": "public key changed"}

        # --- Epoch check ---
        local_conn = self.store.get_connection(from_id)
        local_epoch = local_conn["epoch"] if local_conn else 0
        msg_epoch = envelope.connection_epoch

        if local_conn and msg_epoch < local_epoch:
            # Stale message from old epoch — don't process
            return {
                "action": "epoch_mismatch",
                "from_agent_id": from_id,
                "local_epoch": local_epoch,
                "message_epoch": msg_epoch,
            }

        if local_conn and msg_epoch > local_epoch:
            # Other side re-established — update our epoch
            self.store.save_connection(
                from_id, local_conn["status"],
                public_key=local_conn["public_key"],
                epoch=msg_epoch,
            )

        # Decrypt payload
        payload = self._decrypt_envelope(envelope, sender_pub_key)

        # Record in transcript
        self._transcript.append_message(envelope.conversation_id, envelope)

        if payload.type == MessageType.CONNECTION_REQUEST:
            return await self._handle_connection_request(from_id, payload, envelope)

        elif payload.type == MessageType.CONNECTION_ACCEPTED:
            self.store.save_connection(from_id, "connected", public_key=_encode_key(sender_pub_key), epoch=envelope.connection_epoch)
            return {"action": "connection_accepted", "from_agent_id": from_id}

        elif payload.type == MessageType.CONNECTION_DECLINED:
            self.store.remove_connection(from_id)
            return {"action": "connection_declined", "from_agent_id": from_id}

        elif payload.type == MessageType.CONNECTION_REVOKED:
            self.store.remove_connection(from_id)
            return {"action": "connection_revoked", "from_agent_id": from_id}

        elif payload.type == MessageType.CONVERSATION:
            return {"action": "delivered", "from_agent_id": from_id, "content": payload.content, "tier": envelope.disclosure_tier}

        return {"action": "unknown", "type": str(payload.type)}

    # --- Private helpers ---

    async def _handle_connection_request(self, from_id: str, payload: Payload, envelope: Envelope) -> dict:
        """Handle an incoming connection request based on autonomy level."""
        # Mutual connection request or reconnection — auto-resolve
        existing = self.store.get_connection(from_id)
        if existing and existing["status"] in ("pending_outbound", "connected"):
            accept_env_dict = await self.accept_connection(from_id)
            return {
                "action": "auto_accepted",
                "from_agent_id": from_id,
                "message": payload.content,
                "mutual": existing["status"] == "pending_outbound",
                "accept_envelope": accept_env_dict,
            }

        # Store as pending
        self.store.save_pending_request(from_id, envelope.model_dump_json())

        if self.config.autonomy == AutonomyLevel.ASK_ALWAYS:
            return {"action": "ask_owner", "from_agent_id": from_id, "message": payload.content}

        # Auto-accept (AUTO_ACCEPT_NOTIFY or FULL_AUTO)
        accept_env_dict = await self.accept_connection(from_id)
        return {
            "action": "auto_accepted",
            "from_agent_id": from_id,
            "message": payload.content,
            "accept_envelope": accept_env_dict,
        }

    def _encrypt_envelope(self, envelope: Envelope, payload: Payload, target_pub_key: VerifyKey) -> Envelope:
        """Encrypt a payload into the envelope."""
        my_x25519 = ed25519_to_x25519_private(self._private_key)
        their_x25519 = ed25519_to_x25519_public(target_pub_key)
        shared = x25519_key_exchange(my_x25519, their_x25519)
        session_key = derive_session_key(shared, envelope.conversation_id)

        plaintext = payload.model_dump_json().encode()
        ciphertext = encrypt_payload(session_key, plaintext)
        envelope.encrypted_payload = base64.urlsafe_b64encode(ciphertext).rstrip(b"=").decode()
        return envelope

    def _decrypt_envelope(self, envelope: Envelope, sender_pub_key: VerifyKey) -> Payload:
        """Decrypt the envelope's payload."""
        my_x25519 = ed25519_to_x25519_private(self._private_key)
        their_x25519 = ed25519_to_x25519_public(sender_pub_key)
        shared = x25519_key_exchange(my_x25519, their_x25519)
        session_key = derive_session_key(shared, envelope.conversation_id)

        padded = envelope.encrypted_payload + "=" * (4 - len(envelope.encrypted_payload) % 4)
        ciphertext = base64.urlsafe_b64decode(padded)
        plaintext = decrypt_payload(session_key, ciphertext)
        return Payload.model_validate_json(plaintext)

    async def _fetch_agent_key(self, agent_id: str) -> VerifyKey:
        """Fetch an agent's public key from registry or local cache."""
        # Check local connections first
        conn = self.store.get_connection(agent_id)
        if conn and conn["public_key"]:
            padded = conn["public_key"] + "=" * (4 - len(conn["public_key"]) % 4)
            return VerifyKey(base64.urlsafe_b64decode(padded))

        # Fetch from registry
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.config.registry_url}/agents/{agent_id}")
        if resp.status_code != 200:
            raise ValueError(f"Agent {agent_id} not found in registry")

        data = resp.json()
        pub_key_b64 = data["public_key"]
        padded = pub_key_b64 + "=" * (4 - len(pub_key_b64) % 4)
        pub_key = VerifyKey(base64.urlsafe_b64decode(padded))

        # Cache in connections store
        self.store.save_connection(agent_id, "known", public_key=pub_key_b64)

        return pub_key
