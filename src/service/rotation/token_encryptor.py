import hashlib
import hmac

from cryptography.fernet import Fernet

from src.config.settings import settings


class TokenEncryptor:
    def __init__(self, secret_key: bytes) -> None:
        self._secret_key: bytes = secret_key
        self._internal_encryptor = Fernet(self._secret_key)

    def encrypt(self, token: str) -> str:
        return self._internal_encryptor.encrypt(token.encode()).decode()

    def decrypt(self, token: bytes) -> str:
        return self._internal_encryptor.decrypt(token).decode()

    def hash(self, token: str) -> str:
        return hmac.new(self._secret_key, token.encode(), hashlib.sha256).hexdigest()


token_encryptor = TokenEncryptor(settings.token_encryption.secret_key)
