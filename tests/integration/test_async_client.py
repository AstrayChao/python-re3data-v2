"""Integration tests for the asynchronous client against a mocked transport."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from re3data._client import AsyncClient, ReturnType
from re3data._exceptions import RepositoryNotFoundError
from re3data._resources import Repository, RepositorySummary


@pytest.fixture
def client(mock_transport: httpx.MockTransport) -> AsyncClient:
    return AsyncClient(transport=mock_transport)


class TestAsyncGet:
    def test_returns_dataclass(self, client: AsyncClient) -> None:
        repository = asyncio.run(client.repositories.get("r3d100012417"))
        assert isinstance(repository, Repository)
        assert repository.id == "r3d100012417"

    def test_returns_dict(self, client: AsyncClient) -> None:
        payload = asyncio.run(client.repositories.get("r3d100012417", return_type=ReturnType.DICT))
        assert payload["identifiers"]["re3data"] == "r3d100012417"  # type: ignore[index]

    def test_not_found_raises(self, client: AsyncClient) -> None:
        with pytest.raises(RepositoryNotFoundError):
            asyncio.run(client.repositories.get("r3d999999999"))


class TestAsyncList:
    def test_list_with_query(self, client: AsyncClient) -> None:
        summaries = asyncio.run(client.repositories.list(query="UCL"))
        assert all(isinstance(summary, RepositorySummary) for summary in summaries)

    def test_list_count(self, client: AsyncClient) -> None:
        count = asyncio.run(client.repositories.list(query="UCL", count=True))
        assert count == 11

    def test_list_without_query_hits_upstream_500(self, client: AsyncClient) -> None:
        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(client.repositories.list())
