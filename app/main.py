from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from .core import settings
from .routers import api

app = FastAPI()
app.include_router(api.router, prefix='/api')


@app.on_event("startup")
async def on_startup():
    pass


@app.on_event('shutdown')
async def on_shutdown():
    pass


@app.get('/')
async def main():
    return {'hello': 'world'}


register_tortoise(
    app,
    db_url=settings.DB_URL,
    modules={"models": ["app.db.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
