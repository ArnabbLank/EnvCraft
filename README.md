# envcraft

> **Stop debugging missing env vars.** Type-safe configuration with fuzzy error suggestions, auto-generated `.env.example`, and multi-file cascading — in one class.

[![PyPI](https://img.shields.io/pypi/v/envcraft)](https://pypi.org/project/envcraft/)
[![Downloads](https://static.pepy.tech/badge/envcraft)](https://pepy.tech/project/envcraft)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/envcraft/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Problem

```
$ python app.py
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
DATABSE_URL
  Field required [type=missing, input_value={}, input_type=dict]
```

You stare at the error. Was it `DATABASE_URL`? `DB_URL`? Which `.env` file is active? Did `.env.local` override it? Is the value even the right type?

**With envcraft:**

```
❌ Environment Configuration Error:

  • database_url: Field required
    → Set DATABASE_URL in your .env file or environment
    💡 Did you mean: DATABASE_URL?
```

Plus: your `.env.example` is auto-generated, your secrets never leak into logs, and environment-specific overrides just work.

---

## Install

```bash
pip install envcraft
```

---

## Quick Start

```python
from envcraft import EnvCraft
from pydantic import Field

class Config(EnvCraft):
    database_url: str = Field(..., description="PostgreSQL connection string")
    api_key: str = Field(..., description="External API key")
    debug: bool = False
    max_workers: int = 4

config = Config.load()
# ✅ Type-validated, cached, thread-safe, with helpful errors if anything's wrong
```

Create a `.env`:

```bash
DATABASE_URL=postgresql://localhost/mydb
API_KEY=sk-secret-key
DEBUG=true
MAX_WORKERS=8
```

That's it. EnvCraft handles type coercion, multi-file loading, variable interpolation, and auto-generates `.env.example` from your schema.

---

## Why envcraft?

| Feature | python-dotenv | pydantic-settings | **envcraft** |
|---------|:---:|:---:|:---:|
| Type validation | ❌ | ✅ | ✅ |
| Fuzzy error suggestions | ❌ | ❌ | ✅ |
| Auto `.env.example` generation | ❌ | ❌ | ✅ |
| Multi-file cascade | ❌ | ⚠️ | ✅ |
| Variable interpolation (`${VAR}`) | ❌ | ❌ | ✅ |
| Secret masking in logs | ❌ | ❌ | ✅ |
| Hot reload with callbacks | ❌ | ❌ | ✅ |
| CLI tools | ❌ | ❌ | ✅ |
| Secret backends (AWS/Azure/Vault) | ❌ | ⚠️ | ✅ |
| Strict mode (catch drift) | ❌ | ❌ | ✅ |
| Nested config groups | ❌ | ✅ | ✅ |

---

## Features

### Multi-File Cascade

Load order: `.env` → `.env.{environment}` → `.env.local`

```python
config = Config.load(env="production")
# Loads: .env → .env.production → .env.local (each overrides the previous)
```

### Variable Interpolation

```bash
# .env
BASE_URL=https://api.example.com
AUTH_URL=${BASE_URL}/auth
CALLBACK_URL=${BASE_URL}/callback
```

### Secret Masking

```python
from envcraft import EnvCraft, Secret

class Config(EnvCraft):
    api_key: Secret[str]
    database_url: str

config = Config.load()
print(config.api_key)        # Secret('***')
print(config.api_key.get())  # actual value (use intentionally)
```

Secrets never accidentally appear in logs, repr, or serialized output.

### Secret Backends

```python
from envcraft import Secret

class Config(EnvCraft):
    # Load from AWS Secrets Manager
    db_password: Secret[str] = Secret.from_aws("prod/db-password", region="us-east-1")

    # Load from Azure Key Vault
    api_key: Secret[str] = Secret.from_azure("api-key", vault_url="https://myvault.vault.azure.net")

    # Load from HashiCorp Vault
    token: Secret[str] = Secret.from_vault("app/token", url="https://vault.example.com")
```

Install backend extras:

```bash
pip install envcraft[aws]      # AWS Secrets Manager
pip install envcraft[azure]    # Azure Key Vault
pip install envcraft[vault]    # HashiCorp Vault
pip install envcraft[all]      # All backends
```

### Thread-Safe Caching & Hot Reload

```python
# Singleton — same instance across your app
config = Config.load()  # loads once, cached thereafter

# Hot reload when env files change
config = Config.reload()

# Register callbacks on reload
@Config.on_reload
def handle_reload(new_config):
    print(f"Config reloaded! Debug is now: {new_config.debug}")
```

### Strict Mode

Catch config drift — fail if `.env` contains variables not in your schema:

```python
config = Config.load(strict=True)
# Raises ValueError if .env has unknown variables
```

### Nested Configs

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"

class Config(EnvCraft):
    database: DatabaseConfig = DatabaseConfig()
    debug: bool = False
```

```bash
# .env
DATABASE__HOST=prod-db.example.com
DATABASE__PORT=5432
DATABASE__NAME=production
```

### Source Tracing

See which file provided each variable:

```python
config = Config.load(show_sources=True)
```

```
📋 Environment Variable Sources:

  DATABASE_URL = postgresql://localhost/mydb
    └─ loaded from .env.local
  API_KEY = ***
    └─ loaded from .env
  DEBUG = True
    └─ loaded from .env.production
```

---

## CLI

```bash
envcraft check      # Validate all config vars — shows ✓/✗ per variable
envcraft generate   # Auto-generate .env.example from your schema
envcraft docs       # Generate CONFIG.md documentation
envcraft explain DATABASE_URL   # Explain a specific variable
```

**`envcraft check` output:**

```
🔍 Configuration Diagnosis:

  ✓ DATABASE_URL present
  ✓ API_KEY present
  ✓ DEBUG using default (False)
  ✗ REDIS_URL missing (required)

❌ Some required variables are missing
```

---

## API Reference

### `Config.load()`

```python
Config.load(
    env: str = None,              # Environment name (loads .env.{env})
    auto_generate_example: bool = True,  # Auto-create .env.example
    show_sources: bool = False,   # Print which file supplied each var
    strict: bool = False,         # Fail on unknown variables
    cache: bool = True,           # Cache instance (thread-safe singleton)
)
```

### `Config.reload()`

Force-reload from disk. Triggers registered callbacks.

### `Config.diagnose()`

Print status of all variables without loading (useful for CI).

### `Config.generate_example(output=".env.example")`

Generate `.env.example` from schema with types and descriptions.

### `Config.generate_docs(output="CONFIG.md")`

Generate Markdown documentation of all config variables.

---

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI, Depends
from envcraft import EnvCraft
from pydantic import Field

class Settings(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    secret_key: str = Field(..., description="JWT signing key")
    debug: bool = False

def get_settings() -> Settings:
    return Settings.load()

app = FastAPI()

@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

### Django

```python
# settings.py
from envcraft import EnvCraft

class DjangoEnv(EnvCraft):
    secret_key: str
    database_url: str
    debug: bool = False
    allowed_hosts: str = "localhost"

env = DjangoEnv.load()
SECRET_KEY = env.secret_key
DEBUG = env.debug
```

---

## Requirements

- Python 3.8+
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0

---

## Development

```bash
git clone https://github.com/ArnabbLank/EnvCraft.git
cd EnvCraft
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Contributing

Contributions welcome:

- 🐛 Report bugs
- ✨ Suggest features
- 🧪 Add tests
- 📖 Improve docs

---

## License

MIT © 2026 [Arnab Sen](https://github.com/ArnabbLank)

---

**Source:** https://github.com/ArnabbLank/EnvCraft
