"""Integration tests for the synchronous client against a mocked transport."""

from __future__ import annotations

import httpx
import pytest

from re3data._client import Client, ReturnType
from re3data._client.base import build_query_params
from re3data._exceptions import RepositoryNotFoundError
from re3data._resources import Repository, RepositorySummary


@pytest.fixture
def client(mock_transport: httpx.MockTransport) -> Client:
    return Client(transport=mock_transport)


class TestGet:
    def test_returns_dataclass_by_default(self, client: Client) -> None:
        repository = client.repositories.get("r3d100012417")
        assert isinstance(repository, Repository)
        assert repository.id == "r3d100012417"

    def test_returns_dict(self, client: Client) -> None:
        payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)
        assert payload["identifiers"]["re3data"] == "r3d100012417"  # type: ignore[index]

    def test_returns_json_string(self, client: Client) -> None:
        payload = client.repositories.get("r3d100012417", return_type=ReturnType.JSON)
        assert '"r3d100012417"' in payload  # type: ignore[operator]

    def test_returns_raw_xml(self, client: Client) -> None:
        payload = client.repositories.get("r3d100012417", return_type=ReturnType.XML)
        assert payload.startswith("<?xml")  # type: ignore[union-attr]

    def test_returns_response_object(self, client: Client) -> None:
        response = client.repositories.get("r3d100012417", return_type=ReturnType.RESPONSE)
        assert response.status_code == 200

    def test_returns_csv(self, client: Client) -> None:
        payload = client.repositories.get("r3d100012417", return_type=ReturnType.CSV)
        assert payload.splitlines()[0] == "id,doi,name,href"  # type: ignore[union-attr]

    def test_not_found_raises(self, client: Client) -> None:
        with pytest.raises(RepositoryNotFoundError):
            client.repositories.get("r3d999999999")

    def test_invalid_return_type_raises(self, client: Client) -> None:
        with pytest.raises(ValueError, match="Invalid value for `return_type`"):
            client.repositories.get("r3d100012417", return_type="dict")  # type: ignore[arg-type]


class TestList:
    def test_list_with_query(self, client: Client) -> None:
        summaries = client.repositories.list(query="UCL")
        assert isinstance(summaries, list)
        assert all(isinstance(summary, RepositorySummary) for summary in summaries)
        assert summaries[0].id == "r3d100013090"

    def test_list_with_filters(self, client: Client) -> None:
        summaries = client.repositories.list(filters={"countries": ["NZL", "CAN"], "dataAccess": "open"})
        assert len(summaries) == 11

    def test_list_count(self, client: Client) -> None:
        count = client.repositories.list(query="UCL", count=True)
        assert count == 11

    def test_list_without_query_hits_upstream_500(self, client: Client) -> None:
        # mirrors the current upstream behaviour of the unfiltered full list
        with pytest.raises(httpx.HTTPStatusError):
            client.repositories.list()

    def test_list_dict(self, client: Client) -> None:
        payload = client.repositories.list(query="UCL", return_type=ReturnType.DICT)
        assert payload[0]["name"] == "UCL Research Data Repository"  # type: ignore[index]


class TestQueryParams:
    def test_query_and_filters_serialize_as_repeated_bracket_params(self) -> None:
        params = build_query_params("WDCC", {"countries": ["DEU", "NZL"], "dataAccess": "open"})
        assert params == [
            ("query", "WDCC"),
            ("countries[]", "DEU"),
            ("countries[]", "NZL"),
            ("dataAccess[]", "open"),
        ]

    def test_empty_query_is_omitted(self) -> None:
        assert build_query_params(None, None) == []
        assert build_query_params("", None) == []
