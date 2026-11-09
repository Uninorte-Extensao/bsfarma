"""
Configurações globais da aplicação.
Lê variáveis do arquivo .env automaticamente via pydantic-settings.
Acesse em qualquer módulo com: from app.core.config import settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Banco de dados
    database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Ambiente
    environment: str = "development"

    # CORS: origens separadas por vírgula
    cors_origins: str = "http://localhost:4200"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origins_lista(self) -> list[str]:
        return [origem.strip().rstrip("/") for origem in self.cors_origins.split(",") if origem.strip()]


# IMPORTAR OBJETO settings, NÃO A CLASSE SETTINGS()
settings = Settings()
