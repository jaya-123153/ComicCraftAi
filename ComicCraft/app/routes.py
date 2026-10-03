import logging
from pathlib import Path
from urllib.parse import quote

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import (
    ImageRequest,
    PromptRequest,
)

from app.services.gemini_flash import (
    generate_outline,
)

from app.services.gemini_pro import (
    generate_story,
)

from app.services.image_generator import (
    generate_image,
)

from app.services.layout_builder import (
    build_comic_layout,
)

from app.services.exporters import (
    save_pdf,
)


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


def _generate_comic(
    data: PromptRequest,
) -> tuple[list[dict], str]:

    # Step 1
    outline = generate_outline(
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
    )

    # Step 2
    story = generate_story(
        outline=outline,
        character_name=data.character_name,
        tone=data.tone,
    )

    # Step 3
    image_paths = []

    for panel in story:

        image_prompt = (
            f"{panel['image_prompt']}, "
            f"{data.art_style}, "
            "clean comic composition, "
            "professional comic illustration, "
            "consistent character design"
        )

        image_path = generate_image(
            prompt=image_prompt,
            panel_number=panel["panel_number"],
        )

        image_paths.append(image_path)

    # Step 4
    layout = build_comic_layout(
        story_panels=story,
        image_paths=image_paths,
    )

    # Step 5
    pdf_path = save_pdf(layout)

    return layout, pdf_path


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_form(
    request: Request,

    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_path = _generate_comic(data)

        pdf_url = (
            "/download-pdf?path="
            + quote(pdf_path)
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
            },
        )

    except Exception as exc:

        logger.exception(
            "Comic generation failed."
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_json(
    data: PromptRequest,
):

    try:

        layout, pdf_path = _generate_comic(data)

        pdf_url = (
            "/download-pdf?path="
            + quote(pdf_path)
        )

        return {
            "success": True,
            "panels": layout,
            "pdf_url": pdf_url,
        }

    except Exception as exc:

        logger.exception(
            "JSON comic generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/test-image")
async def test_image(
    data: ImageRequest,
):

    try:

        path = generate_image(
            prompt=data.prompt
        )

        settings = get_settings()

        filename = Path(path).name

        image_url = (
            "/static/panels/"
            + filename
        )

        return {
            "success": True,
            "image_url": image_url,
            "provider": settings.image_provider,
        }

    except Exception as exc:

        logger.exception(
            "Image test failed."
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/download-pdf")
async def download_pdf(
    path: str,
):

    settings = get_settings()

    requested = Path(path).resolve()
    export_root = settings.exports_dir.resolve()

    # Security:
    # Make sure requested file stays inside exports folder.
    if requested.parent != export_root:
        raise HTTPException(
            status_code=400,
            detail="Invalid export path.",
        )

    if not requested.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    if requested.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    return FileResponse(
        requested,
        media_type="application/pdf",
        filename=requested.name,
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/health")
async def health():

    settings = get_settings()

    return {
        "status": "ok",
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
        "image_provider": settings.image_provider,
        "huggingface_configured": bool(
            settings.hf_token
        ),
    }