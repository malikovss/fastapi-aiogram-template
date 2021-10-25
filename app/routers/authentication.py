from datetime import timedelta

from fastapi import HTTPException, status, APIRouter

from app.core import settings
from app.db.schemas import LoginForm
from .deps import authenticate_user, create_access_token

router = APIRouter()


@router.post('/token')
async def get_token(form: LoginForm):
    user = await authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"token": access_token, "token_type": "bearer"}
