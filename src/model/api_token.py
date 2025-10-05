from src.model.api_provider import ApiProvider


class ApiToken:

    def __init__(self, token_id: int, api_provider: ApiProvider, value: str) -> None:
        self.token_id: int = token_id
        self.api_provider: ApiProvider = api_provider
        self.value: str = value
