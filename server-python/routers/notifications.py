import os
import hmac
import logging  # Added for tracking critical security logs
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status  # Added status import
from pydantic import BaseModel
from services.notification_service import notify_team_leader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notify", tags=["Notifications"])

class JoinRequestPayload(BaseModel):
    teamId: int
    pitch: str
    skills: str
    github: str

INTERNAL_SERVICE_SECRET = os.getenv("INTERNAL_SERVICE_SECRET", "")


def _verify_service_auth(x_service_auth: Optional[str] = Header(default=None)) -> None:
    """Dependency that validates the internal service auth header string securely."""
    
    # FIX ISSUE 1 ONLY: Fail-Safe / Default-Deny Security Guard
    if not INTERNAL_SERVICE_SECRET:
        logger.critical("SECURITY CONFIGURATION ERROR: INTERNAL_SERVICE_SECRET environment variable is missing or blank!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: authentication setup is missing."
        )
    
    if not x_service_auth or not hmac.compare_digest(x_service_auth, INTERNAL_SERVICE_SECRET):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: invalid service auth"
        )

@router.post("/join-request")
async def handle_join_request_notification(
    payload: JoinRequestPayload,
    _: None = Depends(_verify_service_auth),
):
    """
    Webhook endpoint called by the Java backend when a new join request is created.
    """
    result = notify_team_leader(
        team_id=payload.teamId,
        pitch=payload.pitch,
        skills=payload.skills,
        github=payload.github
    )
    return result
