from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DEBUG = True
    BOT_TOKEN: str
    DB_URL: str
    HOST: str
    SECRET_KEY: str
    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    ADMIN = 1459259424

    WEBHOOK_PATH: str = None
    WEBHOOK_URL: str = None

    @validator("WEBHOOK_PATH")
    def weebhook_path(cls, v, values: dict) -> str:
        return f"/bot/{values.get('BOT_TOKEN')}"

    @validator("WEBHOOK_URL")
    def weebhook_url(cls, v, values: dict) -> str:
        return f'{values.get("HOST")}/api{values.get("WEBHOOK_PATH")}'

    TIMEZONE = "Asia/Samarkand"


settings = Settings(_env_file=".env")

TORTOISE_ORM = {
    "connections": {"default": settings.DB_URL},
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
