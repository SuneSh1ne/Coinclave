from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "uploads"
    max_file_size_mb: int = 5
    
    @property
    def sync_database_url(self) -> str:
        """Синхронная версия URL для Alembic"""
        return self.database_url.replace("+asyncpg", "")
    
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()