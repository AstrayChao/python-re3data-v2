"""Integration tests for the selectable API versions (v40 / v1 / beta)."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

from re3data import APIVersion, AsyncClient, Client, ReturnType
from re3data._client.base import base_url_for, resolve_api_version

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _versioned_transport() -> httpx.MockTransport:
    """Serve v40 detail + v1 list; v40 list fails like the live upstream."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.startswith("/api/v1/repositories"):
            return httpx.Response(200, text=fixture_text("repositories_v1_list.xml"))
        if path.startswith("/api/v40/repository/"):
            return httpx.Response(200, text=fixture_text("repository_r3d100012417.xml"))
        if path.startswith("/api/v1/repository/"):
            return httpx.Response(200, text=fixture_text("repository_v1_r3d100012417.xml"))
        if path.startswith("/api/beta/repository/"):
            return httpx.Response(200, text=fixture_text("repository_beta_r3d100012417.xml"))
        if path.startswith("/api/v40/repositories"):
            return httpx.Response(500, text="upstream 500")
        return httpx.Response(404)

    return httpx.MockTransport(handler)


class TestResolveAPIVersion:
    def test_defaults_to_fallback(self) -> None:
        assert resolve_api_version(None, APIVersion.V40) is APIVersion.V40

    def test_accepts_strings_and_enum(self) -> None:
        assert resolve_api_version("v1", APIVersion.V40) is APIVersion.V1
        assert resolve_api_version(APIVersion.BETA, APIVersion.V40) is APIVersion.BETA

    def test_rejects_unknown_versions(self) -> None:
        with pytest.raises(ValueError, match="Invalid API version"):
            resolve_api_version("v99", APIVersion.V40)

    def test_base_urls(self) -> None:
        assert base_url_for(APIVersion.V40) == "https://www.re3data.org/api/v40/"
        assert base_url_for(APIVersion.V1) == "https://www.re3data.org/api/v1/"


class TestVersionedClient:
    def test_default_is_v40_and_list_fails_like_upstream(self) -> None:
        with Client(transport=_versioned_transport()) as client:
            with pytest.raises(httpx.HTTPStatusError):
                client.repositories.list()
            repository = client.repositories.get("r3d100012417")
            assert repository.id == "r3d100012417"
            assert repository.identifiers.doi  # schema 4.0 native

    def test_list_via_v1_while_details_stay_on_v40(self) -> None:
        with Client(list_api_version="v1", transport=_versioned_transport()) as client:
            summaries = client.repositories.list()
            assert summaries[0].id == "r3d100000001"
            repository = client.repositories.get("r3d100012417")
            assert repository.identifiers.doi

    def test_full_v1_detail_is_converted_from_22(self) -> None:
        with Client(api_version="v1", transport=_versioned_transport()) as client:
            payload = client.repositories.get("r3d100012417", return_type=ReturnType.DICT)
            assert payload["identifiers"]["re3data"] == "r3d100012417"  # type: ignore[index]
            assert payload["repositoryUrl"] == "https://discovery.ucl.ac.uk/"  # type: ignore[index]

    def test_filters_are_dropped_on_non_v40_list(self, caplog: pytest.LogCaptureFixture) -> None:
        with (
            Client(list_api_version="v1", transport=_versioned_transport()) as client,
            caplog.at_level("WARNING"),
        ):
            summaries = client.repositories.list(filters={"countries": ["DEU"]})
        assert summaries
        assert any("ignoring filters" in record.message for record in caplog.records)

    def test_beta_detail_works(self) -> None:
        with Client(api_version="beta", transport=_versioned_transport()) as client:
            repository = client.repositories.get("r3d100012417")
            assert repository.id == "r3d100012417"


class TestVersionedAsyncClient:
    def test_list_via_v1_details_via_v40(self) -> None:
        client = AsyncClient(list_api_version="v1", transport=_versioned_transport())
        summaries = asyncio.run(client.repositories.list())
        repository = asyncio.run(client.repositories.get("r3d100012417"))
        asyncio.run(client.aclose())
        assert summaries[0].id == "r3d100000001"
        assert repository.identifiers.doi
