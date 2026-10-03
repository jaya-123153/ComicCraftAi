from pathlib import Path


def build_comic_layout(
    story_panels: list[dict],
    image_paths: list[str],
) -> list[dict]:

    if len(story_panels) != len(image_paths):

        raise ValueError(
            "Every story panel must have exactly "
            "one image."
        )

    layout = []

    for panel, image_path in zip(
        story_panels,
        image_paths,
    ):

        filename = Path(
            image_path
        ).name

        layout.append(
            {
                "panel_number": panel[
                    "panel_number"
                ],
                "title": panel["title"],
                "image_path": image_path,
                "image_url": (
                    "/static/panels/"
                    + filename
                ),
                "scene_description": panel[
                    "scene_description"
                ],
                "image_prompt": panel[
                    "image_prompt"
                ],
                "caption": panel.get(
                    "caption",
                    "",
                ),
                "narration": panel.get(
                    "narration",
                    "",
                ),
                "dialogue": panel.get(
                    "dialogue",
                    [],
                ),
            }
        )

    return layout