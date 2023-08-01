__import__('os').environ['TZ'] = 'UTC'

from src.on import on_start, on_shutdown



import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src import redis
from src.auth.router import router as auth_router
from src.config import app_configs, settings
from src.database import database
from sentry_sdk.integrations.fastapi import FastApiIntegration
app = FastAPI(**app_configs)


@app.on_event("startup")
async def lifespan():
    # Startup
    await on_start()


@app.on_event("shutdown")
async def shutdown():
    await on_shutdown()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration()]
    )
    sentry_sdk.capture_message("run server")


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:

    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
