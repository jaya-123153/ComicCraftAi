import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


settings = get_settings()


logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )
)


app = FastAPI(
    title="ComicCraft",
    version="1.0.0",
    description="AI Comic Story Creator using Gemini and image generation.",
)


app.mount(
    "/static",
    StaticFiles(directory=settings.static_dir),
    name="static",
)


app.include_router(router)