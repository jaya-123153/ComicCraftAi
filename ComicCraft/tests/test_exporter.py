from pathlib import Path

from PIL import Image

from app.config import get_settings
from app.services.exporters import save_pdf


def test_save_pdf():

    settings = get_settings()

    image = (
        settings.panels_dir
        / "test_export.png"
    )

    Image.new(
        "RGB",
        (200, 200),
        "white",
    ).save(image)

    layout = [
        {
            "panel_number": 1,
            "title": "Test",
            "image_path": str(image),
            "scene_description":
                "Test scene",
            "caption":
                "Caption",
            "narration":
                "Narration",
            "dialogue": [
                "Hello"
            ],
        }
    ]

    result = save_pdf(layout)

    assert Path(result).exists()

    assert (
        Path(result).suffix
        == ".pdf"
    )

    Path(result).unlink(
        missing_ok=True
    )

    image.unlink(
        missing_ok=True
    )