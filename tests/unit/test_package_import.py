"""Smoke tests for the package import surface."""

from __future__ import annotations

import re3data


def test_public_api_exports() -> None:
    for name in (
        "AsyncClient",
        "Client",
        "Re3Data",
        "Re3dataError",
        "Repository",
        "RepositoryList",
        "RepositoryNotFoundError",
        "RepositorySummary",
        "Response",
        "ReturnType",
        "__version__",
    ):
        assert hasattr(re3data, name), name


def test_module_level_repositories_manager() -> None:
    assert hasattr(re3data.repositories, "list")
    assert hasattr(re3data.repositories, "get")
