"""Skill configuration — endpoints, autonomy level, tier limits."""

from enum import StrEnum

from pydantic import BaseModel


class AutonomyLevel(StrEnum):
    ASK_ALWAYS = "ask_always"  # Always ask owner (default, least privileged)
    AUTO_ACCEPT_NOTIFY = "auto_accept_notify"  # Auto-accept, notify owner
    FULL_AUTO = "full_auto"  # Handle everything, escalate at high tiers


class DAPConfig(BaseModel):
    relay_url: str = "ws://localhost:8080"
    registry_url: str = "http://localhost:8081"
    autonomy: AutonomyLevel = AutonomyLevel.ASK_ALWAYS
    max_disclosure_tier: int = 2
    data_dir: str = "./dap_data"
