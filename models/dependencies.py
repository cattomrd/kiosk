from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union

from models.database import get_db
from models.models import User
from models.schemas import TokenData

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_aqui"  # Debes cambiar esto por una clave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_from_cookie(access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not access_token or not access_token.startswith("Bearer "):
        return None
    
    token = access_token[7:]  # Quitar "Bearer "
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user or not user.is_active:
        return None
    
    return user

def get_admin_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency para rutas de administración.
    Si el usuario no está autenticado o no es admin, redirecciona a login.
    """
    try:
        token = request.cookies.get("access_token")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401)
        
        token = token[7:]  # Quitar "Bearer "
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401)
        
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )
        
        return user
    except:
        # En caso de cualquier error, redirigir a login
        response = RedirectResponse(url="/login")
        return response