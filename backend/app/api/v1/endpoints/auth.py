from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
from app.models.models import User
from app.core.security import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    full_name: str
    role: str

@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    user.last_login = datetime.utcnow()
    await db.commit()

    role = user.role if isinstance(user.role, str) else user.role.value
    token = create_access_token({"sub": str(user.id), "role": role})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        username=user.username,
        full_name=user.full_name,
        role=role,
    )

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(payload: ChangePasswordRequest, db: AsyncSession = Depends(get_db)):
    # Simplified - in production use proper auth dependency
    raise HTTPException(501, "Use proper authentication middleware")
