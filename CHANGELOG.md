# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-11

### Added
- Initial release of EnvCraft
- Core `EnvCraft` class for environment configuration management
- `Secret` wrapper for sensitive values with automatic masking
- Multi-file support (.env, .env.{env}, .env.local)
- Auto-generation of .env.example files
- Variable interpolation with `${VAR}` syntax
- Smart error messages with fuzzy matching suggestions
- Configuration diagnosis tool
- Singleton pattern with thread-safe caching
- Reload support with callbacks
- Source tracking (show which file provided each variable)
- Strict mode for preventing configuration drift
- Documentation generator (CONFIG.md)
- Nested configuration support with `__` delimiter
- Secret backend plugins:
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - Custom backends
- CLI tool with commands:
  - `envcraft check` - Validate configuration
  - `envcraft generate` - Generate .env.example
  - `envcraft docs` - Generate documentation
  - `envcraft explain` - Explain variables
- Comprehensive test suite (20 tests)
- Full documentation with migration guides and integration examples

[0.1.0]: https://github.com/yourusername/envcraft/releases/tag/v0.1.0
