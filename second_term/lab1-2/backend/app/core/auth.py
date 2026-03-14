from datetime import datetime, timedelta, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import app.core.config  # noqa: F401  (чтобы load_dotenv сработал)
from app.api.schemas import PasswordChange, RefreshTokenPayload, Token, UserProfileUpdate, UserRead, UserRegister
from app.db.db import get_db
from app.db.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def _create_token(
    *,
    subject: str,
    token_type: str,
    token_version: int,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "ver": token_version,
        "exp": now + expires_delta,
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(*, subject: str, token_version: int) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        token_version=token_version,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(*, subject: str, token_version: int) -> str:
    return _create_token(
        subject=subject,
        token_type="refresh",
        token_version=token_version,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_token_response(user: User) -> Token:
    serialized_user = UserRead.model_validate(user)
    return Token(
        access_token=create_access_token(subject=user.username, token_version=user.token_version),
        refresh_token=create_refresh_token(subject=user.username, token_version=user.token_version),
        token_type="bearer",
        user=serialized_user,
    )


def _auth_exception(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": code, "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_token(token: str, *, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        if expected_type == "access":
            raise _auth_exception("tokenExpiredException", "Access token expired")
        raise _auth_exception("refreshTokenExpired", "Refresh token expired")
    except JWTError:
        raise _auth_exception("invalidToken", "Invalid token")

    if payload.get("type") != expected_type:
        raise _auth_exception("invalidTokenType", "Invalid token type")
    return payload


def _user_from_payload(db: Session, payload: dict) -> User:
    username = payload.get("sub")
    token_version = payload.get("ver")
    if not username:
        raise _auth_exception("invalidToken", "Invalid token payload")

    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        raise _auth_exception("notAuthenticated", "Not authenticated")
    if token_version != user.token_version:
        raise _auth_exception("tokenRevoked", "Token is no longer valid")
    return user


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    payload = _decode_token(token, expected_type="access")
    return _user_from_payload(db, payload)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        last_name=payload.last_name,
        first_name=payload.first_name,
        middle_name=payload.middle_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_token_response(user)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return build_token_response(user)


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    payload: RefreshTokenPayload,
    db: Session = Depends(get_db),
):
    decoded = _decode_token(payload.refresh_token, expected_type="refresh")
    user = _user_from_payload(db, decoded)
    return build_token_response(user)


@router.get("/me", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserRead)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.username is not None and payload.username != current_user.username:
        existing = get_user_by_username(db, payload.username)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Username already exists")
        current_user.username = payload.username

    if payload.email is not None and payload.email != current_user.email:
        existing = get_user_by_email(db, payload.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already exists")
        current_user.email = payload.email

    if payload.last_name is not None:
        current_user.last_name = payload.last_name
    if payload.first_name is not None:
        current_user.first_name = payload.first_name
    if "middle_name" in payload.model_fields_set:
        current_user.middle_name = payload.middle_name
    if payload.default_page_size is not None:
        current_user.default_page_size = payload.default_page_size
    if payload.auto_refresh_seconds is not None:
        current_user.auto_refresh_seconds = payload.auto_refresh_seconds
    if payload.default_language is not None:
        current_user.default_language = payload.default_language

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password must differ from current password")

    current_user.hashed_password = hash_password(payload.new_password)
    current_user.token_version += 1
    db.commit()
    return None
