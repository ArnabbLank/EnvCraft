# EnvCraft

Enhanced environment configuration for Python with better error messages and multi-source loading.

> **The last config library you'll need** - From startup to enterprise in one package.

## Features

- 🔒 **Secret wrapper** - Prevents accidental logging of sensitive values
- 📝 **Better error messages** - Clear, actionable validation errors with smart suggestions
- 🔄 **Multi-file support** - Load from `.env`, `.env.{env}`, `.env.local`
- 📋 **Auto-generate templates** - Automatically creates `.env.example` on first load
- ✅ **Type validation** - Built on Pydantic for robust type checking
- 🌍 **Variable interpolation** - Use `${VAR}` syntax in .env files
- 📦 **Caching & reload** - Singleton pattern with thread-safe reload support

## Installation

```bash
pip install envcraft
```

**With secret backends:**
```bash
pip install envcraft[aws]    # AWS Secrets Manager
pip install envcraft[azure]  # Azure Key Vault  
pip install envcraft[vault]  # HashiCorp Vault
pip install envcraft[all]    # All backends
```

## Quick Start

```python
from envcraft import EnvCraft, Secret
from pydantic import Field

class AppConfig(EnvCraft):
    database_url: str = Field(..., description="PostgreSQL connection string")
    api_key: Secret[str] = Field(..., description="External API key")
    debug: bool = False
    max_workers: int = 4

# Load configuration - automatically generates .env.example if missing
config = AppConfig.load()

# Access values
print(config.debug)  # False
print(config.api_key)  # Secret('***')
print(config.api_key.get())  # Actual key value
```

## Why EnvCraft?

| Feature | python-dotenv | pydantic-settings | **EnvCraft** |
|---------|---------------|-------------------|---------------|
| Type validation | ❌ | ✅ | ✅ |
| Auto .env.example | ❌ | ❌ | ✅ |
| Smart error suggestions | ❌ | ❌ | ✅ |
| Variable interpolation | ❌ | ❌ | ✅ |
| Secret backends (AWS/Azure/Vault) | ❌ | ❌ | ✅ |
| Multi-file support | ⚠️ | ⚠️ | ✅ |
| CLI tool | ❌ | ❌ | ✅ |
| Documentation generator | ❌ | ❌ | ✅ |
| Reload support | ❌ | ❌ | ✅ |

## Auto-generated .env.example

When you call `load()` for the first time, EnvCraft automatically generates a `.env.example` file with:
- Field descriptions from your Pydantic schema
- Type information for each variable
- Default values for optional fields

**Generated `.env.example`:**
```bash
# PostgreSQL connection string
# Type: str
DATABASE_URL=

# External API key
# Type: Secret[str]
API_KEY=

# Type: bool
DEBUG=False

# Type: int
MAX_WORKERS=4
```

To disable auto-generation:
```python
config = AppConfig.load(auto_generate_example=False)
```

Or manually generate anytime:
```python
AppConfig.generate_example()
```

## Environment-specific configs

```python
# Loads .env, then .env.production, then .env.local
config = AppConfig.load(env='production')
```

## Debug Variable Sources

See which file supplied each variable - extremely useful for debugging deployments:

```python
config = AppConfig.load(show_sources=True)
```

**Output:**
```
📋 Environment Variable Sources:

  DATABASE_URL = postgresql://user:pass@localhost/db
    └─ loaded from .env.production
  API_KEY = ***
    └─ loaded from .env
  DEBUG = True
    └─ loaded from .env.local
  MAX_WORKERS = 4
    └─ loaded from default value
```

**Precedence order:** `.env` → `.env.{env}` → `.env.local` (later files override earlier ones)

## Config Validation

Check configuration status without loading - perfect for CI/CD and onboarding:

```python
AppConfig.diagnose()
```

**Output:**
```
🔍 Configuration Diagnosis:

  ✓ DATABASE_URL present
  ✓ API_KEY present
  ✓ DEBUG using default (False)
  ✗ REDIS_URL missing (required)
  ⚠ CACHE_TTL not set (optional)

❌ Some required variables are missing
```

Returns `True` if all required variables are present, `False` otherwise. Great for:
- CI/CD pipeline checks
- Developer onboarding
- Deployment validation
- Quick environment audits

## CLI Tool

EnvCraft includes a command-line tool for quick validation and documentation:

```bash
# Check if all required variables are present
envcraft check

# Generate .env.example file
envcraft generate

# Generate configuration documentation
envcraft docs

# Explain a specific variable
envcraft explain DATABASE_URL
```

**Example output:**
```bash
$ envcraft explain DATABASE_URL

📝 DATABASE_URL

  Description: PostgreSQL connection string
  Type: str
  Required: Yes
```

The CLI automatically finds your config class in common locations:
- `config.AppConfig`
- `app.config.AppConfig`
- `settings.Settings`
- `config.Config`

Perfect for:
- CI/CD validation: `envcraft check || exit 1`
- Pre-commit hooks
- Developer onboarding
- Quick reference

## Nested Config Support

Organize complex configurations with nested models:

```python
from pydantic import BaseModel

class DBConfig(BaseModel):
    url: str
    pool_size: int = 10

class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379

class AppConfig(EnvCraft):
    db: DBConfig
    redis: RedisConfig
    debug: bool = False
```

**Environment variables use double underscore (`__`) for nesting:**
```bash
DB__URL=postgresql://localhost/mydb
DB__POOL_SIZE=20
REDIS__HOST=redis.example.com
REDIS__PORT=6380
DEBUG=true
```

