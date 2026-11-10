"""Shared building blocks for the sync and async re3data API clients."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal, overload

import httpx

from re3data import __version__
from re3data._parser import parse_repository, parse_repository_list
from re3data._response import Response
from re3data._serializer import _to_csv, _to_dict, _to_json

if TYPE_CHECKING:
    from re3data._resources import Repository, RepositorySummary

BASE_URL: str = "https://www.re3data.org/api/v40/"
DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/xml; charset=utf-8",
    "User-Agent": f"python-re3data-v2/{__version__}",
}
DEFAULT_TIMEOUT = httpx.Timeout(timeout=10.0)  # timeout in seconds


class Endpoint(StrEnum):
    """The re3data v40 API endpoints."""

    REPOSITORY = "repository/{repository_id}"
    REPOSITORY_LIST = "repositories"


class ResourceType(StrEnum):
    """The type of an API resource."""

    REPOSITORY = "repository"
    REPOSITORY_LIST = "repositories"


class ReturnType(StrEnum):
    """The supported serialization formats of API resources."""

    CSV = "csv"
    DATACLASS = "dataclass"
    DICT = "dict"
    JSON = "json"
    RESPONSE = "response"
    XML = "xml"


def is_valid_return_type(return_type: Any) -> None:
    """Validate that the given return type is a known :class:`ReturnType`.

    Raises:
        ValueError: If the given return type is not one of the allowed types.
    """
    if not isinstance(return_type, ReturnType):
        allowed_types = [return_type.value for return_type in ReturnType]
        raise ValueError(  # noqa: TRY004 - ValueError for compat with the original client
            f"Invalid value for `return_type`: {return_type} is not one of {allowed_types}."
        )


def build_query_params(
    query: str | None = None,
    filters: dict[str, str | list[str] | tuple[str, ...]] | None = None,
) -> list[tuple[str, str]]:
    """Build the query parameters for the list endpoint.

    Args:
        query: An optional search term, sent as the ``query`` parameter.
        filters: Optional facet filters. Keys are the v40 filter names without
            brackets (e.g. ``countries``, ``dataAccess``, ``subjects``); values
            are one value or a sequence of values. They are serialized as
            repeated ``name[]`` parameters, e.g. ``countries[]=NZL``.

    Returns:
        A list of query parameter pairs, ready for ``httpx``.
    """
    params: list[tuple[str, str]] = []
    if query:
        params.append(("query", query))
    for name, raw_values in (filters or {}).items():
        values = (raw_values,) if isinstance(raw_values, str) else raw_values
        params.extend((f"{name}[]", str(value)) for value in values)
    return params


@overload
def _dispatch_return_type(
    response: Response, resource_type: Literal[ResourceType.REPOSITORY], return_type: ReturnType
) -> Repository | Response | dict | str: ...
@overload
def _dispatch_return_type(
    response: Response, resource_type: Literal[ResourceType.REPOSITORY_LIST], return_type: ReturnType, count: bool = False
) -> list[RepositorySummary] | Response | list[dict] | str | int: ...


def _dispatch_return_type(  # noqa: PLR0911 - mirrors the upstream dispatch structure
    response: Response, resource_type: ResourceType, return_type: ReturnType, count: bool = False
) -> Repository | list[RepositorySummary] | Response | dict | list[dict] | str | int:
    """Dispatch a response to the requested return type.

    Args:
        response: The response object.
        resource_type: The type of resource being processed.
        return_type: The desired return type for the API resource.
        count: Whether to return the total number of matching items instead of
            a list of repositories (list endpoint only).

    Returns:
        Depending on the return type: a typed model, the response object, the
            raw XML, a dict/JSON/CSV serialization or the repository count.
    """
    if resource_type is ResourceType.REPOSITORY_LIST and count:
        return response.text.count("<repository>")
    if return_type is ReturnType.RESPONSE:
        return response
    if return_type is ReturnType.XML:
        return response.text

    parsed = (
        parse_repository_list(response.text).repository
        if resource_type is ResourceType.REPOSITORY_LIST
        else parse_repository(response.text)
    )
    if return_type is ReturnType.DATACLASS:
        return parsed
    if return_type is ReturnType.DICT:
        return _to_dict(parsed)
    if return_type is ReturnType.JSON:
        return _to_json(parsed)
    return _to_csv(parsed)


class BaseClient:
    """A base class for clients that interact with the re3data v40 API."""

    def __init__(
        self,
        client: type[httpx.Client | httpx.AsyncClient],
        transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None = None,
    ) -> None:
        kwargs: dict[str, object] = {
            "base_url": BASE_URL,
            "headers": DEFAULT_HEADERS,
            "timeout": DEFAULT_TIMEOUT,
            "follow_redirects": True,
        }
        if transport is not None:
            kwargs["transport"] = transport
        self._client = client(**kwargs)
