#!/usr/bin/env python3
"""
x402 Payment

Handles the HTTP 402 payment flow:
- Default: EIP-3009 (transferWithAuthorization) to pay USDC
- Solana partial signing
- Permit2 (generic ERC-20 fallback)

Usage:

  # Full HTTP 402 flow (request + payment + retry)
  python3 pay.py pay \
    --url https://openapi.misttrack.io/x402/address_labels \
    --private-key <hex> \
    --chain-id 8453

  # Sign EIP-3009 payment from a 402 response
  python3 pay.py sign-eip3009 \
    --private-key <hex> \
    --token 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
    --chain-id 8453 \
    --to 0x209693Bc6afc0C5328bA36FaF03C514EF312287C \
    --amount 10000 \
    --token-name "USD Coin" \
    --token-version "2" \
    --max-timeout 60

  # Partially sign a Solana x402 transaction
  python3 pay.py sign-solana \
    --private-key <hex> \
    --transaction <base64-encoded-tx>

"""

import argparse
import base64
import json
import os
import sys
import time


def _keccak256(data: bytes) -> bytes:
    """Compute keccak256 hash."""
    from eth_utils import keccak
    return keccak(data)


def _eip712_hash(token_name, token_version, chain_id, token_address,
                 from_addr, to_addr, value, valid_after, valid_before,
                 nonce_bytes):
    """Compute the EIP-712 hash for TransferWithAuthorization (EIP-3009).

    This is a manual implementation to match the verification standard used by x402 receivers.
    eth_account.encode_typed_data encodes bytes32 differently, producing hashes that receivers reject.
    """
    from eth_abi import encode

    # EIP712Domain type hash
    domain_type_hash = _keccak256(
        b"EIP712Domain(string name,string version,"
        b"uint256 chainId,address verifyingContract)")
    domain_separator = _keccak256(
        domain_type_hash
        + _keccak256(token_name.encode())
        + _keccak256(token_version.encode())
        + encode(["uint256"], [chain_id])
        + encode(["address"], [token_address]))

    # TransferWithAuthorization type hash
    auth_type_hash = _keccak256(
        b"TransferWithAuthorization(address from,address to,"
        b"uint256 value,uint256 validAfter,uint256 validBefore,"
        b"bytes32 nonce)")
    struct_hash = _keccak256(
        auth_type_hash
        + encode(["address"], [from_addr])
        + encode(["address"], [to_addr])
        + encode(["uint256"], [value])
        + encode(["uint256"], [valid_after])
        + encode(["uint256"], [valid_before])
        + nonce_bytes)  # raw 32 bytes, not abi-encoded

    return _keccak256(b"\x19\x01" + domain_separator + struct_hash)


def sign_eip3009(private_key, token_address, chain_id, to, amount,
                 token_name="USD Coin", token_version="2", max_timeout=60):
    """Sign transferWithAuthorization (EIP-3009) for an x402 payment.

    Returns a dict with 'signature' and 'authorization' fields.
    """
    from eth_account import Account

    now = int(time.time())
    nonce_bytes = os.urandom(32)
    nonce_hex = "0x" + nonce_bytes.hex()
    acct = Account.from_key(private_key)

    valid_after = now - 600  # allow 10-minute clock skew (consistent with official SDK)
    valid_before = now + max_timeout

    msg_hash = _eip712_hash(
        token_name, token_version, chain_id, token_address,
        acct.address, to, int(amount), valid_after, valid_before, nonce_bytes)

    signed = acct.unsafe_sign_hash(msg_hash)

    return {
        "signature": "0x" + signed.signature.hex(),
        "authorization": {
            "from": acct.address,
            "to": to,
            "value": str(int(amount)),
            "validAfter": str(valid_after),
            "validBefore": str(valid_before),
            "nonce": nonce_hex,
        }
    }


