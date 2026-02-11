import pytest
from envcraft import Secret
from envcraft.backends import EnvBackend, SecretBackend, register_backend
import os


def test_secret_lazy_loading():
    """Test that secrets are loaded lazily"""
    secret = Secret.from_backend("TEST_KEY", backend="env")
    
    # Value should not be loaded yet
    assert secret._value is None
    
    # Set env var and get value
    os.environ["TEST_KEY"] = "secret_value"
    assert secret.get() == "secret_value"
    
    # Value should now be cached
    assert secret._value == "secret_value"


def test_custom_backend():
    """Test custom backend registration"""
    
    class MockBackend(SecretBackend):
        def get_secret(self, key: str) -> str:
            return f"mock_{key}"
    
    register_backend("mock", MockBackend())
    secret = Secret.from_backend("test", backend="mock")
    
    assert secret.get() == "mock_test"


def test_secret_masking():
    """Test that secrets are masked in output"""
    secret = Secret("sensitive_data")
    
    assert str(secret) == "***"
    assert repr(secret) == "Secret('***')"
    assert secret.get() == "sensitive_data"


def test_env_backend():
    """Test environment variable backend"""
    backend = EnvBackend()
    os.environ["TEST_SECRET"] = "test_value"
    
    assert backend.get_secret("TEST_SECRET") == "test_value"
    
    with pytest.raises(ValueError):
        backend.get_secret("NONEXISTENT_KEY")
