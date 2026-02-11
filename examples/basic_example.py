"""
EnvCraft - Complete Feature Showcase

This example demonstrates all major features of EnvCraft.
"""

from envcraft import EnvCraft, Secret
from pydantic import BaseModel, Field


# 1. Nested Configuration
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = Field(..., description="Database name")


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379


# 2. Main Configuration with all features
class AppConfig(EnvCraft):
    # Basic fields
    app_name: str = Field(default="MyApp", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Nested configs
    database: DatabaseConfig
    redis: RedisConfig
    
    # Secrets (can load from AWS, Azure, Vault)
    api_key: str = Field(..., description="External API key")
    
    # Optional fields
    max_workers: int = Field(default=4, description="Maximum worker threads")


def main():
    print("=" * 60)
    print("EnvCraft Feature Showcase")
    print("=" * 60)
    
    # Feature 1: Auto-generate .env.example
    print("\n1. Auto-generating .env.example...")
    AppConfig.generate_example()
    
    # Feature 2: Generate documentation
    print("\n2. Generating CONFIG.md documentation...")
    AppConfig.generate_docs()
    
    # Feature 3: Diagnose configuration
    print("\n3. Running configuration diagnosis...")
    is_valid = AppConfig.diagnose()
    
    if not is_valid:
        print("\n⚠️  Some required variables are missing.")
        print("Please set them in your .env file and try again.")
        return
    
    # Feature 4: Load with various options
    print("\n4. Loading configuration...")
    
    # Load with source tracking
    config = AppConfig.load(
        show_sources=True,      # Show where each variable came from
        strict=False,            # Don't fail on unknown variables
        cache=True               # Cache the instance
    )
    
    # Feature 5: Access configuration
    print("\n5. Accessing configuration values...")
    print(f"   App Name: {config.app_name}")
    print(f"   Debug Mode: {config.debug}")
    print(f"   Database: {config.database.host}:{config.database.port}/{config.database.name}")
    print(f"   Redis: {config.redis.host}:{config.redis.port}")
    print(f"   API Key: {config.api_key}")  # Masked as ***
    print(f"   Max Workers: {config.max_workers}")
    
    # Feature 6: Reload support with callbacks
    print("\n6. Setting up reload callback...")
    
    def on_config_reload(new_config):
        print(f"   ✓ Config reloaded! Debug mode is now: {new_config.debug}")
    
    AppConfig.on_reload(on_config_reload)
    
    # Feature 7: Demonstrate caching
    print("\n7. Testing singleton caching...")
    config2 = AppConfig.load()
    print(f"   Same instance? {config is config2}")
    
    print("\n" + "=" * 60)
    print("All features demonstrated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Example .env file content (create this manually):
    """
    # .env
    APP_NAME=MyAwesomeApp
    DEBUG=true
    
    # Database configuration (nested with __)
    DATABASE__HOST=localhost
    DATABASE__PORT=5432
    DATABASE__NAME=mydb
    
    # Redis configuration
    REDIS__HOST=redis.example.com
    REDIS__PORT=6380
    
    # Secrets
    API_KEY=sk_test_1234567890
    
    # Optional
    MAX_WORKERS=8
    
    # Variable interpolation example:
    # USER=myuser
    # DATABASE__HOST=db.example.com
    # DATABASE__NAME=mydb
    # DATABASE_URL=postgresql://${USER}@${DATABASE__HOST}/${DATABASE__NAME}
    """
    
    main()
