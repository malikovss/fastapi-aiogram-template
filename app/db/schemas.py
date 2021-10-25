from pydantic import BaseModel


class QueryParam(BaseModel):
    limit: int
    offset: int
    search: str = None
    sort: str


class LoginForm(BaseModel):
    username: str
    password: str
