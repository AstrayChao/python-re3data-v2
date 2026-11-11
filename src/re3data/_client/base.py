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

API_ROOT_URL: str = "https://www.re3data.org/api/"
DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "application/xml; charset=utf-8",
    "User-Agent": f"python-re3data-v2/{__version__}",
}
DEFAULT_TIMEOUT = httpx.Timeout(timeout=10.0)  # timeout in seconds


class APIVersion(StrEnum):
    """The re3data API versions.

    - ``v40`` (current, schema 4.0): detail responses are parsed natively.
    - ``v1`` / ``beta`` (deprecated, schema 2-2): detail responses are parsed
      and *converted* into the schema 4.0 model. Facet filters are not sent
      (v1 ignores them; beta accepts them but both list endpoints share the
      upstream availability of the v40 list).
    The unfiltered repository list currently only works on ``v1``; the v40 and
    beta list endpoints return HTTP 500 server-side. Pass
    ``list_api_version=APIVersion.V1`` to keep discovery working.
    """

    V40 = "v40"
    V1 = "v1"
    BETA = "beta"


def resolve_api_version(version: APIVersion | str | None, fallback: APIVersion) -> APIVersion:
    """Normalize an optional API version argument, defaulting to ``fallback``.

    Raises:
        ValueError: If the version is not a known :class:`APIVersion`.
    """
    if version is None:
        return fallback
    if isinstance(version, APIVersion):
        return version
    try:
        return APIVersion(str(version).lower())
    except ValueError as error:
        allowed = [item.value for item in APIVersion]
        raise ValueError(f"Invalid API version: {version!r} is not one of {allowed}.") from error


def base_url_for(version: APIVersion) -> str:
    return f"{API_ROOT_URL}{version.value}/"


class Endpoint(StrEnum):
    """The re3data API endpoints (relative to the versioned base URL)."""

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
    """A base class for clients that interact with the re3data API.

    The list and the detail endpoint may target different API versions
    (e.g. list on ``v1`` while details stay on ``v40``), each with its own
    versioned base URL.
    """

    def __init__(
        self,
        client: type[httpx.Client | httpx.AsyncClient],
        *,
        list_base_url: str,
        detail_base_url: str,
        transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._list_base_url = list_base_url
        self._detail_base_url = detail_base_url
        kwargs: dict[str, object] = {
            "base_url": list_base_url,
            "headers": DEFAULT_HEADERS,
            "timeout": DEFAULT_TIMEOUT,
            "follow_redirects": True,
        }
        if transport is not None:
            kwargs["transport"] = transport
        self._client = client(**kwargs)

    def list_url(self, path: str) -> str:
        """Absolute URL of a list-endpoint path under the list API version."""
        return f"{self._list_base_url}{path}"

    def detail_url(self, path: str) -> str:
        """Absolute URL of a detail-endpoint path under the detail API version."""
        return f"{self._detail_base_url}{path}"
