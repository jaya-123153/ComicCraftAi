from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from app.config import get_settings


def _fit_image(
    path: str,
    max_width: float,
    max_height: float,
) -> tuple[float, float]:

    with Image.open(path) as img:

        width, height = img.size

    scale = min(
        max_width / width,
        max_height / height,
    )

    return (
        width * scale,
        height * scale,
    )


def _find_unicode_font() -> str | None:

    candidates = [
        Path(
            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans.ttf"
        ),
        Path(
            "/usr/share/fonts/dejavu/"
            "DejaVuSans.ttf"
        ),
        Path(
            "C:/Windows/Fonts/arial.ttf"
        ),
        Path(
            "C:/Windows/Fonts/seguisym.ttf"
        ),
    ]

    for path in candidates:

        if path.exists():
            return str(path)

    return None


def save_pdf(
    layout: list[dict],
) -> str:

    settings = get_settings()

    filename = (
        "comic_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )
        + ".pdf"
    )

    output = (
        settings.exports_dir
        / filename
    )

    pdf = FPDF(
        unit="mm",
        format="A4",
    )

    unicode_font = _find_unicode_font()

    if unicode_font:

        pdf.add_font(
            "ComicCraftUnicode",
            "",
            unicode_font,
        )

        pdf.add_font(
            "ComicCraftUnicode",
            "B",
            unicode_font,
        )

        pdf.add_font(
            "ComicCraftUnicode",
            "I",
            unicode_font,
        )

    font_name = (
        "ComicCraftUnicode"
        if unicode_font
        else "Helvetica"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # Title
        pdf.set_font(
            font_name,
            "B",
            18,
        )

        pdf.multi_cell(
            0,
            10,
            (
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            ),
        )

        # Image
        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            width, height = _fit_image(
                str(image_path),
                175,
                105,
            )

            x = (
                210 - width
            ) / 2

            pdf.image(
                str(image_path),
                x=x,
                y=35,
                w=width,
                h=height,
            )

        pdf.set_y(145)

        # Scene description
        pdf.set_font(
            font_name,
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.get(
                "scene_description",
                "",
            ),
        )

        pdf.ln(2)

        # Caption
        if panel.get("caption"):

            pdf.set_font(
                font_name,
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                "Caption: "
                + panel["caption"],
            )

        # Narration
        if panel.get("narration"):

            pdf.set_font(
                font_name,
                "",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                "Narration: "
                + panel["narration"],
            )

        # Dialogue
        for line in panel.get(
            "dialogue",
            [],
        ):

            pdf.multi_cell(
                0,
                6,
                "Dialogue: "
                + str(line),
            )

    pdf.output(
        str(output)
    )

    return str(output)