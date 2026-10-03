from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000,
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    )
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


class ImageRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=5,
        max_length=3000,
    )


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: list[str] = []


class ComicResult(BaseModel):
    panels: list[dict]
    pdf_url: str