"""Tests for DAPConfig and AutonomyLevel."""

from dap_skill.config import DAPConfig, AutonomyLevel


def test_default_config():
    config = DAPConfig()
    assert config.relay_url == "ws://localhost:8080"
    assert config.registry_url == "http://localhost:8081"
    assert config.autonomy == AutonomyLevel.ASK_ALWAYS
    assert config.max_disclosure_tier == 2
    assert config.data_dir == "./dap_data"


def test_custom_config():
    config = DAPConfig(
        relay_url="ws://custom:9090",
        registry_url="http://custom:9091",
        autonomy=AutonomyLevel.FULL_AUTO,
        max_disclosure_tier=3,
        data_dir="/tmp/dap_test",
    )
    assert config.relay_url == "ws://custom:9090"
    assert config.autonomy == AutonomyLevel.FULL_AUTO
    assert config.max_disclosure_tier == 3


def test_autonomy_levels():
    assert AutonomyLevel.ASK_ALWAYS == "ask_always"
    assert AutonomyLevel.AUTO_ACCEPT_NOTIFY == "auto_accept_notify"
    assert AutonomyLevel.FULL_AUTO == "full_auto"


def test_config_from_dict():
    config = DAPConfig.model_validate({"autonomy": "full_auto", "max_disclosure_tier": 1})
    assert config.autonomy == AutonomyLevel.FULL_AUTO
    assert config.max_disclosure_tier == 1
