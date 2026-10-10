from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import model_validator


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

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_MODE.lower() == "production":
            if self.JWT_SECRET_KEY == "your-secret-key-change-in-production" or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("Production requires an explicit JWT secret of at least 32 characters")
            if "DATABASE_URL" not in self.model_fields_set or "/Applications/MAMP/" in self.DATABASE_URL:
                raise ValueError("Production requires an explicit production DATABASE_URL")
            if self.DEBUG:
                raise ValueError("Production requires DEBUG=False")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
