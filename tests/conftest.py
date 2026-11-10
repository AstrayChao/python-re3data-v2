"""Shared fixtures: real v40 XML documents and httpx mock transports."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def fixture_text(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


@pytest.fixture
def detail_xml() -> str:
    """A real v40 detail response (UCL Discovery, r3d100012417)."""
    return fixture_text("repository_r3d100012417.xml")


@pytest.fixture
def detail_rich_xml() -> str:
    """A real v40 detail response with repositoryIdentifier/fundingInformation/metrics (Zenodo)."""
    return fixture_text("repository_r3d100010468.xml")


@pytest.fixture
def detail_certificate_xml() -> str:
    """A real v40 detail response with a structured certificate (r3d100010299)."""
    return fixture_text("repository_r3d100010299.xml")


@pytest.fixture
def list_xml() -> str:
    """A real v40 list response (query=UCL)."""
    return fixture_text("repositories_query_ucl.xml")


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/api/v40/repositories":
        if dict(request.url.params):
            # any query/filter narrows the result and works upstream
            return httpx.Response(200, text=fixture_text("repositories_query_ucl.xml"))
        # upstream currently returns 500 for the unfiltered full list
        return httpx.Response(500, text='<?xml version="1.0"?><response><status>500</status></response>')
    if path == "/api/v40/repository/r3d100012417":
        return httpx.Response(200, text=fixture_text("repository_r3d100012417.xml"))
    if path == "/api/v40/repository/r3d100010468":
        return httpx.Response(200, text=fixture_text("repository_r3d100010468.xml"))
    if path == "/api/v40/repository/r3d100010299":
        return httpx.Response(200, text=fixture_text("repository_r3d100010299.xml"))
    return httpx.Response(404, text='<?xml version="1.0"?><response><status>404</status></response>')


@pytest.fixture
def mock_transport() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)
