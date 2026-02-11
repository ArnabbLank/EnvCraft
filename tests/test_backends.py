import pytest
from envcraft import Secret, EnvCraft
from envcraft.backends import EnvBackend, SecretBackend, register_backend, get_backend
from pydantic import Field
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
    
    # Cleanup
    del os.environ["TEST_KEY"]


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
    
    # Cleanup
    del os.environ["TEST_SECRET"]


def test_secret_in_config(tmp_path, monkeypatch):
    """Test Secret fields in EnvCraft config"""
    monkeypatch.chdir(tmp_path)
    
    # Clear environment
    for key in list(os.environ.keys()):
        if key.startswith('API_') or key.startswith('DB_'):
            monkeypatch.delenv(key, raising=False)
    
    class SecretConfig(EnvCraft):
        api_key: str = Field(..., description="API key")
        db_password: str = Field(..., description="Database password")
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
API_KEY=secret123
DB_PASSWORD=pass456
""")
    
    config = SecretConfig.load(cache=False, auto_generate_example=False)
    
    assert config.api_key == "secret123"
    assert config.db_password == "pass456"


def test_secret_with_default():
    """Test Secret with default value"""
    secret = Secret("default_value")
    assert secret.get() == "default_value"
    assert str(secret) == "***"


def test_secret_caching():
    """Test that secret values are cached after first access"""
    os.environ["CACHE_TEST"] = "cached_value"
    
    secret = Secret.from_backend("CACHE_TEST", backend="env")
    
    # First access
    value1 = secret.get()
    assert value1 == "cached_value"
    
    # Change env var
    os.environ["CACHE_TEST"] = "new_value"
    
    # Should still return cached value
    value2 = secret.get()
    assert value2 == "cached_value"
    
    # Cleanup
    del os.environ["CACHE_TEST"]


def test_backend_registration():
    """Test backend registration and retrieval"""
    
    class TestBackend(SecretBackend):
        def get_secret(self, key: str) -> str:
            return f"test_{key}"
    
    backend = TestBackend()
    register_backend("test_backend", backend)
    
    retrieved = get_backend("test_backend")
    assert retrieved is backend
    assert retrieved.get_secret("foo") == "test_foo"


def test_backend_not_found():
    """Test error when backend not found"""
    with pytest.raises(ValueError, match="not registered"):
        get_backend("nonexistent_unique_backend_name_12345")


def test_multiple_secrets_in_config(tmp_path, monkeypatch):
    """Test multiple secret fields in one config"""
    monkeypatch.chdir(tmp_path)
    
    # Clear environment
    for key in list(os.environ.keys()):
        if key in ['SECRET1', 'SECRET2', 'SECRET3']:
            monkeypatch.delenv(key, raising=False)
    
    class MultiSecretConfig(EnvCraft):
        secret1: str
        secret2: str
        secret3: str
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
SECRET1=value1
SECRET2=value2
SECRET3=value3
""")
    
    config = MultiSecretConfig.load(cache=False, auto_generate_example=False)
    
    assert config.secret1 == "value1"
    assert config.secret2 == "value2"
    assert config.secret3 == "value3"
