from fastapi import Depends
from app.db.database import get_db_session
from app.core.redis import get_redis
from app.services.email import get_email_service
from app.services.auth import AuthService

def get_auth_service(
    session=Depends(get_db_session),
    cache=Depends(get_redis),
    email=Depends(get_email_service),
):
    return AuthService(cache, session, email)