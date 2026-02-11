# Migration Guides

Switching to EnvCraft is easy. Here's how to migrate from popular alternatives.

## Migrating from python-dotenv

### Before (python-dotenv)

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
API_KEY = os.getenv('API_KEY')

# No validation - runtime errors if missing
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required")
```

### After (EnvCraft)

```python
# config.py
from envcraft import EnvCraft, Secret
from pydantic import Field

class Config(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    debug: bool = False
    max_workers: int = 4
    api_key: Secret[str] = Field(..., description="API key")

# Automatic validation, type conversion, and helpful errors
config = Config.load()
```

### Migration Steps

1. **Install EnvCraft**
   ```bash
   pip install envcraft
   ```

2. **Create config class** (replace scattered `os.getenv()` calls)
   ```python
   from envcraft import EnvCraft
   
   class Config(EnvCraft):
       # Add all your environment variables here
       pass
   ```

3. **Replace `os.getenv()` with config attributes**
   ```python
   # Before
   db_url = os.getenv('DATABASE_URL')
   
   # After
   db_url = config.database_url
   ```

4. **Remove manual type conversions**
   ```python
   # Before
   max_workers = int(os.getenv('MAX_WORKERS', '4'))
   debug = os.getenv('DEBUG', 'false').lower() == 'true'
   
   # After - automatic type conversion
   max_workers = config.max_workers  # Already an int
   debug = config.debug  # Already a bool
   ```

5. **Wrap secrets**
   ```python
   # Before
   api_key = os.getenv('API_KEY')
   
   # After
   api_key: Secret[str]
   # Access with: config.api_key.get()
   ```

### Benefits You Get

- ✅ Automatic type validation
- ✅ Better error messages
- ✅ Auto-generated .env.example
- ✅ No manual type conversions
- ✅ Secret masking
- ✅ Multi-file support

---

## Migrating from pydantic-settings

### Before (pydantic-settings)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    max_workers: int = 4
    
    class Config:
        env_file = '.env'

settings = Settings()
```

### After (EnvCraft)

```python
from envcraft import EnvCraft, Secret
from pydantic import Field

class Settings(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    debug: bool = False
    max_workers: int = 4

settings = Settings.load()
```

### Migration Steps

1. **Install EnvCraft**
   ```bash
   pip install envcraft
   ```

2. **Replace `BaseSettings` with `EnvCraft`**
   ```python
   # Before
   from pydantic_settings import BaseSettings
   class Settings(BaseSettings):
   
   # After
   from envcraft import EnvCraft
   class Settings(EnvCraft):
   ```

3. **Remove `Config` inner class** (not needed)
   ```python
   # Before
   class Settings(BaseSettings):
       database_url: str
       
       class Config:
           env_file = '.env'
   
   # After
   class Settings(EnvCraft):
       database_url: str
       # Config is automatic
   ```

4. **Replace instantiation with `load()`**
   ```python
   # Before
   settings = Settings()
   
   # After
   settings = Settings.load()
   ```

5. **Add descriptions for better docs**
   ```python
   from pydantic import Field
   
   database_url: str = Field(..., description="PostgreSQL connection")
   ```

6. **Wrap sensitive values**
   ```python
   # Before
   api_key: str
   
   # After
   api_key: Secret[str]
   # Access with: settings.api_key.get()
   ```

### What You Gain

- ✅ Auto-generated .env.example
- ✅ Better error messages with suggestions
- ✅ Multi-file support (.env, .env.production, .env.local)
- ✅ Secret masking
- ✅ Variable interpolation
- ✅ CLI tool (envcraft check, generate, docs)
- ✅ Source tracking (show_sources=True)
- ✅ Config diagnosis
- ✅ Documentation generator
- ✅ Reload support

### Nested Configs (No Change Needed!)

EnvCraft is fully compatible with pydantic-settings nested configs:

```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int = 5432

class Settings(EnvCraft):
    database: DatabaseConfig

# Use same environment variables
# DATABASE__HOST=localhost
# DATABASE__PORT=5432
```

---

## Migrating from django-environ

### Before (django-environ)

```python
# settings.py
import environ

env = environ.Env(
    DEBUG=(bool, False),
    MAX_WORKERS=(int, 4),
)

environ.Env.read_env()

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
DATABASE_URL = env('DATABASE_URL')
MAX_WORKERS = env('MAX_WORKERS')
```

### After (EnvCraft)

```python
# config.py
from envcraft import EnvCraft, Secret
from pydantic import Field

class DjangoConfig(EnvCraft):
    debug: bool = False
    secret_key: Secret[str]
    database_url: str
    max_workers: int = 4

config = DjangoConfig.load()

# settings.py
from .config import config

DEBUG = config.debug
SECRET_KEY = config.secret_key.get()
DATABASE_URL = config.database_url
MAX_WORKERS = config.max_workers
```

### Migration Steps

1. **Create separate config.py**
   ```python
   # config.py
   from envcraft import EnvCraft
   
   class DjangoConfig(EnvCraft):
       # Move all env variables here
       pass
   ```

2. **Replace `env()` calls**
   ```python
   # Before
   DEBUG = env('DEBUG')
   
   # After
   DEBUG = config.debug
   ```

3. **Import in settings.py**
   ```python
   from .config import config
   ```

---

## Migrating from decouple

### Before (python-decouple)

```python
from decouple import config

DATABASE_URL = config('DATABASE_URL')
DEBUG = config('DEBUG', default=False, cast=bool)
MAX_WORKERS = config('MAX_WORKERS', default=4, cast=int)
SECRET_KEY = config('SECRET_KEY')
```

### After (EnvCraft)

```python
from envcraft import EnvCraft, Secret

class Config(EnvCraft):
    database_url: str
    debug: bool = False
    max_workers: int = 4
    secret_key: Secret[str]

config = Config.load()
```

### Migration Steps

1. **Replace all `config()` calls with class attributes**
2. **Types are automatic** (no need for `cast=`)
3. **Defaults are cleaner** (just use `=` in class)

---

## Side-by-Side Comparison

### Loading Environment Variables

```python
# python-dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')

# pydantic-settings
settings = Settings()

# EnvCraft
config = Config.load()
```

### Type Conversion

```python
# python-dotenv
max_workers = int(os.getenv('MAX_WORKERS', '4'))
debug = os.getenv('DEBUG', 'false').lower() == 'true'

# pydantic-settings
max_workers: int = 4
debug: bool = False

# EnvCraft (same as pydantic-settings)
max_workers: int = 4
debug: bool = False
```

### Validation

```python
# python-dotenv
if not os.getenv('DATABASE_URL'):
    raise ValueError("DATABASE_URL required")

# pydantic-settings
database_url: str  # Validates automatically

# EnvCraft (same + better errors)
database_url: str  # Validates with helpful suggestions
```

### Multi-file Support

```python
# python-dotenv
load_dotenv('.env')
load_dotenv('.env.local', override=True)

# pydantic-settings
# Not built-in

# EnvCraft
config = Config.load(env='production')
# Loads .env, .env.production, .env.local automatically
```

### Secret Management

```python
# python-dotenv
api_key = os.getenv('API_KEY')  # Can be logged accidentally

# pydantic-settings
api_key: str  # Can be logged accidentally

# EnvCraft
api_key: Secret[str]  # Masked in logs automatically
```

---

## Common Patterns

### Pattern 1: Singleton Config

```python
# Before (manual singleton)
_config = None

def get_config():
    global _config
    if _config is None:
        _config = load_config()
    return _config

# After (automatic)
config = Config.load()  # Cached automatically
```

### Pattern 2: Environment-Specific Configs

```python
# Before (manual)
env = os.getenv('ENV', 'development')
if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

# After (automatic)
config = Config.load(env='production')
```

### Pattern 3: Config Validation

```python
# Before (manual)
required = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
missing = [var for var in required if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing: {', '.join(missing)}")

# After (automatic)
config = Config.load()  # Validates automatically
# Or check without loading:
Config.diagnose()
```

---

## Gradual Migration Strategy

You don't have to migrate everything at once:

### Step 1: Install alongside existing solution
```bash
pip install envcraft
```

### Step 2: Create config class for new code
```python
from envcraft import EnvCraft

class NewConfig(EnvCraft):
    new_feature_api_key: str
    new_feature_enabled: bool = False

new_config = NewConfig.load()
```

### Step 3: Gradually move old config
```python
# Keep using old config
old_db_url = os.getenv('DATABASE_URL')

# Start using new config for new features
new_api_key = new_config.new_feature_api_key
```

### Step 4: Eventually consolidate
```python
class Config(EnvCraft):
    # All config in one place
    database_url: str
    new_feature_api_key: str
    new_feature_enabled: bool = False

config = Config.load()
```

---

## Need Help?

- Check the [README](README.md) for full documentation
- See [INTEGRATIONS.md](INTEGRATIONS.md) for framework-specific examples
- Run `envcraft --help` for CLI usage
- Open an issue on GitHub for questions
