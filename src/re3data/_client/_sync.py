"""The synchronous client to interact with the re3data v40 API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

import httpx

from re3data._client.base import (
    BaseClient,
    Endpoint,
    ResourceType,
    ReturnType,
    _dispatch_return_type,
    build_query_params,
    is_valid_return_type,
)
from re3data._exceptions import RepositoryNotFoundError
from re3data._response import Response, _build_response

if TYPE_CHECKING:
    from re3data._resources import Repository, RepositorySummary

logger = logging.getLogger(__name__)


def log_response(response: httpx.Response) -> None:
    """Log method, URL and status code of an HTTP response on the debug level."""
    logger.debug("[http] Response: %s %s - Status %s", response.request.method, response.request.url, response.status_code)


class RepositoryManager:
    """A manager for interacting with the repositories endpoints."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list(
        self,
        query: str | None = None,
        return_type: ReturnType = ReturnType.DATACLASS,
        count: bool = False,
        filters: dict[str, str | list[str] | tuple[str, ...]] | None = None,
    ) -> list[RepositorySummary] | Response | list[dict] | str | int:
        """List the metadata of repositories in the re3data API.

        Args:
            query: A query string to filter the results. If provided, only
                repositories matching the query will be returned.
            return_type: The desired return type for the API resource.
                Defaults to `ReturnType.DATACLASS`.
            count: Whether to return the total number of matching items
                instead of a list of repositories.
            filters: Optional facet filters for the v40 endpoint, e.g.
                ``{"countries": ["DEU", "NZL"], "dataAccess": "open"}``.

        Returns:
            Depending on the `return_type`, this is a list of
            RepositorySummary objects, an HTTP response, a dictionary/JSON/CSV
            representation, the original XML, or the count of repositories.

        Raises:
            ValueError: If an invalid `return_type` is provided.
            httpx.HTTPStatusError: If the server returned an error status code >= 500.
        """
        is_valid_return_type(return_type)
        params = build_query_params(query, filters)
        response = self._client._request(Endpoint.REPOSITORY_LIST.value, params)
        return _dispatch_return_type(response, ResourceType.REPOSITORY_LIST, return_type, count)

    def get(self, repository_id: str, return_type: ReturnType = ReturnType.DATACLASS) -> Repository | Response | dict | str:
        """Get the metadata of a specific repository.

        Args:
            repository_id: The identifier of the repository to retrieve,
                e.g. "r3d100012417".
            return_type: The desired return type for the API resource.
                Defaults to `ReturnType.DATACLASS`.

        Returns:
            Depending on the `return_type`, this is a Repository object, an
            HTTP response, a dictionary/JSON/CSV representation or the
            original XML.

        Raises:
            ValueError: If an invalid `return_type` is provided.
            httpx.HTTPStatusError: If the server returned an error status code >= 500.
            RepositoryNotFoundError: If no repository with the given ID is found.
        """
        is_valid_return_type(return_type)
        response = self._client._request(Endpoint.REPOSITORY.value.format(repository_id=repository_id))
        if response.status_code == httpx.codes.NOT_FOUND:
            raise RepositoryNotFoundError(f"No repository with id '{repository_id}' available at {response.url}.")
        return _dispatch_return_type(response, ResourceType.REPOSITORY, return_type)


class Client(BaseClient):
    """A client that interacts with the re3data v40 API.

    Examples:
        >>> client = Client()
        >>> client.repositories.get("r3d100012417")
        Repository(identifiers=Identifiers(re3data='r3d100012417', doi='https://doi.org/10.17616/R34F41'), ...)
        >>> client.repositories.list(query="biosharing")
        [RepositorySummary(id='r3d100010142', ...)]
    """

    _client: httpx.Client

    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        """Initialize the client.

        Args:
            transport: An optional custom httpx transport, e.g. for testing.
        """
        super().__init__(httpx.Client, transport)
        self._client.event_hooks["response"] = [log_response]
        self._repository_manager: RepositoryManager = RepositoryManager(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._client.close()

    def _request(self, path: str, query_params: list[tuple[str, str]] | None = None) -> Response:
        """Send an HTTP GET request to the specified API endpoint.

        Raises:
            httpx.HTTPStatusError: If the server returned an error status code >= 500.
        """
        http_response = self._client.get(path, params=query_params)
        if http_response.is_server_error:
            http_response.raise_for_status()
        return _build_response(http_response)

    @property
    def repositories(self) -> RepositoryManager:
        """The repository manager of this client."""
        return self._repository_manager
