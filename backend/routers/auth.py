import logging
import os
from datetime import datetime, timedelta

import jwt
from ..database.utils import execute_query, fetch_query
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

auth = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class RegisterRequest(BaseModel):
    name: str
    phone: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def hash_password(password: str):
    return pwd_context.hash(password)


@auth.post("/register")
def register_user(req: RegisterRequest):
    existing = fetch_query(
        "SELECT * FROM Customer WHERE email = %s OR phone = %s",
        (req.email, req.phone),
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(req.password)

    execute_query(
        """
        INSERT INTO Customer(name, phone, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (req.name, req.phone, req.email, hashed_pw),
    )

    return {"message": "User registered successfully"}


@auth.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = fetch_query(
        """
        SELECT customer_id, name, email, phone, password
        FROM Customer
        WHERE email = %s OR phone = %s
        """,
        (form_data.username, form_data.username),
    )

    if not result:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user = result[0]

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["customer_id"])})

    return TokenResponse(access_token=token)


from fastapi import Header


@auth.get("/me")
def get_current_user(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = fetch_query(
        "SELECT customer_id, name, phone, email FROM Customer WHERE customer_id = %s",
        (user_id,),
    )

    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return data[0]
