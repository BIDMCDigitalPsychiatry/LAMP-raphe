from importlib.resources import files

import yaml


SCHEMA_NAMES = {
    "study",
    "episodes",
    "participants",
    "gps",
    "accelerometer",
    "screen",
    "source_intervals",
    "clinical",
    "clinical_windows",
}


def load_schema(name: str) -> dict:
    """
    Load one RAPHE canonical schema specification.
    """

    if name not in SCHEMA_NAMES:
        raise ValueError(
            f"Unknown RAPHE schema: {name}. "
            f"Available: {sorted(SCHEMA_NAMES)}"
        )

    path = (
        files("raphe")
        / "schema_specs"
        / f"{name}.yaml"
    )

    with path.open("r") as f:
        return yaml.safe_load(f)


def list_schemas() -> list[str]:
    return sorted(SCHEMA_NAMES)
