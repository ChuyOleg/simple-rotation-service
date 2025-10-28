from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    database: str = Field(alias="POSTGRES_DATABASE")
    username: str = Field(alias="POSTGRES_USERNAME")
    password: str = Field(alias="POSTGRES_PASSWORD")

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class TokenEncryptionSettings(BaseSettings):
    secret_key: bytes = Field(alias="TOKEN_ENCRYPTION_SECRET_KEY")

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
    cron: str = Field(alias="ROTATION_CRON")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RotationTesterSettings(BaseSettings):
    cron: str = Field(alias="ROTATION_TESTER_CRON")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    token_encryption: TokenEncryptionSettings = Field(default_factory=TokenEncryptionSettings)
    rotation: RotationSettings = Field(default_factory=RotationSettings)
    rotation_tester: RotationTesterSettings = Field(default_factory=RotationTesterSettings)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
