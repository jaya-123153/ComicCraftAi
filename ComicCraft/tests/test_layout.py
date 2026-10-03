from app.services.layout_builder import (
    build_comic_layout,
)


def test_build_layout():

    story = [
        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description":
                "A fox enters a forest.",
            "image_prompt":
                "fox in forest",
            "caption":
                "Morning.",
            "narration":
                "Lumi walks forward.",
            "dialogue": [
                "Let's go!"
            ],
        }
    ]

    result = build_comic_layout(
        story_panels=story,
        image_paths=[
            "/tmp/comiccraft/static/"
            "panels/panel.png"
        ],
    )

    assert (
        result[0]["panel_number"]
        == 1
    )

    assert (
        result[0]["image_url"]
        .endswith(
            "/static/panels/panel.png"
        )
    )