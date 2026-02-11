import pytest
from pathlib import Path
from envcraft import EnvCraft
from envcraft.config import _instances, _reload_callbacks
from pydantic import Field
import time
import os


class InterpolationTestConfig(EnvCraft):
    user: str
    host: str
    database_url: str


def test_variable_interpolation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
USER=testuser
HOST=localhost
DATABASE_URL=postgresql://${USER}@${HOST}/mydb
""")
    
    config = InterpolationTestConfig.load(cache=False)
    assert config.user == "testuser"
    assert config.host == "localhost"
    assert config.database_url == "postgresql://testuser@localhost/mydb"


def test_interpolation_with_system_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SYSTEM_VAR", "from_system")
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
USER=testuser
HOST=${SYSTEM_VAR}
DATABASE_URL=postgresql://${USER}@from_system/mydb
""")
    
    config = InterpolationTestConfig.load(cache=False)
    assert config.host == "from_system"
    assert config.database_url == "postgresql://testuser@from_system/mydb"


class CacheTestConfig(EnvCraft):
    test_value: str = "default"


def test_caching(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Clear any cached instance
    if CacheTestConfig in _instances:
        del _instances[CacheTestConfig]
    
    config1 = CacheTestConfig.load()
    config2 = CacheTestConfig.load()
    
    assert config1 is config2


def test_reload(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Clear any cached instance
    if CacheTestConfig in _instances:
        del _instances[CacheTestConfig]
    
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_VALUE=initial")
    
    config1 = CacheTestConfig.load()
    assert config1.test_value == "initial"
    
    # Update file
    env_file.write_text("TEST_VALUE=updated")
    
    config2 = CacheTestConfig.reload()
    assert config2.test_value == "updated"


def test_reload_callbacks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Clear any cached instance
    if CacheTestConfig in _instances:
        del _instances[CacheTestConfig]
    if CacheTestConfig in _reload_callbacks:
        _reload_callbacks[CacheTestConfig] = []
    
    callback_called = []
    
    def on_reload(config):
        callback_called.append(config.test_value)
    
    CacheTestConfig.on_reload(on_reload)
    
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_VALUE=initial")
    
    CacheTestConfig.load()
    
    env_file.write_text("TEST_VALUE=reloaded")
    CacheTestConfig.reload()
    
    assert "reloaded" in callback_called


def test_no_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Clear any cached instance
    if CacheTestConfig in _instances:
        del _instances[CacheTestConfig]
    
    config1 = CacheTestConfig.load(cache=False)
    config2 = CacheTestConfig.load(cache=False)
    
    assert config1 is not config2


class SuggestionTestConfig(EnvCraft):
    database_url: str = Field(...)
    api_key: str = Field(...)


def test_smart_suggestions_missing_field(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Clear environment
    for key in list(os.environ.keys()):
        if key.startswith('DATABSE') or key.startswith('DATABASE') or key.startswith('API'):
            monkeypatch.delenv(key, raising=False)
    
    # Clear any cached instance
    if SuggestionTestConfig in _instances:
        del _instances[SuggestionTestConfig]
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
API_KEY=test123
""")
    
    with pytest.raises(Exception) as exc_info:
        SuggestionTestConfig.load(cache=False, auto_generate_example=False)
    
    # The error should mention the missing field
    assert "database_url" in str(exc_info.value).lower() or "DATABASE_URL" in str(exc_info.value)
