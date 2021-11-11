import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from rebalancing.config import Config
from rebalancing.utils.password import verify_password, get_hashed_password
from rebalancing.exceptions import CredentialException


# fastapi 비밀번호가 담긴 환경변수명
PASSWORD_ENV = Config.get('fastapi', 'PASSWORD_ENV')

# ADMIN USER 한개만 존재
ADMIN_USER = {
    "username": Config.get('fastapi', 'USERNAME'),
    "hashed_password": get_hashed_password(PASSWORD_ENV),
}

# api secret_key
SECRET_KEY = Config.get('fastapi', 'SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = Config.get_int('fastapi', 'ACCESS_TOKEN_EXPIRE_MINUTES')
ALGORITHM = "HS256"


# BaseModels
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


class LoginManager(OAuth2PasswordBearer):
    """ Name Aliasing """


# Auth Router
r = APIRouter(prefix='/auth',
              tags=['auth', ])

# set login manager
manager = LoginManager(tokenUrl="/auth/token")


def get_user(username: str) -> Optional[UserInDB]:
    if username == ADMIN_USER['username']:
        return UserInDB(**ADMIN_USER)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
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


async def login_required(token: str = Depends(manager)) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise CredentialException

        # set token data
        token_data = TokenData(username=username)

    except JWTError:
        raise CredentialException

    return token_data


async def get_current_user(token_data: TokenData = Depends(login_required)):
    user = get_user(username=token_data.username)

    if user is None:
        raise CredentialException

    return user


@r.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@r.get("/current-user", response_model=User)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# for import
__all__ = [
    'login_required',
]
