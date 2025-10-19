from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

from src.model.api_provider import ApiProvider
from src.service.rotation.rate_checking.impl.open_router_rate_limit_checker import open_router_rate_limit_checker
from src.service.rotation.token_service import token_service
from src.util.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class TokenCreationDto(BaseModel):
    token: str
    api_provider: ApiProvider


class TokenRotationDto(BaseModel):
    token_id: int
    api_provider: ApiProvider


# ToDo: 01/10 For testing only, delete it.
@router.get("/tokens/random")
async def get_token(api_provider: ApiProvider):
    token = await token_service.get_random_by_api_provider(api_provider=api_provider)
    return token


# ToDo: 03/10 For testing only, delete it.
@router.get("/tokens/locked")
async def get_locked_token():
    locked_token = await token_service.get_locked_tokens()
    return locked_token


# ToDo: 01/10 For testing only, delete it.
@router.get("/tokens/{token_id}")
async def get_token_by_id(token_id: int):
    token = await token_service.get_by_id(token_id)
    return token


@router.get("/tokens/open-router/rate-limit-check")
async def check_open_router_token_rate_limit(token_id: int):
    token = await token_service.get_by_id(token_id=token_id)
    rate_limit_info = await open_router_rate_limit_checker.is_unlocked(token.value)
    return rate_limit_info


@router.put("/tokens/rotation")
async def rotate_token(token_rotation_dto: TokenRotationDto):
    rotated_token = await token_service.rotate(
        token_id=token_rotation_dto.token_id,
        api_provider=token_rotation_dto.api_provider)
    return rotated_token


@router.post("/tokens")
async def save_token(body: TokenCreationDto):
    token_id: Optional[int] = await token_service.save(body.token, body.api_provider)

    if token_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate token")

    return { 'id': token_id }


@router.put("/tokens/lock/{token_id}")
async def lock_token(token_id: int):
    await token_service.lock(token_id)
    return 'Locked, if found.'


@router.put("/tokens/unlock/{token_id}")
async def unlock_token(token_id: int):
    await token_service.unlock(token_id)
    return 'Locked, if found.'


@router.delete("/tokens/{token_id}")
async def delete_token(token_id: str):
    await token_service.delete(token_id)
    return 'Deleted, if found.'
