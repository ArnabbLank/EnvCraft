import pytest
from pathlib import Path
from envcraft import EnvCraft, Secret
from pydantic import Field, ValidationError


class AppTestConfig(EnvCraft):
    test_var: str = "default"
    test_int: int = 42


def test_secret_masking():
    secret = Secret("sensitive_value")
    assert str(secret) == "***"
    assert repr(secret) == "Secret('***')"
    assert secret.get() == "sensitive_value"


def test_config_defaults():
    config = AppTestConfig()
    assert config.test_var == "default"
    assert config.test_int == 42


def test_generate_example(tmp_path):
    output = tmp_path / ".env.example"
    AppTestConfig.generate_example(str(output))
    assert output.exists()
    content = output.read_text()
    assert "TEST_VAR" in content
    assert "TEST_INT" in content
