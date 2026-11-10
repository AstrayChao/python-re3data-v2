"""Unit tests for the v40 XML parser."""

from __future__ import annotations

from datetime import date

import pytest

from re3data._exceptions import Re3dataError
from re3data._parser import parse_repository, parse_repository_list


class TestParseRepository:
    def test_parses_identifiers(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.identifiers.re3data == "r3d100012417"
        assert repository.identifiers.doi == "https://doi.org/10.17616/R34F41"
        assert repository.id == "r3d100012417"

    def test_parses_localized_repository_name(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.repositoryName.value == "UCL Discovery"
        assert repository.repositoryName.language == "eng"

    def test_parses_v40_url_casing(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.repositoryUrl == "https://discovery.ucl.ac.uk/"

    def test_parses_structured_repository_contact(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.repositoryContact[0].repositoryContactInformation == "discovery@ucl.ac.uk"

    def test_parses_size_without_updated_attribute(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.size == "103datasets"

    def test_parses_subject_ids_and_names(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        subjects = {subject.subjectId: subject for subject in repository.subject}
        assert "4" in subjects
        assert subjects["4"].subjectName == "Engineering Sciences"
        assert subjects["4"].subjectScheme == "DFG"

    def test_parses_structured_institution_identifier(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        identifiers = repository.institution[0].institutionIdentifier
        by_type = {identifier.institutionIdentifierType: identifier for identifier in identifiers}
        assert by_type["ROR"].institutionIdentifierUrl == "https://ror.org/02jx3x895"

    def test_parses_policy_names_and_urls(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.policy[0].policyName == "Open access"
        assert repository.policy[0].policyUrl == "https://www.ucl.ac.uk/library/open-science-research-support/open-access/"

    def test_parses_data_upload_restrictions(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        restricted = [upload for upload in repository.dataUpload if upload.dataUploadType == "restricted"]
        # upstream data uses "institutional membership" (with space), the XSD
        # vocabulary says "institutionalMembership" — kept verbatim as a string
        assert restricted[0].dataUploadRestriction == ["institutional membership"]

    def test_parses_api_with_url_element(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.api[0].apiType == "OAI-PMH"
        assert repository.api[0].apiUrl == "https://discovery.ucl.ac.uk/cgi/oai2?verb=Identify"

    def test_parses_metadata_standard_urls(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.metadataStandard[0].metadataStandardName == "DataCite Metadata Schema"
        assert repository.metadataStandard[0].metadataStandardUrl == "https://rdamsc.bath.ac.uk/msc/m11"

    def test_parses_dates(self, detail_xml: str) -> None:
        repository = parse_repository(detail_xml)
        assert repository.entryDate == date(2017, 7, 21)
        assert repository.lastUpdate == date(2023, 12, 6)

    def test_parses_new_v40_fields_of_rich_document(self, detail_rich_xml: str) -> None:
        repository = parse_repository(detail_rich_xml)
        assert repository.metrics
        assert repository.fundingInformation
        assert all(entry.funderName for entry in repository.fundingInformation)
        identifier_types = {
            identifier.repositoryIdentifierType for identifier in repository.repositoryIdentifier
        }
        assert identifier_types
        assert all(identifier.repositoryIdentifierValue for identifier in repository.repositoryIdentifier)

    def test_parses_structured_certificate(self, detail_certificate_xml: str) -> None:
        repository = parse_repository(detail_certificate_xml)
        certificate = repository.certificate[0]
        assert certificate.certificateName
        assert certificate.certificateUrl
        assert certificate.certificateStartDate is None or isinstance(certificate.certificateStartDate, date)

    def test_malformed_xml_raises_re3data_error(self) -> None:
        with pytest.raises(Re3dataError):
            parse_repository("<not-xml")

    def test_empty_document_raises_re3data_error(self) -> None:
        with pytest.raises(Re3dataError):
            parse_repository('<?xml version="1.0"?><r3d:re3data xmlns:r3d="http://www.re3data.org/schema/4-0"></r3d:re3data>')


class TestParseRepositoryList:
    def test_parses_summaries_including_name(self, list_xml: str) -> None:
        document = parse_repository_list(list_xml)
        assert len(document.repository) == 11
        summary = document.repository[0]
        assert summary.id == "r3d100013090"
        assert summary.doi == "https://doi.org/10.17616/R31NJMLE"
        assert summary.name == "UCL Research Data Repository"
        assert summary.href == "https://www.re3data.org/api/v40/repository/r3d100013090"
        assert summary.link.rel == "self"

    def test_malformed_xml_raises_re3data_error(self) -> None:
        with pytest.raises(Re3dataError):
            parse_repository_list("nope")
