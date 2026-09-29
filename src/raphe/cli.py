import json
from pathlib import Path

import typer

from raphe.io.study_inventory import (
    run_inventory,
)

app = typer.Typer(
    help=(
        "RAPHE — Reliability-Aware Personalized "
        "Health Phenotyping Engine"
    )
)


@app.command()
def version():
    """Show RAPHE version."""
    typer.echo("RAPHE 0.1.0")


@app.command()
def info():
    """Show the RAPHE processing framework."""
    typer.echo(
        "\n"
        "Observability\n"
        "  -> Feature extraction\n"
        "  -> Analysis-ready features\n"
        "  -> Personal baseline\n"
        "  -> Behavioral deviations\n"
        "  -> Clinical alignment\n"
        "  -> Reliability/degradation\n"
        "  -> Transdiagnostic transportability\n"
    )


@app.command()
def inventory(
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        exists=True,
        readable=True,
    )
):
    """Validate a study and build its canonical inventory."""

    result = run_inventory(
        config
    )

    typer.echo(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
