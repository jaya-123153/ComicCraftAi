from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Gemini
    gemini_api_key: str | None = None
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-3.1-pro-preview"
    demo_mode: bool = True

    # Hugging Face
    hf_token: str | None = None
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"

    # Image provider:
    # hf          = Hugging Face hosted generation
    # local       = local Diffusers
    # placeholder = development-only placeholder
    image_provider: str = "hf"

    local_image_model: str = (
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    # Application
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "info"

    # Comic
    max_panels: int = 5
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 4

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings