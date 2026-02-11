"""
EnvCraft - Enhanced environment configuration management

Public API:
    EnvCraft: Main configuration class
    Secret: Secret value wrapper with masking
    SecretBackend: Base class for custom secret backends
    EnvBackend: Environment variable backend
    AWSSecretsBackend: AWS Secrets Manager backend
    AzureKeyVaultBackend: Azure Key Vault backend
    HashiCorpVaultBackend: HashiCorp Vault backend
    register_backend: Register custom secret backend
    get_backend: Get registered backend by name
"""

from .config import EnvCraft, Secret
from .backends import (
    SecretBackend,
    EnvBackend,
    AWSSecretsBackend,
    AzureKeyVaultBackend,
    HashiCorpVaultBackend,
    register_backend,
    get_backend,
)

__version__ = "0.1.0"
__all__ = [
    "EnvCraft",
    "Secret",
    "SecretBackend",
    "EnvBackend",
    "AWSSecretsBackend",
    "AzureKeyVaultBackend",
    "HashiCorpVaultBackend",
    "register_backend",
    "get_backend",
]
