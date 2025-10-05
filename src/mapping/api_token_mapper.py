from typing import Dict, Any

from src.model.api_provider import ApiProvider
from src.model.api_token import ApiToken


def map_db_row_to_api_token_dict(row: Any) -> Dict[str, Any]:
    return {
        'id': row["id"],
        'api_provider': row['api_provider'],
        'token_encrypted': row["token_encrypted"]}


def map_api_token_dict_to_api_token(api_token_dict: Dict[str, Any], token_value: str) -> ApiToken:
    return ApiToken(
        token_id=api_token_dict['id'],
        api_provider=ApiProvider(api_token_dict['api_provider']),
        value=token_value)
