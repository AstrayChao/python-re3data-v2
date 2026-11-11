"""End-to-end smoke tests against the live re3data v40 API.

Run with: uv run pytest -m e2e
"""

from __future__ import annotations

import httpx
import pytest

from re3data import Client, ReturnType

pytestmark = pytest.mark.e2e


def test_live_get_repository() -> None:
    with Client() as client:
        repository = client.repositories.get("r3d100012417")
    assert repository.id == "r3d100012417"
    assert repository.repositoryName is not None


def test_live_get_repository_dict() -> None:
    with Client() as client:
        payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)
    assert payload["identifiers"]["re3data"] == "r3d100012417"  # type: ignore[index]


def test_live_list_with_query() -> None:
    with Client() as client:
        summaries = client.repositories.list(query="UCL")
    assert summaries, "expected at least one UCL repository"


def test_live_list_without_query_is_currently_broken_upstream() -> None:
    with Client() as client, pytest.raises(httpx.HTTPStatusError):
        client.repositories.list()


def test_live_v1_discovery_with_v40_details() -> None:
    # workaround profile while the v40 list endpoint is down upstream
    with Client(list_api_version="v1") as client:
        summaries = client.repositories.list()
        assert len(summaries) > 3000, "expected the full v1 index"
        repository = client.repositories.get(summaries[0].id)
    assert repository.id == summaries[0].id
    assert repository.identifiers.doi  # details still parsed as schema 4.0


def test_live_v1_detail_converts_schema_22() -> None:
    with Client(api_version="v1") as client:
        repository = client.repositories.get("r3d100012417")
    assert repository.id == "r3d100012417"
    assert repository.repositoryName.value == "UCL Discovery"

