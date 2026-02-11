# EnvCraft

> **Enhanced environment configuration for Python** - Type-safe, multi-source .env loading with better error messages.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Status

⚠️ **Early Development (v0.1.0)** - Use with caution in production

| Component | Status | Coverage |
|-----------|--------|----------|
| Core config loading | **Beta** | ✅ 26 tests |
| Secret backends (AWS/Azure/Vault) | **Experimental** | ⚠️ Untested |
| CLI tools | **Alpha** | ⚠️ Manual only |

**Safe for:** Development, staging, basic .env loading  
**Not ready for:** Mission-critical production

[Full status details →](docs/FEATURES.md#status)

---

## Quick Start

**Install:**
```bash
pip install envcraft
```

**Use:**
```python
from envcraft import EnvCraft
from pydantic import Field

class Config(EnvCraft):
    database_url: str = Field(..., description="Database connection")
    api_key: str
    debug: bool = False

config = Config.load()
print(config.database_url)
```

**Create `.env`:**
```bash
DATABASE_URL=postgresql://localhost/mydb
API_KEY=secret123
DEBUG=true
```

That's it! EnvCraft handles type validation, multi-file loading, and auto-generates `.env.example`.

---

## Key Features

- ✅ **Type validation** - Powered by Pydantic
- 🔄 **Multi-file support** - `.env`, `.env.{env}`, `.env.local`
- 📋 **Auto .env.example** - Generated automatically
- 🌍 **Variable interpolation** - `${VAR}` syntax
- 📝 **Smart errors** - Fuzzy matching suggestions
- 🔒 **Secret masking** - Prevents accidental logging
- 📦 **Caching & reload** - Thread-safe singleton pattern
- 🎯 **Strict mode** - Prevent config drift
- 🏗️ **Nested configs** - Organize complex settings
- 🛠️ **CLI tools** - `envcraft check`, `generate`, `docs`

[See all features →](docs/FEATURES.md)

---

## Why EnvCraft?

| Feature | python-dotenv | pydantic-settings | **EnvCraft** |
|---------|---------------|-------------------|---------------|
| Type validation | ❌ | ✅ | ✅ |
| Multi-file support | ⚠️ Manual merging | ⚠️ Custom logic needed | ✅ Built-in |
| Auto .env.example | ❌ | ❌ | ✅ |
| Smart error suggestions | ❌ | ⚠️ Basic errors | ✅ Fuzzy matching |
| Variable interpolation | ❌ | ❌ | ✅ |
| Secret backends | ❌ | ⚠️ Via custom sources | ✅ AWS/Azure/Vault |
| CLI tool | ❌ | ❌ | ✅ |
| Maturity | ✅ Very stable | ✅ Very stable | ⚠️ Early (v0.1.0) |

**Note:** python-dotenv and pydantic-settings are mature, battle-tested libraries. EnvCraft adds convenience features but is still in early development.

---

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Features](docs/FEATURES.md)** - Complete feature list
- **[Integrations](docs/INTEGRATIONS.md)** - FastAPI, Django, Flask examples
- **[Migration](docs/MIGRATION.md)** - Switch from other libraries
- **[Changelog](CHANGELOG.md)** - Version history

---

## CLI Tools

```bash
envcraft check      # Validate configuration
envcraft generate   # Create .env.example
envcraft docs       # Generate CONFIG.md
envcraft explain    # Explain a variable
```

---

## Installation

**Requirements:**
- Python 3.8+
- Pydantic v2.0+

**Basic:**
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

---

## Contributing

Contributions welcome! Help us reach 1.0:

- 🧪 Add tests (especially for AWS/Azure/Vault backends)
- 🐛 Report issues
- 📖 Improve documentation
- ✨ Suggest features

[GitHub Repository](https://github.com/ArnabbLank/EnvCraft)

---

## License

MIT © 2026 Arnab Sen
