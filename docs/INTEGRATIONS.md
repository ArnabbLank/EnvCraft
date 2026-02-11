# Framework Integrations

EnvCraft works seamlessly with popular Python frameworks.

## FastAPI

```python
from fastapi import FastAPI
from envcraft import EnvCraft, Secret
from pydantic import Field

class Settings(EnvCraft):
    app_name: str = "My API"
    debug: bool = False
    database_url: str = Field(..., description="PostgreSQL connection")
    redis_url: str = "redis://localhost"
    secret_key: Secret[str] = Field(..., description="JWT secret")
    cors_origins: str = "http://localhost:3000"

# Load once at startup
settings = Settings.load()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Access config anywhere
@app.get("/")
async def root():
    return {"app": settings.app_name}

# Hot reload endpoint (useful for development)
@app.post("/admin/reload-config")
async def reload_config():
    new_settings = Settings.reload()
    return {"status": "reloaded", "debug": new_settings.debug}

# Use with dependency injection
from fastapi import Depends

def get_settings():
    return Settings.load()

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"app": settings.app_name}
```

**With lifespan events:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = Settings.load()
    print(f"Starting {settings.app_name}")
    yield
    # Shutdown
    print("Shutting down")

app = FastAPI(lifespan=lifespan)
```

## Django

```python
# settings.py
from envcraft import EnvCraft, Secret
from pydantic import Field

class DjangoConfig(EnvCraft):
    secret_key: Secret[str] = Field(..., description="Django secret key")
    debug: bool = False
    database_url: str = Field(..., description="Database URL")
    allowed_hosts: str = "localhost,127.0.0.1"
    static_url: str = "/static/"
    media_url: str = "/media/"

# Load configuration
config = DjangoConfig.load()

# Use in Django settings
SECRET_KEY = config.secret_key.get()
DEBUG = config.debug
ALLOWED_HOSTS = config.allowed_hosts.split(',')
STATIC_URL = config.static_url
MEDIA_URL = config.media_url

# Parse database URL (use dj-database-url)
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(config.database_url)
}
```

**With nested configs:**
```python
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    engine: str = "django.db.backends.postgresql"
    name: str
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432

class DjangoConfig(EnvCraft):
    secret_key: Secret[str]
    debug: bool = False
    database: DatabaseConfig

config = DjangoConfig.load()

DATABASES = {
    'default': {
        'ENGINE': config.database.engine,
        'NAME': config.database.name,
        'USER': config.database.user,
        'PASSWORD': config.database.password,
        'HOST': config.database.host,
        'PORT': config.database.port,
    }
}
```

## Flask

```python
from flask import Flask
from envcraft import EnvCraft, Secret

class FlaskConfig(EnvCraft):
    secret_key: Secret[str]
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost"

config = FlaskConfig.load()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key.get()
app.config['DEBUG'] = config.debug
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_url

@app.route('/')
def index():
    return f"Running in {'debug' if config.debug else 'production'} mode"
```

## Celery

```python
# celery_config.py
from envcraft import EnvCraft
from pydantic import Field

class CeleryConfig(EnvCraft):
    broker_url: str = Field(default="redis://localhost:6379/0", description="Message broker URL")
    result_backend: str = Field(default="redis://localhost:6379/0", description="Result backend URL")
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True

config = CeleryConfig.load()

# celery.py
from celery import Celery

app = Celery('myapp')

app.conf.update(
    broker_url=config.broker_url,
    result_backend=config.result_backend,
    task_serializer=config.task_serializer,
    result_serializer=config.result_serializer,
    accept_content=config.accept_content.split(','),
    timezone=config.timezone,
    enable_utc=config.enable_utc,
)

@app.task
def process_data(data):
    # Task implementation
    pass
```

**With FastAPI + Celery:**
```python
# config.py
from envcraft import EnvCraft
from pydantic import BaseModel

