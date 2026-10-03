import json
import re

from google import genai
from google.genai import types
from app.config import get_settings


def _client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"```$",
            "",
            text,
        ).strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}|\[.*\]",
            text,
            re.DOTALL,
        )

        if not match:
            raise ValueError(
                "Gemini returned invalid JSON."
            )

        return json.loads(
            match.group(0)
        )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[dict]:

    settings = get_settings()

    # DEMO MODE
    # This avoids Gemini API calls during the demo.
    if settings.demo_mode:
        return [
            {
                "panel_number": i,
                "title": f"Demo Panel {i}",
                "scene_description": (
                    f"{character_name} continues the adventure "
                    f"in {setting}."
                ),
                "image_prompt": (
                    f"Comic book illustration of {character_name} "
                    f"in {setting}, panel {i}, "
                    f"{art_style}, dramatic lighting, "
                    f"colorful comic style."
                ),
            }
            for i in range(1, settings.max_panels + 1)
        ]

    # NORMAL GEMINI MODE
    panel_count = settings.max_panels

    prompt = f"""
You are a professional comic story planner.

Create a coherent {panel_count}-panel comic outline.

Story idea:

{story_prompt}

Main character:

{character_name}

Setting:

{setting}

Tone:

{tone}

Art style:

{art_style}

The story must have a clear beginning,
development, conflict or important event,
and ending.

Return ONLY valid JSON.

Required JSON format:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "Short title",
      "scene_description": "Visual description",
      "image_prompt": "Detailed image generation prompt"
    }}
  ]
}}

There must be exactly {panel_count} panels.

Rules:

1. panel_number must be 1 through {panel_count}.
2. Every panel must continue the same story.
3. Keep the main character visually consistent.
4. Keep the setting consistent.
5. image_prompt must describe the actual scene.
6. Do not include markdown.
7. Do not include explanations outside JSON.
"""

    response = _client().models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=5000,
            response_mime_type="application/json",
        ),
    )

    data = _extract_json(
        response.text or ""
    )

    if isinstance(data, dict):
        panels = data.get("panels")
    else:
        panels = data

    if not isinstance(panels, list):
        raise ValueError(
            "Gemini did not return a panel list."
        )

    if len(panels) != panel_count:
        raise ValueError(
            f"Expected {panel_count} panels, "
            f"but Gemini returned {len(panels)}."
        )

    return panels