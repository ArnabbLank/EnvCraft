# EnvCraft - Complete Feature List

## ✅ All Features Implemented

### Core Features (MVP)
- [x] Secret wrapper with masking
- [x] Better error messages
- [x] Multi-file support (.env, .env.{env}, .env.local)
- [x] Auto-generate .env.example
- [x] Type validation via Pydantic

### Developer Experience (DX)
- [x] **Variable interpolation** - `${VAR}` syntax in .env files
- [x] **Smart suggestions** - Fuzzy matching for typos ("Did you mean X?")
- [x] **Caching** - Singleton pattern for efficiency
- [x] **Reload support** - `reload()` method for long-running apps
- [x] **Thread-safe hooks** - Callbacks for reload events
- [x] Environment precedence visualization
- [x] Config validation/diagnosis

### Enterprise Features
- [x] **Secret backend plugins**
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - Custom backends
- [x] **Strict mode** - Fail on unknown variables
- [x] **Documentation generator** - Auto-generate CONFIG.md
- [x] Nested configuration support

### CLI Tool
- [x] `envcraft check` - Validate configuration
- [x] `envcraft generate` - Generate .env.example
- [x] `envcraft docs` - Generate documentation
- [x] `envcraft explain <VAR>` - Explain variable

## Feature Comparison

| Feature | python-dotenv | pydantic-settings | **EnvCraft** |
|---------|---------------|-------------------|---------------|
| Load .env files | ✅ | ✅ | ✅ |
| Type validation | ❌ | ✅ | ✅ |
| Multi-file support | ❌ | ⚠️ | ✅ |
| Auto .env.example | ❌ | ❌ | ✅ |
| Variable interpolation | ❌ | ❌ | ✅ |
| Smart error suggestions | ❌ | ❌ | ✅ |
| Secret backends | ❌ | ❌ | ✅ |
| Documentation generator | ❌ | ❌ | ✅ |
| CLI tool | ❌ | ❌ | ✅ |
| Reload support | ❌ | ❌ | ✅ |
| Strict mode | ❌ | ⚠️ | ✅ |
| Nested configs | ❌ | ✅ | ✅ |

## Quick Start

```python
from envcraft import EnvCraft, Secret
from pydantic import Field

class AppConfig(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    api_key: Secret[str] = Secret.from_aws("prod/api_key")
    debug: bool = False

# Load with all features
config = AppConfig.load(
    env='production',        # Load .env.production
    show_sources=True,       # Show where vars came from
    strict=True,             # Fail on unknown vars
)

# Access values
print(config.debug)
print(config.api_key.get())  # Fetches from AWS

# Reload on file change
AppConfig.on_reload(lambda cfg: print("Reloaded!"))
config = AppConfig.reload()
```

## Installation

```bash
# Basic
pip install envcraft

# With secret backends
pip install envcraft[aws]      # AWS Secrets Manager
pip install envcraft[azure]    # Azure Key Vault
pip install envcraft[vault]    # HashiCorp Vault
pip install envcraft[all]      # All backends
```

## Why EnvCraft?

**For Startups:**
- Get started in 5 minutes
- Auto-generates documentation
- Helpful error messages save debugging time

**For Scale-ups:**
- Multi-environment support
- Variable interpolation
- Reload without restart

**For Enterprise:**
- Secret manager integration
- Strict validation
- Thread-safe operations
- Audit trail with source tracking

## Real-World Use Cases

### 1. FastAPI Application
```python
from fastapi import FastAPI
from envcraft import EnvCraft

class Config(EnvCraft):
    database_url: str
    redis_url: str
    debug: bool = False

config = Config.load()
app = FastAPI(debug=config.debug)

# Reload config without restart
@app.post("/admin/reload-config")
async def reload():
    Config.reload()
    return {"status": "reloaded"}
```

### 2. CI/CD Validation
```bash
# In your CI pipeline
envcraft check || exit 1
```

### 3. Developer Onboarding
```bash
# New developer joins
git clone repo
envcraft generate  # Creates .env.example
envcraft docs      # Creates CONFIG.md
envcraft check     # Validates their setup
```

### 4. Production Deployment
```python
# Load from AWS Secrets Manager
class ProdConfig(EnvCraft):
    db_password: Secret[str] = Secret.from_aws("prod/db", region="us-east-1")
    api_key: Secret[str] = Secret.from_aws("prod/api", region="us-east-1")

config = ProdConfig.load(strict=True)  # Fail on any issues
```

## Roadmap (Future Ideas)

- [ ] Watch mode - Auto-reload on file changes
- [ ] Config validation schemas (JSON Schema export)
- [ ] Environment variable encryption at rest
- [ ] Integration with popular frameworks (Django, Flask)
- [ ] Config versioning and rollback
- [ ] Remote config sources (S3, HTTP)
- [ ] Config diff tool
- [ ] Performance metrics and monitoring

## Contributing

This package is feature-complete for v1.0. Contributions welcome!

## Documentation

- **[README.md](README.md)** - Quick start and feature overview
- **[INTEGRATIONS.md](INTEGRATIONS.md)** - Framework integration examples
  - FastAPI, Django, Flask, Celery
  - Docker, Kubernetes, AWS Lambda
  - Pytest, Streamlit
- **[MIGRATION.md](MIGRATION.md)** - Migration guides from other libraries
  - python-dotenv
  - pydantic-settings
  - django-environ
  - decouple
- **[FEATURES.md](FEATURES.md)** - Complete feature list and comparison
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical implementation details

## License

MIT