def sign_solana_partial(private_key_hex, serialized_tx_b64):
    """Partially sign a Solana x402 payment transaction.

    Returns the base64-encoded transaction containing the partial signature.
    """
    import base58
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction

    kp = Keypair.from_seed(bytes.fromhex(private_key_hex))
    tx_bytes = base64.b64decode(serialized_tx_b64)
    vtx = VersionedTransaction.from_bytes(tx_bytes)

    # Find our signer index by matching public key
    our_index = -1
    for i, key in enumerate(vtx.message.account_keys):
        if key == kp.pubkey():
            our_index = i
            break

    if our_index == -1:
        raise ValueError(f"Wallet {kp.pubkey()} is not among the transaction signers")

    # Decode shortvec to find the signature array boundary
    original_bytes = bytes(vtx)
    idx = 0
    result = 0
    shift = 0
    while True:
        byte = original_bytes[idx]
        result |= (byte & 0x7F) << shift
        idx += 1
        if (byte & 0x80) == 0:
            break
        shift += 7
    sig_count = result
    sig_array_start = idx

    # Extract message bytes (after all signatures)
    msg_bytes = original_bytes[sig_array_start + sig_count * 64:]

    # Sign the message
    sig = kp.sign_message(msg_bytes)

    # Write signature into the correct slot
    new_tx = bytearray(original_bytes)
    offset = sig_array_start + our_index * 64
    new_tx[offset:offset + 64] = bytes(sig)

    return base64.b64encode(bytes(new_tx)).decode()


def build_payment_payload(payment_required, private_key, chain_id=None):
    """Build a PaymentPayload from a 402 PaymentRequired response.

    Accepts both a full PaymentRequired (containing accepts[]) and a single PaymentRequirements object.
    Automatically selects EIP-3009 or Solana based on the network.
    Returns a PaymentPayload dict ready to be placed in the PAYMENT-SIGNATURE header.
    """
    # Hard cap: reject payments over $1 USDC (1_000_000 units, 6 decimals)
    # This prevents a malicious server from draining the wallet by inflating 402 fees.
    MAX_AMOUNT = 1_000_000  # $1.00 USDC

    if "accepts" in payment_required:
        req = payment_required["accepts"][0]
    else:
        req = payment_required

    amount = int(req.get("amount", 0))
    if amount > MAX_AMOUNT:
        raise ValueError(
            f"Payment amount {amount} exceeds hard cap {MAX_AMOUNT} "
            f"(${amount / 1_000_000:.2f} > ${MAX_AMOUNT / 1_000_000:.2f} USDC). "
            f"Signing refused — possible malicious server."
        )

    scheme = req.get("scheme", "exact")
    network = req.get("network", "")

    payload = {
        "x402Version": 2,
        "accepted": req,
    }

    if network.startswith("eip155:"):
        # EVM payment
        cid = int(network.split(":")[1]) if not chain_id else chain_id
        extra = req.get("extra", {})
        method = extra.get("assetTransferMethod", "eip3009")

        if method == "eip3009":
            result = sign_eip3009(
                private_key=private_key,
                token_address=req["asset"],
                chain_id=cid,
                to=req["payTo"],
                amount=req["amount"],
                token_name=extra.get("name", "USD Coin"),
                token_version=extra.get("version", "2"),
                max_timeout=req.get("maxTimeoutSeconds", 60),
            )
            payload["payload"] = result
        else:
            raise NotImplementedError("Permit2 signing is not yet implemented")

    elif network.startswith("solana:"):
        raise NotImplementedError(
            "Solana x402 requires a pre-built transaction. "
            "Use the sign-solana subcommand on a pre-built transaction."
        )
    else:
        raise ValueError(f"Unsupported network: {network}")

    return payload


def cmd_sign_eip3009(args):
    """Sign an EIP-3009 transferWithAuthorization."""
    result = sign_eip3009(
        private_key=args.private_key,
        token_address=args.token,
        chain_id=args.chain_id,
        to=args.to,
        amount=args.amount,
        token_name=args.token_name,
        token_version=args.token_version,
        max_timeout=args.max_timeout,
    )
    print(json.dumps(result, indent=2))


def cmd_sign_solana(args):
    """Partially sign a Solana x402 transaction."""
    result = sign_solana_partial(args.private_key, args.transaction)
    print(result)


