from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import os


class SecretBackend(ABC):
    """Base class for secret backend plugins"""
    
    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by key"""
        pass


class AWSSecretsBackend(SecretBackend):
    """AWS Secrets Manager backend"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None
    
    def get_secret(self, key: str) -> str:
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('secretsmanager', region_name=self.region)
            except ImportError:
                raise ImportError("boto3 is required for AWS Secrets Manager. Install with: pip install boto3")
        
        try:
            response = self._client.get_secret_value(SecretId=key)
            return response['SecretString']
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret '{key}' from AWS Secrets Manager: {e}")


class AzureKeyVaultBackend(SecretBackend):
    """Azure Key Vault backend"""
    
    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self._client = None
    
    def get_secret(self, key: str) -> str:
        if self._client is None:
            try:
                from azure.keyvault.secrets import SecretClient
                from azure.identity import DefaultAzureCredential
                self._client = SecretClient(vault_url=self.vault_url, credential=DefaultAzureCredential())
            except ImportError:
                raise ImportError("azure-keyvault-secrets and azure-identity are required. Install with: pip install azure-keyvault-secrets azure-identity")
        
        try:
            secret = self._client.get_secret(key)
            return secret.value
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret '{key}' from Azure Key Vault: {e}")


class HashiCorpVaultBackend(SecretBackend):
    """HashiCorp Vault backend"""
    
    def __init__(self, url: str, token: Optional[str] = None, mount_point: str = "secret"):
        self.url = url
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self._client = None
    
    def get_secret(self, key: str) -> str:
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.url, token=self.token)
            except ImportError:
                raise ImportError("hvac is required for HashiCorp Vault. Install with: pip install hvac")
        
        try:
            secret = self._client.secrets.kv.v2.read_secret_version(path=key, mount_point=self.mount_point)
            return secret['data']['data']['value']
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret '{key}' from HashiCorp Vault: {e}")


class EnvBackend(SecretBackend):
    """Fallback to environment variables"""
    
    def get_secret(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not found")
        return value


# Global registry of backends
_backend_registry: Dict[str, SecretBackend] = {}


def register_backend(name: str, backend: SecretBackend):
    """Register a custom secret backend"""
    _backend_registry[name] = backend


def get_backend(name: str) -> SecretBackend:
    """Get a registered backend by name"""
    if name not in _backend_registry:
        raise ValueError(f"Backend '{name}' not registered. Available: {list(_backend_registry.keys())}")
    return _backend_registry[name]


# Register default backends
register_backend('env', EnvBackend())
