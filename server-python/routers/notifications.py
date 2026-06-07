import os
import hmac
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException
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


# FIX ISSUE 3 ONLY: Explicitly binding matching target via alias keyword
def _verify_service_auth(
    x_service_auth: Optional[str] = Header(default=None, alias="X-Service-Auth")
) -> None:
    """Dependency that validates the internal service auth header string securely."""
    if not INTERNAL_SERVICE_SECRET:
        return
    
    if not x_service_auth or not hmac.compare_digest(x_service_auth, INTERNAL_SERVICE_SECRET):
        raise HTTPException(
            status_code=401, 
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
