from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "MedClarify AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Split comma-separated origins string into a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()