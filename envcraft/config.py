from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Generic, TypeVar, Any, Dict, Optional, Callable, List
from pathlib import Path
from threading import RLock
from difflib import get_close_matches
import os
import re

T = TypeVar('T')

# Global registries (outside the class to avoid Pydantic interference)
_instances: Dict[type, 'EnvConfig'] = {}
_locks: Dict[type, RLock] = {}
_reload_callbacks: Dict[type, List[Callable]] = {}

class Secret(Generic[T]):
    """Wrapper for secret values that won't be logged or printed"""
    def __init__(self, value: T, backend: Optional[str] = None, key: Optional[str] = None):
        if backend and key:
            # Lazy load from backend
            self._backend = backend
            self._key = key
            self._value = None
        else:
            self._value = value
            self._backend = None
            self._key = None
    
    def get(self) -> T:
        if self._value is None and self._backend and self._key:
            # Lazy load from backend
            from .backends import get_backend
            backend = get_backend(self._backend)
            self._value = backend.get_secret(self._key)
        return self._value
    
    def __repr__(self) -> str:
        return "Secret('***')"
    
    def __str__(self) -> str:
        return "***"
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Custom Pydantic validator to accept strings and convert to Secret"""
        from pydantic_core import core_schema
        
        def validate_secret(value):
            if isinstance(value, Secret):
                return value
            # Convert string to Secret
            return Secret(value)
        
        python_schema = core_schema.no_info_plain_validator_function(validate_secret)
        return core_schema.json_or_python_schema(
            json_schema=python_schema,
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: "***",
                return_schema=core_schema.str_schema(),
            ),
        )
    
    @classmethod
    def from_backend(cls, key: str, backend: str = 'env'):
        """Create a Secret that loads from a backend"""
        return cls(None, backend=backend, key=key)
    
    @classmethod
    def from_aws(cls, key: str, region: str = "us-east-1"):
        """Create a Secret that loads from AWS Secrets Manager"""
        from .backends import register_backend, AWSSecretsBackend
        backend_name = f"aws_{region}"
        try:
            from .backends import get_backend
            get_backend(backend_name)
        except ValueError:
            register_backend(backend_name, AWSSecretsBackend(region=region))
        return cls(None, backend=backend_name, key=key)
    
    @classmethod
    def from_azure(cls, key: str, vault_url: str):
        """Create a Secret that loads from Azure Key Vault"""
        from .backends import register_backend, AzureKeyVaultBackend
        backend_name = f"azure_{vault_url}"
        try:
            from .backends import get_backend
            get_backend(backend_name)
        except ValueError:
            register_backend(backend_name, AzureKeyVaultBackend(vault_url=vault_url))
        return cls(None, backend=backend_name, key=key)
    
    @classmethod
    def from_vault(cls, key: str, url: str, token: Optional[str] = None):
        """Create a Secret that loads from HashiCorp Vault"""
        from .backends import register_backend, HashiCorpVaultBackend
        backend_name = f"vault_{url}"
        try:
            from .backends import get_backend
            get_backend(backend_name)
        except ValueError:
            register_backend(backend_name, HashiCorpVaultBackend(url=url, token=token))
        return cls(None, backend=backend_name, key=key)


class EnvCraft(BaseSettings):
    """Enhanced environment configuration with better errors and multi-source loading"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
        env_nested_delimiter='__',
        # Don't try to parse complex types as JSON
        json_schema_extra={'env_parse_none_str': None},
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self._source_map: Dict[str, str] = {}
    
    @classmethod
    def _get_lock(cls) -> RLock:
        """Get or create lock for this class"""
        if cls not in _locks:
            _locks[cls] = RLock()
        return _locks[cls]
    
    @classmethod
    def _get_callbacks(cls) -> List[Callable]:
        """Get or create callback list for this class"""
        if cls not in _reload_callbacks:
            _reload_callbacks[cls] = []
        return _reload_callbacks[cls]
    
    @classmethod
    def _interpolate_variables(cls, content: str, env_vars: Dict[str, str]) -> str:
        """Interpolate ${VAR} syntax in environment file content"""
        def replace_var(match):
            var_name = match.group(1)
            # Check in current env_vars first, then os.environ
            return env_vars.get(var_name, os.environ.get(var_name, match.group(0)))
        
        # Match ${VAR} or $VAR
        pattern = r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
        
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return env_vars.get(var_name, os.environ.get(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, content)
    
    @classmethod
    def load(cls, env: str = None, auto_generate_example: bool = True, show_sources: bool = False, strict: bool = False, cache: bool = True):
        """Load config with environment-specific overrides"""
        # Return cached instance if available
        if cache and cls in _instances:
            return _instances[cls]
        
        lock = cls._get_lock()
        with lock:
            # Auto-generate .env.example if it doesn't exist
            if auto_generate_example and not Path('.env.example').exists():
                cls.generate_example()
            
            # Apply strict mode if requested
            if strict:
                # Create a new config with extra='forbid'
                original_extra = cls.model_config.get('extra', 'ignore')
                cls.model_config['extra'] = 'forbid'
            else:
                original_extra = None
            
            env_files = ['.env']
            if env:
                env_files.append(f'.env.{env}')
            env_files.append('.env.local')
            
            # Track which file provides each variable and load with interpolation
            source_map = {}
            all_vars = {}
            
            for env_file in env_files:
                if Path(env_file).exists():
                    with open(env_file) as f:
                        content = f.read()
                    
                    # Parse variables first
                    temp_vars = {}
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            temp_vars[key] = value.strip()
                    
                    # Interpolate variables
                    interpolated_content = cls._interpolate_variables(content, {**all_vars, **temp_vars})
                    
                    # Parse again with interpolated values
                    for line in interpolated_content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip().lower()
                            all_vars[key] = value.strip()
                            source_map[key] = env_file
                            # Set in environment for Pydantic to pick up
                            os.environ[key.upper()] = value.strip()
            
            # In strict mode, check for unknown variables
            if strict:
                known_fields = {name.lower() for name in cls.model_fields.keys()}
                unknown_vars = set(all_vars.keys()) - known_fields
                if unknown_vars:
                    unknown_list = ', '.join(sorted(unknown_vars))
                    raise ValueError(f"Unknown environment variables in strict mode: {unknown_list}")
            
            try:
                instance = cls()
                instance._source_map = source_map
                
                if cache:
                    _instances[cls] = instance
                
                if show_sources:
                    cls._print_sources(instance, source_map)
                
                return instance
            except ValidationError as e:
                cls._format_error(e)
                raise
            finally:
                # Restore original extra setting
                if original_extra is not None:
                    cls.model_config['extra'] = original_extra
    
    @classmethod
    def reload(cls):
        """Reload configuration from files"""
        lock = cls._get_lock()
        with lock:
            if cls in _instances:
                del _instances[cls]
            new_instance = cls.load(cache=True)
            
            # Trigger reload callbacks
            for callback in cls._get_callbacks():
                callback(new_instance)
            
            return new_instance
    
    @classmethod
    def on_reload(cls, callback: Callable[['EnvConfig'], None]):
        """Register a callback to be called when config is reloaded"""
        cls._get_callbacks().append(callback)
    
    @classmethod
    def _print_sources(cls, instance, source_map: Dict[str, str]):
        """Print which file supplied each variable"""
        print("\n📋 Environment Variable Sources:\n")
        for field_name in cls.model_fields.keys():
            env_name = field_name.lower()
            source = source_map.get(env_name, "default value")
            value = getattr(instance, field_name)
            
            # Mask secrets
            if isinstance(value, Secret):
                display_value = "***"
            else:
                display_value = value
            
            print(f"  {field_name.upper()} = {display_value}")
            print(f"    └─ loaded from {source}")
        print()
    
    @classmethod
    def diagnose(cls):
        """Validate configuration and report status of all fields"""
        print("\n🔍 Configuration Diagnosis:\n")
        
        all_valid = True
        env_vars = {k.lower(): v for k, v in os.environ.items()}
        
        def check_fields(fields, prefix=""):
            nonlocal all_valid
            
            for field_name, field_info in fields.items():
                field_type = field_info.annotation
                
                # Check if nested BaseModel
                try:
                    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                        print(f"  {prefix}{field_name.upper()} (nested):")
                        check_fields(field_type.model_fields, f"{prefix}{field_name.upper()}__")
                        continue
                except TypeError:
                    pass
                
                env_name = f"{prefix}{field_name.upper()}"
                env_name_lower = env_name.lower()
                
                # Check if variable is present
                has_value = env_name_lower in env_vars
                has_default = field_info.default is not None and field_info.default != ...
                is_required = field_info.is_required()
                
                if has_value:
                    print(f"  ✓ {env_name} present")
                elif has_default:
                    print(f"  ✓ {env_name} using default ({field_info.default})")
                elif is_required:
                    print(f"  ✗ {env_name} missing (required)")
                    all_valid = False
                else:
                    print(f"  ⚠ {env_name} not set (optional)")
        
        check_fields(cls.model_fields)
        
        print()
        
        if all_valid:
            print("✅ All required variables are present\n")
            return True
        else:
            print("❌ Some required variables are missing\n")
            return False
    
    @classmethod
    def generate_docs(cls, output_file: str = 'CONFIG.md'):
        """Generate Markdown documentation from config schema"""
        lines = [
            "# Configuration Documentation\n",
            "This document describes all available configuration options.\n",
        ]
        
        def add_field_docs(fields, prefix="", level=2):
            for field_name, field_info in fields.items():
                field_type = field_info.annotation
                
                # Check if nested BaseModel
                try:
                    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                        lines.append(f"{'#' * level} {prefix}{field_name.upper()}\n")
                        if field_info.description:
                            lines.append(f"{field_info.description}\n")
                        lines.append("")
                        add_field_docs(field_type.model_fields, f"{prefix}{field_name.upper()}__", level + 1)
                        continue
                except TypeError:
                    pass
                
                env_name = f"{prefix}{field_name.upper()}"
                type_str = str(field_type).replace('typing.', '').replace('envconfig.config.', '')
                
                lines.append(f"{'#' * level} {env_name}\n")
                
                if field_info.description:
                    lines.append(f"{field_info.description}\n")
                
                lines.append(f"- **Type:** `{type_str}`")
                lines.append(f"- **Required:** {'Yes' if field_info.is_required() else 'No'}")
                
                if field_info.default is not None and field_info.default != ...:
                    lines.append(f"- **Default:** `{field_info.default}`")
                
                lines.append("")
                lines.append("**Example:**")
                lines.append("```bash")
                if field_info.default is not None and field_info.default != ...:
                    lines.append(f"{env_name}={field_info.default}")
                else:
                    lines.append(f"{env_name}=<value>")
                lines.append("```\n")
        
        add_field_docs(cls.model_fields)
        
        Path(output_file).write_text('\n'.join(lines))
        print(f"✓ Generated {output_file}")
    
    @classmethod
    def _format_error(cls, error: ValidationError):
        """Format validation errors with helpful messages and smart suggestions"""
        print("\n❌ Environment Configuration Error:\n")
        
        # Get all valid field names for suggestions
        valid_fields = set()
        
        def collect_fields(fields, prefix=""):
            for field_name in fields.keys():
                field_type = fields[field_name].annotation
                try:
                    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                        collect_fields(field_type.model_fields, f"{prefix}{field_name.upper()}__")
                    else:
                        valid_fields.add(f"{prefix}{field_name.upper()}")
                except TypeError:
                    valid_fields.add(f"{prefix}{field_name.upper()}")
        
        collect_fields(cls.model_fields)
        
        for err in error.errors():
            field = err['loc'][0]
            msg = err['msg']
            error_type = err['type']
            
            print(f"  • {field}: {msg}")
            
            # Add helpful hints
            if error_type == 'missing':
                print(f"    → Set {field.upper()} in your .env file or environment")
                
                # Smart suggestions
                suggestions = get_close_matches(field.upper(), valid_fields, n=3, cutoff=0.6)
                if suggestions:
                    print(f"    💡 Did you mean: {', '.join(suggestions)}?")
            elif 'int' in error_type:
                print(f"    → {field.upper()} must be a valid integer")
            elif 'bool' in error_type:
                print(f"    → {field.upper()} must be true/false or 1/0")
            elif 'extra' in error_type:
                # Unknown field in strict mode
                print(f"    → {field.upper()} is not a valid configuration variable")
                suggestions = get_close_matches(field.upper(), valid_fields, n=3, cutoff=0.6)
                if suggestions:
                    print(f"    💡 Did you mean: {', '.join(suggestions)}?")
            print()
    
    @classmethod
    def generate_example(cls, output_file: str = '.env.example'):
        """Generate .env.example from config schema"""
        lines = ["# Environment Configuration Template\n"]
        
        def add_fields(fields, prefix=""):
            for field_name, field_info in fields.items():
                field_type = field_info.annotation
                description = field_info.description
                
                # Check if this is a nested BaseModel
                try:
                    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                        # Nested config
                        lines.append(f"# {prefix}{field_name.upper()} (nested)")
                        if description:
                            lines.append(f"# {description}")
                        lines.append("")
                        add_fields(field_type.model_fields, f"{prefix}{field_name.upper()}__")
                        continue
                except TypeError:
                    pass
                
                env_name = f"{prefix}{field_name.upper()}"
                
                # Add description if available
                if description:
                    lines.append(f"# {description}")
                
                # Add comment with type
                type_str = str(field_type).replace('typing.', '').replace('envconfig.config.', '')
                lines.append(f"# Type: {type_str}")
                
                # Add default if exists
                if field_info.default is not None and field_info.default != ...:
                    lines.append(f"{env_name}={field_info.default}")
                else:
                    lines.append(f"{env_name}=")
                lines.append("")
        
        add_fields(cls.model_fields)
        
        Path(output_file).write_text('\n'.join(lines))
        print(f"✓ Generated {output_file}")


# Example usage
if __name__ == "__main__":
    class AppConfig(EnvConfig):
        database_url: str = Field(..., description="PostgreSQL connection string")
        api_key: str = Field(..., description="External API key")
        debug: bool = False
        max_workers: int = 4
        redis_host: str = "localhost"
        
        @field_validator('database_url')
        @classmethod
        def validate_db_url(cls, v: str) -> str:
            if not v.startswith(('postgresql://', 'postgres://')):
                raise ValueError("Must be a valid PostgreSQL URL (postgresql://...)")
            return v
    
    # Generate example file
    AppConfig.generate_example()
    
    # Try to load (will fail with nice errors if vars missing)
    try:
        config = AppConfig.load()
        print(f"✓ Config loaded successfully")
        print(f"  Debug mode: {config.debug}")
        print(f"  Max workers: {config.max_workers}")
    except ValidationError:
        print("Fix the errors above and try again")