**Generated `.env.example`:**
```bash
# DB (nested)

# Type: str
DB__URL=

# Type: int
DB__POOL_SIZE=10

# REDIS (nested)

# Type: str
REDIS__HOST=localhost

# Type: int
REDIS__PORT=6379
```

## Strict Mode

Prevent configuration drift by failing on unknown environment variables:

```python
# Fails if any unexpected variables are present
config = AppConfig.load(strict=True)
```

This catches typos and ensures your environment matches your schema exactly. Very useful in production deployments.

## Documentation Generator

Auto-generate Markdown documentation for your configuration:

```python
AppConfig.generate_docs()  # Creates CONFIG.md
```

**Generated output:**
```markdown
# Configuration Documentation

## DATABASE_URL

PostgreSQL connection string

- **Type:** `str`
- **Required:** Yes

**Example:**
\`\`\`bash
DATABASE_URL=<value>
\`\`\`

## DEBUG

- **Type:** `bool`
- **Required:** No
- **Default:** `False`
```

Perfect for onboarding documentation and team wikis.

## Secret Backend Plugins

Load secrets from external secret managers instead of environment variables:

```python
from envcraft import EnvCraft, Secret

class AppConfig(EnvCraft):
    # Load from AWS Secrets Manager
    api_key: Secret[str] = Secret.from_aws("prod/api_key", region="us-east-1")
    
    # Load from Azure Key Vault
    db_password: Secret[str] = Secret.from_azure("db-password", vault_url="https://myvault.vault.azure.net/")
    
    # Load from HashiCorp Vault
    jwt_secret: Secret[str] = Secret.from_vault("jwt-secret", url="https://vault.example.com")

config = AppConfig.load()
print(config.api_key.get())  # Fetches from AWS on first access
```

**Supported backends:**
- AWS Secrets Manager (requires `boto3`)
- Azure Key Vault (requires `azure-keyvault-secrets`)
- HashiCorp Vault (requires `hvac`)
- Environment variables (default)

**Custom backends:**
```python
from envcraft import SecretBackend, register_backend

class CustomBackend(SecretBackend):
    def get_secret(self, key: str) -> str:
        # Your custom logic
        return fetch_from_somewhere(key)

register_backend('custom', CustomBackend())
config.secret = Secret.from_backend('my-key', backend='custom')
```

## Variable Interpolation

Use `${VAR}` syntax to reference other variables in your .env files:

```bash
# .env
USER=myuser
HOST=localhost
DATABASE_URL=postgresql://${USER}@${HOST}/mydb
API_BASE=https://${HOST}/api
```

Variables are expanded automatically when the config is loaded. You can reference:
- Other variables in the same file
- Variables from earlier files in the load order
- System environment variables

## Caching & Reload Support

EnvCraft uses a singleton pattern by default for efficient config access:

```python
# First call loads and caches
config1 = AppConfig.load()

# Subsequent calls return cached instance
config2 = AppConfig.load()
assert config1 is config2

# Reload configuration (e.g., after file changes)
config = AppConfig.reload()

# Register callbacks for reload events
def on_config_reload(new_config):
    print(f"Config reloaded! Debug mode: {new_config.debug}")

AppConfig.on_reload(on_config_reload)
```

**Thread-safe:** All reload operations use locks to ensure safety in multi-threaded applications like FastAPI.

To disable caching:
```python
config = AppConfig.load(cache=False)
```

## Smart Error Suggestions

When you make a typo, EnvCraft suggests the correct variable name:

```
❌ Environment Configuration Error:

  • databse_url: Field required
    → Set DATABSE_URL in your .env file or environment
    💡 Did you mean: DATABASE_URL?
```

Works for:
- Missing required variables
- Unknown variables in strict mode
- Nested configuration fields

## Framework Integrations

EnvCraft works seamlessly with popular frameworks:

- **[FastAPI](docs/INTEGRATIONS.md#fastapi)** - Dependency injection, lifespan events, hot reload
- **[Django](docs/INTEGRATIONS.md#django)** - Settings integration, nested configs
- **[Flask](docs/INTEGRATIONS.md#flask)** - App configuration
- **[Celery](docs/INTEGRATIONS.md#celery)** - Task queue configuration
- **[Docker/Kubernetes](docs/INTEGRATIONS.md#docker)** - Container deployments
- **[AWS Lambda](docs/INTEGRATIONS.md#aws-lambda)** - Serverless functions

See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) for complete examples.

## Migration Guides

Switching from another config library? We've got you covered:

- **[From python-dotenv](docs/MIGRATION.md#migrating-from-python-dotenv)** - Simple upgrade path
- **[From pydantic-settings](docs/MIGRATION.md#migrating-from-pydantic-settings)** - Drop-in replacement
- **[From django-environ](docs/MIGRATION.md#migrating-from-django-environ)** - Django-specific guide
- **[From decouple](docs/MIGRATION.md#migrating-from-decouple)** - Quick migration

See [docs/MIGRATION.md](docs/MIGRATION.md) for detailed migration guides.

## Getting Started

- **New to EnvCraft?** See [docs/QUICKSTART.md](docs/QUICKSTART.md) for persona-based guides
- **Migrating?** Check [docs/MIGRATION.md](docs/MIGRATION.md) for your current library
- **Using a framework?** See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) for examples
- **Want all features?** Read [docs/FEATURES.md](docs/FEATURES.md) for complete list

## License

MIT
