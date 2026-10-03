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


def generate_story(
    outline: list[dict],
    character_name: str,
    tone: str,
) -> list[dict]:

    settings = get_settings()

    outline_json = json.dumps(
        outline,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are a professional comic book writer.

Expand the following outline into a complete
{settings.max_panels}-panel comic script.

Main character:
{character_name}

Tone:
{tone}

Outline:

{outline_json}

Return ONLY valid JSON.

Required format:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "Panel title",
      "scene_description": "Scene description",
      "image_prompt": "Image prompt",
      "caption": "Short caption",
      "narration": "Narration",
      "dialogue": [
        "Dialogue line"
      ]
    }}
  ]
}}

Rules:

1. Return exactly {settings.max_panels} panels.
2. Preserve panel numbers.
3. Preserve the same character.
4. Maintain story continuity.
5. Caption should be short.
6. Narration should be 1-3 sentences.
7. Dialogue should contain 0-3 short lines.
8. Do not add extra panels.
9. Do not use markdown.
10. Do not add explanations outside JSON.
"""

    response = _client().models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=7000,
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
            "Gemini did not return story panels."
        )

    if len(panels) != settings.max_panels:
        raise ValueError(
            f"Expected {settings.max_panels} story panels, "
            f"but received {len(panels)}."
        )

    normalized = []

    for panel in panels:

        normalized.append(
            {
                "panel_number": int(
                    panel["panel_number"]
                ),
                "title": str(
                    panel["title"]
                ),
                "scene_description": str(
                    panel["scene_description"]
                ),
                "image_prompt": str(
                    panel["image_prompt"]
                ),
                "caption": str(
                    panel.get("caption", "")
                ),
                "narration": str(
                    panel.get("narration", "")
                ),
                "dialogue": [
                    str(x)
                    for x in panel.get(
                        "dialogue",
                        [],
                    )
                ],
            }
        )

    return normalized