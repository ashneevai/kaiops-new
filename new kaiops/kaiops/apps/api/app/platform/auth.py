from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class OIDCProvider:
    def __init__(self, issuer_url: str):
        self.issuer_url = issuer_url.rstrip("/")

    async def metadata(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.issuer_url}/.well-known/openid-configuration")
            response.raise_for_status()
            return response.json()


@lru_cache
def oidc_providers() -> dict[str, OIDCProvider]:
    return {
        "azuread": OIDCProvider("https://login.microsoftonline.com/common/v2.0"),
        "okta": OIDCProvider("https://example.okta.com/oauth2/default"),
    }


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_jwt(token)
    if "tenant_id" not in payload:
        raise HTTPException(status_code=403, detail="Tenant context missing")
    return payload
