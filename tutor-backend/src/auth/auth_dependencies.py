from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import decode_jwt_token

security = HTTPBearer()

def jwt_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    user = decode_jwt_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido"
        )
    return user

def admin_required(
    user: dict = Depends(jwt_required)
):
    # Mostramos los permisos del usuario como log
    print(user.get("is_admin"))
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return user
