import pytest
from pathlib import Path
from envcraft import EnvCraft
from pydantic import Field


class StrictTestConfig(EnvCraft):
    known_var: str = "default"


def test_strict_mode_allows_known_vars(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("KNOWN_VAR", "value")
    config = StrictTestConfig.load(strict=True, cache=False, auto_generate_example=False)
    assert config.known_var == "value"


def test_strict_mode_rejects_unknown_vars(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    
    env_file = tmp_path / ".env"
    env_file.write_text("""
KNOWN_VAR=value
UNKNOWN_VAR=should_fail
""")
    
    with pytest.raises(Exception):  # Pydantic will raise validation error
        StrictTestConfig.load(strict=True, cache=False, auto_generate_example=False)


def test_generate_docs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    class DocTestConfig(EnvCraft):
        database_url: str = Field(..., description="Database connection string")
        debug: bool = False
    
    output = tmp_path / "CONFIG.md"
    DocTestConfig.generate_docs(str(output))
    
    assert output.exists()
    content = output.read_text()
    assert "# Configuration Documentation" in content
    assert "DATABASE_URL" in content
    assert "Database connection string" in content
    assert "DEBUG" in content
    assert "**Type:**" in content
    assert "**Required:**" in content
