"""Tests for parsing schema 2-2 documents (v1/beta endpoints) into the schema 4.0 model."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from re3data._parser import parse_repository, parse_repository_list

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestParseRepository22:
    def test_parses_v1_detail_into_40_model(self) -> None:
        repository = parse_repository(fixture_text("repository_v1_r3d100012417.xml"))

        assert repository.identifiers.re3data == "r3d100012417"
        assert repository.id == "r3d100012417"
        assert repository.repositoryName.value == "UCL Discovery"
        assert repository.repositoryUrl == "https://discovery.ucl.ac.uk/"

    def test_subjects_are_split_into_id_and_name(self) -> None:
        repository = parse_repository(fixture_text("repository_v1_r3d100012417.xml"))

        subjects = {subject.subjectName for subject in repository.subject}
        assert subjects
        for subject in repository.subject:
            if subject.subjectId is not None:
                assert subject.subjectId.isdigit()
                assert subject.subjectName
                assert not subject.subjectName.startswith(subject.subjectId)

    def test_structured_conversions(self) -> None:
        repository = parse_repository(fixture_text("repository_v1_r3d100012417.xml"))

        # 2-2 plain strings -> 4.0 structures
        assert all(
            contact.repositoryContactInformation for contact in repository.repositoryContact
        )
        assert all(api.apiUrl is not None or api.apiType is not None for api in repository.api)
        assert all(certificate.certificateName for certificate in repository.certificate)
        if repository.qualityManagement is not None:
            assert repository.qualityManagement.qualityManagementStatus in {"yes", "no", "unknown"}
        for content_type in repository.contentType:
            assert content_type.contentTypeName
            assert content_type.contentTypeId is None  # no COAR id on 2-2

    def test_dates(self) -> None:
        repository = parse_repository(fixture_text("repository_v1_r3d100012417.xml"))

        assert repository.entryDate == date(2017, 7, 21)
        assert repository.lastUpdate is not None

    def test_beta_detail_parses_identically(self) -> None:
        v1 = parse_repository(fixture_text("repository_v1_r3d100012417.xml"))
        beta = parse_repository(fixture_text("repository_beta_r3d100012417.xml"))

        assert beta.id == v1.id == "r3d100012417"
        assert beta.repositoryName.value == v1.repositoryName.value
        assert beta.repositoryUrl == v1.repositoryUrl

    def test_v40_document_still_uses_native_parser(self) -> None:
        repository = parse_repository(fixture_text("repository_r3d100012417.xml"))

        # 4.0 fixture: identifiers carry a DOI, subjects use numeric ids natively
        assert repository.identifiers.doi
        assert any(subject.subjectId for subject in repository.subject)


class TestParseV1List:
    def test_parses_v1_list_with_relative_links(self) -> None:
        document = parse_repository_list(fixture_text("repositories_v1_list.xml"))

        assert len(document.repository) == 3
        summary = document.repository[0]
        assert summary.id == "r3d100000001"
        assert summary.doi
        assert summary.name  # v1 list also carries names
        assert summary.href == "/api/v1/repository/r3d100000001"  # relative link