class CelerySettings(BaseModel):
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"

class AppConfig(EnvCraft):
    app_name: str = "My API"
    database_url: str
    celery: CelerySettings

config = AppConfig.load()

# main.py
from fastapi import FastAPI, BackgroundTasks
from celery import Celery

app = FastAPI()
celery_app = Celery(
    'worker',
    broker=config.celery.broker_url,
    backend=config.celery.result_backend
)

@celery_app.task
def send_email(email: str):
    # Send email logic
    pass

@app.post("/send-email")
async def trigger_email(email: str):
    send_email.delay(email)
    return {"status": "queued"}
```

## Pytest

```python
# conftest.py
import pytest
from envcraft import EnvCraft

class TestConfig(EnvCraft):
    database_url: str = "postgresql://test:test@localhost/test_db"
    redis_url: str = "redis://localhost:6379/1"
    debug: bool = True

@pytest.fixture(scope="session")
def config():
    return TestConfig.load(cache=False)

@pytest.fixture(autouse=True)
def reset_config():
    """Reset config cache between tests"""
    TestConfig._instance = None
    yield
```

**Testing with different environments:**
```python
# test_config.py
import pytest
from pathlib import Path

def test_production_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Create production .env
    env_file = tmp_path / ".env.production"
    env_file.write_text("""
DATABASE_URL=postgresql://prod:pass@prod-db/myapp
DEBUG=false
""")
    
    from myapp.config import AppConfig
    config = AppConfig.load(env='production', cache=False)
    
    assert config.debug is False
    assert "prod-db" in config.database_url
```

## Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Validate config before starting
RUN envcraft check

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=false
    env_file:
      - .env
      - .env.production
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine
```

## Kubernetes

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  .env.production: |
    APP_NAME=MyApp
    DEBUG=false
    DATABASE__HOST=postgres-service
    DATABASE__PORT=5432
    DATABASE__NAME=myapp
    REDIS__HOST=redis-service
    REDIS__PORT=6379

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        env:
        - name: DATABASE__USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DATABASE__PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        volumeMounts:
        - name: config
          mountPath: /app/.env.production
          subPath: .env.production
      volumes:
      - name: config
        configMap:
          name: app-config
```

## AWS Lambda

```python
# lambda_function.py
from envcraft import EnvCraft, Secret

class LambdaConfig(EnvCraft):
    database_url: str
    api_key: Secret[str] = Secret.from_aws("prod/api_key", region="us-east-1")
    debug: bool = False

# Load once (cached across invocations)
config = LambdaConfig.load()

def lambda_handler(event, context):
    # Config is already loaded and cached
    return {
        'statusCode': 200,
        'body': f'Running in {"debug" if config.debug else "production"} mode'
    }
```

## Streamlit

```python
# app.py
import streamlit as st
from envcraft import EnvCraft

class StreamlitConfig(EnvCraft):
    app_title: str = "My Dashboard"
    api_url: str
    refresh_interval: int = 60

config = StreamlitConfig.load()

st.set_page_config(page_title=config.app_title)
st.title(config.app_title)

# Use config throughout app
data = fetch_data(config.api_url)
st.dataframe(data)
```

## Tips for All Frameworks

### 1. Load Once at Startup
```python
# Good: Load once
config = AppConfig.load()

# Bad: Load on every request
@app.get("/")
def handler():
    config = AppConfig.load()  # Don't do this!
```

### 2. Use Environment-Specific Files
```python
# Development
config = AppConfig.load(env='development')

# Production
config = AppConfig.load(env='production')
```

### 3. Validate in CI/CD
```bash
# In your CI pipeline
envcraft check || exit 1
```

### 4. Generate Docs for Team
```bash
envcraft docs
git add CONFIG.md
```

### 5. Use Strict Mode in Production
```python
# Production deployment
config = AppConfig.load(
    env='production',
    strict=True  # Fail on unknown variables
)
```
