import os
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(password_env: str):
    password = os.getenv(password_env, None)

    # assertion
    assert password is not None, "FastAPI 비밀번호를 입력해야합니다."

    # hash
    return pwd_context.hash(password)
