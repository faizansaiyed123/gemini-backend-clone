from src.configs.settings import settings 
from src.services.tables import Tables
from src.common.app_constants import AppConstants
from fastapi import Depends, HTTPException, status
from src.common.app_response import AppResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer,HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()
tables = Tables()
app_response = AppResponse()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials  # the raw JWT string
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload["sub"]