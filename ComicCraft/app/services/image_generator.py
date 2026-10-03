import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

from app.config import get_settings


def _safe_name(
    prompt: str,
    panel_number: int | None = None,
) -> str:

    digest = hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()[:12]

    if panel_number is not None:
        prefix = f"panel_{panel_number}_"
    else:
        prefix = "image_"

    return f"{prefix}{digest}.png"


def _generate_hf(
    prompt: str,
    output_path: Path,
) -> str:

    from huggingface_hub import InferenceClient

    settings = get_settings()

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is not configured. "
            "Add it to .env."
        )

    client = InferenceClient(
        provider="auto",
        api_key=settings.hf_token,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )

    image.save(output_path)

    return str(output_path)


def _generate_local(
    prompt: str,
    output_path: Path,
) -> str:

    try:

        import torch
        from diffusers import DiffusionPipeline

    except ImportError as exc:

        raise RuntimeError(
            "Local image generation requires "
            "torch and diffusers. "
            "Install requirements-local-image.txt."
        ) from exc

    settings = get_settings()

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    pipe = DiffusionPipeline.from_pretrained(
        settings.local_image_model,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt,
        num_inference_steps=max(
            1,
            settings.image_steps,
        ),
        width=settings.image_width,
        height=settings.image_height,
    )

    image = result.images[0]

    image.save(output_path)

    return str(output_path)


def _placeholder(
    prompt: str,
    output_path: Path,
) -> str:

    settings = get_settings()

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (
            20,
            20,
            settings.image_width - 20,
            settings.image_height - 20,
        ),
        outline="black",
        width=4,
    )

    draw.text(
        (45, 45),
        "ComicCraft",
        fill="black",
    )

    draw.text(
        (45, 100),
        prompt[:500],
        fill="black",
    )

    image.save(output_path)

    return str(output_path)


def generate_image(
    prompt: str,
    panel_number: int | None = None,
) -> str:

    settings = get_settings()

    output_path = (
        settings.panels_dir
        / _safe_name(
            prompt,
            panel_number,
        )
    )

    # Don't regenerate identical prompts.
    if output_path.exists():
        return str(output_path)

    provider = (
        settings.image_provider
        .lower()
        .strip()
    )

    if provider == "hf":

        return _generate_hf(
            prompt,
            output_path,
        )

    if provider == "local":

        return _generate_local(
            prompt,
            output_path,
        )

    if provider == "placeholder":

        return _placeholder(
            prompt,
            output_path,
        )

    raise RuntimeError(
        f"Unsupported IMAGE_PROVIDER: "
        f"{settings.image_provider}"
    )