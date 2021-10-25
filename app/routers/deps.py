from datetime import timedelta, datetime
from typing import Optional, Type, Dict

from fastapi import HTTPException, Depends, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.query_utils import Q

from app.core import settings
from app.db.models import User
from app.db.schemas import QueryParam

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await User.filter(uid=username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user = await User.filter(id=user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="User is not admin")
    return current_user


def default_query_params(per_page: int = Query(10, alias="itemsPerPage"), page: int = Query(1),
                         search: str = Query(None, alias="search"),
                         sort: str = Query('id', alias="sortBy[]"), sort_desc: bool = Query(True, alias="sortDesc[]")):
    if sort_desc:
        sort = "-" + sort
    if per_page == -1:
        limit = 0
        offset = 0
    else:
        limit = per_page
        offset = per_page * (page - 1)
    query_params = QueryParam(limit=limit, offset=offset, search=search, sort=sort)
    return query_params


class Paginator:
    def __init__(self, model: Type[Model], params: QueryParam, scheme: PydanticModel):
        self.model = model
        self.scheme = scheme
        self.params: QueryParam = params
        self.search_fields: list = []
        self.filters: Dict = {}

    async def get_data(self):
        if self.filters:
            try:
                queryset = self.model.filter(**self.filters)
            except:
                raise Exception("Check filters")
        else:
            queryset = self.model.all().model
        q = Q()
        if self.params.search and self.search_fields:
            for i in self.search_fields:
                q = q | Q(**{f'{i}__icontains': self.params.search})
        queryset = queryset.filter(q)
        count = await queryset.filter().count()
        data = await self.scheme.from_queryset(
            queryset.filter().order_by(self.params.sort).limit(self.params.limit).offset(self.params.offset)
        )
        return {
            "data": data,
            "count": count
        }
