from envcraft import EnvCraft
from pydantic import Field

class AppConfig(EnvCraft):
    database_url: str = Field(..., description="Database connection string")
    api_key: str = Field(..., description="API key")
    debug: bool = Field(default=False, description="Enable debug mode")
    max_workers: int = Field(default=4, description="Maximum worker threads")
