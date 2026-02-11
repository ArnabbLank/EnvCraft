# Quick Start Guide

Choose your path based on your needs:

## 🚀 I'm Starting a New Project

```bash
# Install
pip install envcraft

# Create your config
cat > config.py << 'EOF'
from envcraft import EnvCraft, Secret
from pydantic import Field

class Config(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    api_key: Secret[str] = Field(..., description="API key")
    debug: bool = False

config = Config.load()
EOF

# Generate .env.example
python -c "from config import Config; Config.generate_example()"

# Generate documentation
python -c "from config import Config; Config.generate_docs()"

# Check your setup
envcraft check
```

**Next steps:**
- Copy `.env.example` to `.env` and fill in values
- Import `config` in your app: `from config import config`
- Read [INTEGRATIONS.md](INTEGRATIONS.md) for your framework

---

## 🔄 I'm Migrating from python-dotenv

```bash
# Install alongside existing code
pip install envcraft
```

**Before:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
API_KEY = os.getenv('API_KEY')
```

**After:**
```python
from envcraft import EnvCraft, Secret

class Config(EnvCraft):
    database_url: str
    debug: bool = False
    api_key: Secret[str]

config = Config.load()
```

**Benefits:**
- ✅ No more manual type conversion
- ✅ Automatic validation
- ✅ Better error messages
- ✅ Secret masking

See [MIGRATION.md](MIGRATION.md#migrating-from-python-dotenv) for complete guide.

---

## 🏢 I'm Using pydantic-settings

Great news! EnvCraft is built on pydantic-settings, so migration is trivial:

```python
# Change this:
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    ...

# To this:
from envcraft import EnvCraft
class Settings(EnvCraft):
    ...

# Change this:
settings = Settings()

# To this:
settings = Settings.load()
```

**What you gain:**
- ✅ Auto .env.example generation
- ✅ Smart error suggestions
- ✅ Multi-file support
- ✅ CLI tool
- ✅ Documentation generator
- ✅ Variable interpolation

See [MIGRATION.md](MIGRATION.md#migrating-from-pydantic-settings) for details.

---

## 🐳 I'm Deploying with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Validate config before starting
RUN envcraft check

CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
services:
  app:
    build: .
    env_file:
      - .env
      - .env.production
    environment:
      - DATABASE_URL=postgresql://user:pass@db/myapp
```

See [INTEGRATIONS.md](INTEGRATIONS.md#docker) for complete example.

---

## ☁️ I'm Using AWS/Azure/Vault

```python
from envcraft import EnvCraft, Secret

class Config(EnvCraft):
    # Load from AWS Secrets Manager
    db_password: Secret[str] = Secret.from_aws(
        "prod/db_password",
        region="us-east-1"
    )
    
    # Load from Azure Key Vault
    api_key: Secret[str] = Secret.from_azure(
        "api-key",
        vault_url="https://myvault.vault.azure.net/"
    )
    
    # Load from HashiCorp Vault
    jwt_secret: Secret[str] = Secret.from_vault(
        "jwt-secret",
        url="https://vault.example.com"
    )

config = Config.load()
```

**Install backend dependencies:**
```bash
pip install envcraft[aws]    # For AWS
pip install envcraft[azure]  # For Azure
pip install envcraft[vault]  # For Vault
pip install envcraft[all]    # For all backends
```

---

## 🚄 I'm Using FastAPI

```python
from fastapi import FastAPI
from envcraft import EnvCraft, Secret

class Settings(EnvCraft):
    app_name: str = "My API"
    database_url: str
    secret_key: Secret[str]
    debug: bool = False

settings = Settings.load()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

@app.get("/")
async def root():
    return {"app": settings.app_name}

# Hot reload endpoint
@app.post("/admin/reload")
async def reload():
    Settings.reload()
    return {"status": "reloaded"}
```

See [INTEGRATIONS.md](INTEGRATIONS.md#fastapi) for complete example.

---

## 🎯 I'm Using Django

```python
# config.py
from envcraft import EnvCraft, Secret

class DjangoConfig(EnvCraft):
    secret_key: Secret[str]
    debug: bool = False
    database_url: str
    allowed_hosts: str = "localhost"

config = DjangoConfig.load()

# settings.py
from .config import config

SECRET_KEY = config.secret_key.get()
DEBUG = config.debug
ALLOWED_HOSTS = config.allowed_hosts.split(',')

# Use dj-database-url for database
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(config.database_url)
}
```

See [INTEGRATIONS.md](INTEGRATIONS.md#django) for complete example.

---

## 🧪 I'm Setting Up CI/CD

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Validate configuration
        run: |
          envcraft check || exit 1
      
      - name: Run tests
        run: pytest
```

**Pre-commit hook:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
envcraft check || exit 1
```

---

## 👥 I'm Onboarding New Developers

```bash
# 1. Clone repo
git clone <repo>
cd <repo>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Check what config is needed
envcraft check

# 4. Copy example and fill in values
cp .env.example .env
# Edit .env with your values

# 5. Validate your setup
envcraft check

# 6. Read the docs
envcraft docs  # Generates CONFIG.md
cat CONFIG.md
```

**Add to your README:**
```markdown
## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in values
3. Validate: `envcraft check`
4. Run: `python main.py`
```

---

## 🔍 I'm Debugging Configuration Issues

```python
# Show where each variable came from
config = Config.load(show_sources=True)
```

**Output:**
```
📋 Environment Variable Sources:

  DATABASE_URL = postgresql://localhost/db
    └─ loaded from .env.production
  API_KEY = ***
    └─ loaded from .env
  DEBUG = True
    └─ loaded from .env.local
```

**Check configuration status:**
```bash
envcraft check
```

**Explain a specific variable:**
```bash
envcraft explain DATABASE_URL
```

---

## 📚 I Want to Learn All Features

1. **Read the README** - [README.md](README.md)
2. **Check the comparison** - [FEATURES.md](FEATURES.md)
3. **See framework examples** - [INTEGRATIONS.md](INTEGRATIONS.md)
4. **Run the example** - `python example.py`
5. **Try the CLI** - `envcraft --help`

---

## 🆘 I Need Help

- **Documentation**: Check [README.md](README.md), [FEATURES.md](FEATURES.md), [INTEGRATIONS.md](INTEGRATIONS.md)
- **Migration**: See [MIGRATION.md](MIGRATION.md)
- **CLI Help**: Run `envcraft --help`
- **Issues**: Open an issue on GitHub
- **Examples**: See `example.py` in the repo

---

## Common Commands

```bash
# Validate configuration
envcraft check

# Generate .env.example
envcraft generate

# Generate documentation
envcraft docs

# Explain a variable
envcraft explain DATABASE_URL

# Get help
envcraft --help
```

---

## Pro Tips

1. **Use strict mode in production**
   ```python
   config = Config.load(strict=True)
   ```

2. **Track variable sources during debugging**
   ```python
   config = Config.load(show_sources=True)
   ```

3. **Generate docs for your team**
   ```bash
   envcraft docs
   git add CONFIG.md
   ```

4. **Validate in CI/CD**
   ```bash
   envcraft check || exit 1
   ```

5. **Use environment-specific files**
   ```python
   config = Config.load(env='production')
   ```
