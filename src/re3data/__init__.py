"""python-re3data-v2: the Pythonic client for the re3data API (v40, schema 4.0)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("python-re3data-v2")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"

from re3data._client import AsyncClient, Client, ReturnType
from re3data._exceptions import Re3dataError, RepositoryNotFoundError
from re3data._resources import Link, Re3Data, Repository, RepositoryList, RepositorySummary
from re3data._response import Response

__all__ = (
    "AsyncClient",
    "Client",
    "Link",
    "Re3Data",
    "Re3dataError",
    "Repository",
    "RepositoryList",
    "RepositoryNotFoundError",
    "RepositorySummary",
    "Response",
    "ReturnType",
    "__version__",
)

_client = Client()
repositories = _client.repositories
