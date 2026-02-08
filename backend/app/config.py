from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "mysql+pymysql://root:root@localhost/SANSA?unix_socket=/Applications/MAMP/tmp/mysql/mysql.sock"
    )

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    # App
    APP_MODE: str = "development"
    DEBUG: bool = True

    # Admin Defaults
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@sansa.local"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
