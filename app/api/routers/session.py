import logging
from uuid import uuid4

from fastapi import APIRouter, Cookie, Response

from app.backend_schemas import SessionInitData

logger = logging.getLogger()


router = APIRouter()

@router.post("/session/init", response_model=SessionInitData)
def initialise_session(
    response: Response,
    user_id_from_cookie: str | None = Cookie(None, alias="user_id") # Read existing cookie
):
    current_user_id: str
    is_new: bool = False

    if user_id_from_cookie is None:
        current_user_id = str(uuid4())
        is_new = True
        response.set_cookie(
            key="user_id",
            value=current_user_id,
            httponly=True,
            max_age= 60 * 60 * 24 * 30,  # Cookie lasts a month
            samesite="lax",
            secure=False,
            path="/"
        )
    
        logger.info(f"New session started. User ID: {current_user_id} (cookie set)")

    else:
        current_user_id = user_id_from_cookie
        logger.info(f"Existing session recognized. User ID: {current_user_id} (from cookie)")

    return SessionInitData(user_id= current_user_id, is_new_user=is_new)
    