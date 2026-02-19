from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api_v1 import users, achievements, stats

setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(users.router, prefix="/api/v1")
app.include_router(achievements.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Achievement API"}


from app.core.dependencies import LoggingMiddleware
app.add_middleware(LoggingMiddleware)