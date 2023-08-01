from typing import Any

from pydantic import BaseSettings, RedisDsn, root_validator

from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: RedisDsn

    SITE_DOMAIN: str = "myapp.com"

    ENVIRONMENT: Environment = Environment.PRODUCTION

    SENTRY_DSN: str | None

    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None
    CORS_HEADERS: list[str]

    APP_VERSION: str = "1"

    class Config:
        env_file = ".env"

    BROKER_URL: str

    CELERY_RESULT_BACKEND: str
    CELERY_ENABLE_UTC = True

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']

    CELERY_ROUTES = {
        "hello_task": {
            "queue": "hello"
        }
    }
    CELERY_RESULT_DB_TABLENAMES = {
        'task': 'rfq_tasks',
        'group': 'rfq_task_group',
    }
    CELERY_RESULT_EXTENDED = True

    CELERY_IMPORTS = ['src.tasks']
    @root_validator(skip_on_failure=True)
    def validate_sentry_non_local(cls, data: dict[str, Any]) -> dict[str, Any]:
        if data["ENVIRONMENT"].is_deployed and not data["SENTRY_DSN"]:
            raise ValueError("Sentry is not set")

        return data


settings = Config()

app_configs: dict[str, Any] = {"title": "App API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = "/v1/asset"  # hide docs
