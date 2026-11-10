"""Serialize parsed re3data resources into dict, JSON and CSV representations.

Dict conventions (matching the contract established by the original
python-re3data library):

- Keys are the XML element/attribute names (camelCase).
- Elements with text and attributes become ``{"value": ..., "language": ...}``.
- Dates are rendered as ISO-8601 strings (``2023-12-06``).
- Absent optional scalars are ``None``; absent repeats are empty lists.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, is_dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from re3data._resources import RepositorySummary

if TYPE_CHECKING:
    from re3data._resources import Repository


def _normalize(node: Any) -> Any:
    """Recursively convert non-JSON-native leaves into JSON-native ones."""
    if isinstance(node, date):
        return node.isoformat()
    if is_dataclass(node):
        return {key: _normalize(value) for key, value in asdict(node).items()}
    if isinstance(node, dict):
        return {key: _normalize(value) for key, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [_normalize(item) for item in node]
    return node


def _to_dict(parsed: Repository | list[RepositorySummary]) -> dict[str, Any] | list[dict[str, Any]]:
    """Serialize a parsed resource into a dictionary."""
    return _normalize(parsed)


def _to_json(parsed: Repository | list[RepositorySummary]) -> str:
    """Serialize a parsed resource into a JSON string."""
    return json.dumps(_normalize(parsed), indent=2, ensure_ascii=False)


def _repository_summary_row(summary: RepositorySummary) -> dict[str, Any]:
    return {
        "id": summary.id,
        "doi": summary.doi,
        "name": summary.name,
        "href": summary.href,
    }


def _to_csv(parsed: Repository | list[RepositorySummary]) -> str:
    """Serialize repository summaries into a CSV string.

    Only list responses produce tabular output; a single repository detail is
    rendered as one summary row.
    """
    summaries: list[RepositorySummary]
    if isinstance(parsed, list):
        summaries = parsed
    else:
        summaries = [
            RepositorySummary(
                id=parsed.id,
                doi=parsed.identifiers.doi if parsed.identifiers else None,
                name=parsed.repositoryName.value if parsed.repositoryName else None,
                link=None,
            )
        ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["id", "doi", "name", "href"], lineterminator="\n")
    writer.writeheader()
    for summary in summaries:
        writer.writerow(_repository_summary_row(summary))
    return buffer.getvalue().rstrip("\n")
