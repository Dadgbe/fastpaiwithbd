from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

@app.get("/")
async def root():
    return {"message": "Achievement API"}