import pytest
from pydantic import BaseModel
from envcraft import EnvCraft
import os


class DBConfig(BaseModel):
    url: str
    pool_size: int = 10


class NestedTestConfig(EnvCraft):
    db: DBConfig
    debug: bool = False


def test_nested_config_from_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    
    # Clear environment
    for key in list(os.environ.keys()):
        if key.startswith('DB__') or key == 'DEBUG':
            monkeypatch.delenv(key, raising=False)
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
DB__URL=postgresql://localhost/test
DB__POOL_SIZE=20
DEBUG=false
""")
    
    config = NestedTestConfig.load(cache=False, auto_generate_example=False)
    assert config.db.url == "postgresql://localhost/test"
    assert config.db.pool_size == 20
    assert config.debug is False


def test_nested_config_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    
    # Clear environment
    for key in list(os.environ.keys()):
        if key.startswith('DB__') or key == 'DEBUG':
            monkeypatch.delenv(key, raising=False)
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
DB__URL=postgresql://localhost/test
""")
    
    config = NestedTestConfig.load(cache=False, auto_generate_example=False)
    assert config.db.url == "postgresql://localhost/test"
    assert config.db.pool_size == 10  # default


def test_nested_generate_example(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = tmp_path / ".env.example"
    
    NestedTestConfig.generate_example(str(output))
    content = output.read_text()
    
    assert "DB__URL" in content
    assert "DB__POOL_SIZE" in content
    assert "DEBUG" in content
    assert "(nested)" in content
