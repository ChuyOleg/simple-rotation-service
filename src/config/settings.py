from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str = Field(default="localhost", alias="LOCAL_POSTGRES_HOST")
    port: int = Field(default=5432, alias="LOCAL_POSTGRES_PORT")
    database: str = Field(default="uopp_ai_data", alias="LOCAL_POSTGRES_DATABASE")
    username: str = Field(default="postgres", alias="LOCAL_POSTGRES_USERNAME")
    password: str = Field(default="password", alias="LOCAL_POSTGRES_PASSWORD")

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class TokenEncryptionSettings(BaseSettings):
    secret_key: bytes = Field(default=b"uBfxfR1bz7BMbq1oJoLHS7-PS1Uogor3sfYOS5K4TgM=", alias="TOKEN_ENCRYPTION_SECRET_KEY")

    @classmethod
    @field_validator("secret_key", mode="before")
    def convert_to_bytes(cls, v) -> bytes:
        if isinstance(v, bytes):
            return v
        if isinstance(v, str):
            return v.encode()
        raise TypeError("Expected str or bytes for secret_key")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RotationSettings(BaseSettings):
    cron: str = Field(default="1 * * * *", alias="ROTATION_CRON")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    token_encryption: TokenEncryptionSettings = Field(default_factory=TokenEncryptionSettings)
    rotation: RotationSettings = Field(default_factory=RotationSettings)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