def request_with_x402(url, private_key, chain_id=None, method="GET", data=None, headers=None, auto_pay=False):
    """
    Programmatic HTTP 402 payment flow.
    If the response is HTTP 402, it will parse the 402 payment requirement,
    prompt for confirmation or auto-sign the payment, and retry the request
    with the PAYMENT-SIGNATURE header.
    """
    import requests as req_lib

    if headers is None:
        headers = {}
    if data:
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
    body = data.encode() if isinstance(data, str) else data

    # Step 1: Initial request
    resp = req_lib.request(method, url, headers=headers, data=body)

    if resp.status_code != 402:
        return resp

    # Step 2: Parse payment requirement
    pr_header = (resp.headers.get("payment-required")
                 or resp.headers.get("PAYMENT-REQUIRED", ""))
    if not pr_header:
        print(f"Error: 402 response missing payment-required header\nHeaders: {dict(resp.headers)}")
        return resp

    payment_required = json.loads(base64.b64decode(pr_header))  # x402 spec: header is base64-encoded JSON
    accepts = payment_required.get("accepts", [{}])
    req_info = accepts[0] if accepts else {}
    amount = int(req_info.get("amount", 0))
    decimals = 6  # USDC default
    usd = amount / (10 ** decimals)
    print(f"Payment required: ${usd:.6f} USDC on network {req_info.get('network', '?')}")
    print(f"  Recipient: {req_info.get('payTo', '?')}")
    print(json.dumps(payment_required, indent=2))

    if not auto_pay:
        confirm = input("\nConfirm payment? [y/N] ")
        if confirm.lower() != "y":
            print("Cancelled.")
            return None

    # Step 3: Build and sign payment
    payload = build_payment_payload(payment_required, private_key, chain_id)
    payment_sig = base64.b64encode(json.dumps(payload).encode()).decode()  # x402 spec: header is base64-encoded JSON

    # Step 4: Retry with payment
    headers["PAYMENT-SIGNATURE"] = payment_sig
    resp2 = req_lib.request(method, url, headers=headers, data=body)

    return resp2


def cmd_pay(args):
    """Full HTTP 402 payment flow: request → parse 402 → sign → retry."""
    headers = {}
    if args.header:
        for h in args.header:
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()

    resp2 = request_with_x402(
        url=args.url,
        private_key=args.private_key,
        chain_id=args.chain_id,
        method=args.method.upper(),
        data=args.data,
        headers=headers,
        auto_pay=args.auto
    )

    if not resp2:
        return

    print(f"\nResponse status: {resp2.status_code}")
    for hdr in ["payment-response", "PAYMENT-RESPONSE"]:
        if hdr in resp2.headers:
            pr = json.loads(base64.b64decode(resp2.headers[hdr]))  # x402 spec: header is base64-encoded JSON
            print("Settlement result:", json.dumps(pr, indent=2))
            break
    print(resp2.text[:5000])


def main():
    parser = argparse.ArgumentParser(description="x402 payment client")
    sub = parser.add_subparsers(dest="command")

    # sign-eip3009
    p = sub.add_parser("sign-eip3009", help="Sign an EIP-3009 transferWithAuthorization")
    p.add_argument("--private-key", default=os.environ.get("X402_PRIVATE_KEY"),
                   help="Hex private key (or set X402_PRIVATE_KEY env var)")
    p.add_argument("--token", required=True, help="Token contract address")
    p.add_argument("--chain-id", type=int, required=True, help="EVM chain ID")
    p.add_argument("--to", required=True, help="Payment recipient (payTo)")
    p.add_argument("--amount", type=int, required=True, help="Amount in smallest units (e.g. 10000 = $0.01 USDC)")
    p.add_argument("--token-name", default="USD Coin", help="EIP-712 domain token name")
    p.add_argument("--token-version", default="2", help="EIP-712 domain token version")
    p.add_argument("--max-timeout", type=int, default=60, help="Maximum timeout in seconds")
    p.set_defaults(func=cmd_sign_eip3009)

    # sign-solana
    p = sub.add_parser("sign-solana", help="Partially sign a Solana x402 transaction")
    p.add_argument("--private-key", default=os.environ.get("X402_PRIVATE_KEY"),
                   help="Hex private key, 32-byte seed (or set X402_PRIVATE_KEY env var)")
    p.add_argument("--transaction", required=True, help="Base64-encoded serialized transaction")
    p.set_defaults(func=cmd_sign_solana)

    # pay
    p = sub.add_parser("pay", help="Full HTTP 402 payment flow")
    p.add_argument("--url", required=True, help="URL to access")
    p.add_argument("--private-key", default=os.environ.get("X402_PRIVATE_KEY"),
                   help="Hex private key (or set X402_PRIVATE_KEY env var)")
    p.add_argument("--chain-id", type=int, help="Preferred chain ID")
    p.add_argument("--method", default="GET", help="HTTP method (default: GET)")
    p.add_argument("--data", help="Request body (JSON string)")
    p.add_argument("--header", nargs="*", help="Extra headers (key: value)")
    p.add_argument("--auto", action="store_true",
                   help="Auto-pay silently without confirmation (for testing only, do not use in production agents)")
    p.set_defaults(func=cmd_pay)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if hasattr(args, "private_key") and not args.private_key:
        print("Error: --private-key is required (or set X402_PRIVATE_KEY env var)")
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
