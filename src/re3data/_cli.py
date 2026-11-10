"""python-re3data-v2 command line interface."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated

from rich.console import Console

import re3data
from re3data._client import ReturnType
from re3data._exceptions import RepositoryNotFoundError

logger = logging.getLogger(__name__)

try:
    import typer
except ImportError:  # pragma: no cover - depends on optional extra
    logger.error("`typer` is missing. Please run 'pip install python-re3data-v2[cli]' to use the CLI.")
    sys.exit(1)

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(no_args_is_help=True, context_settings=CONTEXT_SETTINGS)
repositories_app = typer.Typer(no_args_is_help=True)
app.add_typer(repositories_app, name="repository")


def _version_callback(show_version: bool) -> None:
    # Ref: https://typer.tiangolo.com/tutorial/options/version/
    if show_version:
        console.print(re3data.__version__)
        raise typer.Exit(code=0)


def _write_to_file(response: object, outfile: Path | None) -> None:
    """Write the given response to the specified file, asking before overwriting."""
    if outfile and outfile.exists():
        overwrite = typer.confirm(f"{outfile} already exists. Do you want to overwrite it?")
        if not overwrite:
            return
    if outfile:
        outfile.write_text(str(response), encoding="utf-8")


@app.callback(context_settings=CONTEXT_SETTINGS)
def callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Show python-re3data-v2 version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """python-re3data-v2: the Pythonic client for the re3data API (v40, schema 4.0)."""


@repositories_app.command("list")
def list_repositories(
    query: Annotated[
        str | None,
        typer.Option(
            help="A query to filter the results. If provided, only repositories matching the query will be returned."
        ),
    ] = None,
    return_type: ReturnType = ReturnType.DATACLASS,
    count: bool = False,
    outfile: Annotated[
        Path | None,
        typer.Option(
            file_okay=True,
            dir_okay=False,
            writable=True,
        ),
    ] = None,
) -> None:
    """List the metadata of repositories in the re3data API."""
    response = re3data.repositories.list(query, return_type, count)
    _write_to_file(response, outfile)
    console.print(response)


@repositories_app.command("get")
def get_repository(
    repository_id: Annotated[
        str,
        typer.Argument(help="The identifier of the repository to retrieve, e.g. 'r3d100012417'."),
    ],
    return_type: ReturnType = ReturnType.DATACLASS,
    outfile: Annotated[
        Path | None,
        typer.Option(
            file_okay=True,
            dir_okay=False,
            writable=True,
        ),
    ] = None,
) -> None:
    """Get the metadata of a specific repository."""
    try:
        response = re3data.repositories.get(repository_id, return_type)
    except RepositoryNotFoundError as error:
        console.print(str(error), style="bold red")
        raise typer.Exit(code=1) from error
    _write_to_file(response, outfile)
    console.print(response)
