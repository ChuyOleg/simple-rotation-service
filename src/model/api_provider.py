from enum import Enum


class ApiProvider(Enum):
    OPEN_ROUTER = "OpenRouter"
    OPEN_AI = "OpenAI"
    UNKNOWN = "Unknown"
