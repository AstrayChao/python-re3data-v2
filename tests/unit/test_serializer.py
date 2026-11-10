"""Unit tests for the serializers (dict/json/csv conventions)."""

from __future__ import annotations

import json

from re3data._parser import parse_repository, parse_repository_list
from re3data._serializer import _to_csv, _to_dict, _to_json


class TestToDict:
    def test_uses_xml_element_names_as_keys(self, detail_xml: str) -> None:
        payload = _to_dict(parse_repository(detail_xml))
        assert payload["identifiers"] == {"re3data": "r3d100012417", "doi": "https://doi.org/10.17616/R34F41"}

    def test_localized_elements_use_value_and_language(self, detail_xml: str) -> None:
        payload = _to_dict(parse_repository(detail_xml))
        assert payload["repositoryName"] == {"value": "UCL Discovery", "language": "eng"}

    def test_dates_are_iso_strings(self, detail_xml: str) -> None:
        payload = _to_dict(parse_repository(detail_xml))
        assert payload["entryDate"] == "2017-07-21"
        assert payload["lastUpdate"] == "2023-12-06"

    def test_lists_and_missing_optionals(self, detail_xml: str) -> None:
        payload = _to_dict(parse_repository(detail_xml))
        assert payload["additionalName"] == []
        assert payload["startDate"] is None
        assert isinstance(payload["subject"], list)
        assert payload["subject"][0]["subjectId"] == "4"

    def test_summary_list_dict(self, list_xml: str) -> None:
        payload = _to_dict(parse_repository_list(list_xml).repository)
        assert payload[0]["id"] == "r3d100013090"
        assert payload[0]["name"] == "UCL Research Data Repository"


class TestToJson:
    def test_json_round_trip(self, detail_xml: str) -> None:
        text = _to_json(parse_repository(detail_xml))
        payload = json.loads(text)
        assert payload["identifiers"]["re3data"] == "r3d100012417"


class TestToCsv:
    def test_csv_header_and_rows(self, list_xml: str) -> None:
        csv_text = _to_csv(parse_repository_list(list_xml).repository)
        lines = csv_text.splitlines()
        assert lines[0] == "id,doi,name,href"
        assert lines[1].startswith("r3d100013090,https://doi.org/10.17616/R31NJMLE,UCL Research Data Repository")

    def test_csv_of_single_repository(self, detail_xml: str) -> None:
        csv_text = _to_csv(parse_repository(detail_xml))
        lines = csv_text.splitlines()
        assert lines[0] == "id,doi,name,href"
        assert lines[1].startswith("r3d100012417,https://doi.org/10.17616/R34F41,UCL Discovery")
