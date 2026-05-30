"""
SINATOR — Fireworks Routes V15.4 (Playwright, 2026-05-31)
"""
import time
import logging
from fastapi import APIRouter, HTTPException

from agent_toolbox.core.fireworks_service import login_fireworks, create_api_key
from agent_toolbox.api.schemas import (
    FireworksRegisterRequest, FireworksRegisterResponse,
    FireworksApiKeyRequest, FireworksApiKeyResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fireworks", tags=["Fireworks AI Services"])


@router.post("/login", response_model=FireworksRegisterResponse)
async def login(request: FireworksRegisterRequest):
    """Login to Fireworks AI account (Playwright + CUA onboarding)."""
    t0 = time.time()
    result = await login_fireworks(request.email, request.password)
    return FireworksRegisterResponse(
        status=result["status"],
        account_email=request.email,
        execution_time=f"{time.time()-t0:.2f}s",
        error=result.get("error"),
    )


@router.post("/apikey", response_model=FireworksApiKeyResponse)
async def apikey(request: FireworksApiKeyRequest):
    """Create Fireworks API Key with optional Session Reuse.

    If email+password provided: logs in first, then creates key with same session.
    If only key_name provided: creates new page (may redirect to /login).
    """
    t0 = time.time()

    page = None
    playwright = None
    browser = None

    if request.email and request.password:
        login_result = await login_fireworks(request.email, request.password)
        page = login_result.get("page")
        playwright = login_result.get("playwright")
        browser = login_result.get("browser")
        if not login_result.get("success"):
            return FireworksApiKeyResponse(
                status=login_result.get("status", "failed"),
                execution_time=f"{time.time()-t0:.2f}s",
                error=login_result.get("error", "Login failed"),
            )

    result = await create_api_key(
        request.key_name,
        page=page,
        playwright=playwright,
        browser=browser,
    )
    return FireworksApiKeyResponse(
        api_key=result.get("api_key"),
        status=result["status"],
        execution_time=f"{time.time()-t0:.2f}s",
        error=result.get("error"),
    )
