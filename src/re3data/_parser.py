"""Parse re3data API XML documents (schema 4.0) into typed models.

The re3data v40 API only serves ``application/xml``. This module converts the
XML into the typed dataclasses from :mod:`re3data._resources` using only the
standard library :mod:`xml.etree.ElementTree`.

Robustness rules:

- Unknown elements and attributes are ignored (forward compatibility).
- Missing optional elements become ``None`` / empty lists, never errors.
- Malformed dates degrade to ``None`` instead of failing the whole document
  (upstream data has shown such inconsistencies).
- Vocabulary values are kept as plain strings even if unknown to the schema.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date

from re3data._exceptions import Re3dataError
from re3data._resources.repository import (
    AdditionalName,
    Api,
    Certificate,
    ContentType,
    DataAccess,
    DatabaseAccess,
    DatabaseLicense,
    DataLicense,
    DataUpload,
    DataUploadLicense,
    Description,
    EndDate,
    FunderIdentifier,
    FundingInformation,
    Identifiers,
    Institution,
    InstitutionAdditionalName,
    InstitutionIdentifier,
    InstitutionName,
    MetadataStandard,
    Policy,
    Profile,
    QualityManagement,
    QualityManagementMeasure,
    Re3Data,
    RelatedRepository,
    Repository,
    RepositoryContact,
    RepositoryIdentifier,
    RepositoryName,
    Subject,
    Syndication,
)
from re3data._resources.repository_list import Link, RepositoryList, RepositorySummary

_RE3DATA_NS = "{http://www.re3data.org/schema/4-0}"


def _local_name(element: ET.Element) -> str:
    """The local name of an element, ignoring any XML namespace prefix.

    Detail documents use the ``r3d:`` prefix, index list documents are served
    without a namespace; matching on local names covers both.
    """
    return element.tag.rsplit("}", 1)[-1]


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    """All direct children of ``element`` with the given local name."""
    return [child for child in element if _local_name(child) == name]


def _child(element: ET.Element, name: str) -> ET.Element | None:
    """The first direct child of ``element`` with the given local name, if any."""
    for child in element:
        if _local_name(child) == name:
            return child
    return None


def _text(element: ET.Element | None) -> str | None:
    """The stripped text of an element, or None if absent/empty."""
    if element is None:
        return None
    text = (element.text or "").strip()
    return text or None


def _texts(element: ET.Element, name: str) -> list[str]:
    """The stripped texts of all children with the given local name."""
    return [text for child in _children(element, name) if (text := _text(child)) is not None]


def _attr(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    value = element.get(name)
    return value if value else None


def _date_value(text: str | None) -> date | None:
    if text is None:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        # upstream data occasionally carries malformed dates; degrade gracefully
        return None


def _parse_repository_name(element: ET.Element) -> RepositoryName:
    return RepositoryName(value=_text(element) or "", language=_attr(element, "language"))


def _parse_additional_name(element: ET.Element) -> AdditionalName:
    return AdditionalName(value=_text(element) or "", language=_attr(element, "language"))


def _parse_description(element: ET.Element) -> Description:
    return Description(value=_text(element) or "", language=_attr(element, "language"))


def _parse_institution_name(element: ET.Element) -> InstitutionName:
    return InstitutionName(value=_text(element) or "", language=_attr(element, "language"))


def _parse_institution_additional_name(element: ET.Element) -> InstitutionAdditionalName:
    return InstitutionAdditionalName(value=_text(element) or "", language=_attr(element, "language"))


def _parse_repository_identifier(element: ET.Element) -> RepositoryIdentifier:
    return RepositoryIdentifier(
        repositoryIdentifierType=_text(_child(element, "repositoryIdentifierType")),
        repositoryIdentifierValue=_text(_child(element, "repositoryIdentifierValue")),
    )


def _parse_repository_contact(element: ET.Element) -> RepositoryContact:
    return RepositoryContact(
        repositoryContactInformation=_text(_child(element, "repositoryContactInformation")),
        repositoryContactType=_text(_child(element, "repositoryContactType")),
    )


def _parse_end_date(element: ET.Element) -> EndDate:
    return EndDate(
        closed=_child(element, "closed") is not None,
        offline=_child(element, "offline") is not None,
    )


def _parse_related_repository(element: ET.Element) -> RelatedRepository:
    return RelatedRepository(
        relatedRepositoryId=_text(_child(element, "relatedRepositoryId")),
        relatedRepositoryType=_text(_child(element, "relatedRepositoryType")),
    )


def _parse_subject(element: ET.Element) -> Subject:
    return Subject(
        subjectId=_text(_child(element, "subjectId")),
        subjectName=_text(_child(element, "subjectName")),
        subjectScheme=_attr(element, "subjectScheme"),
    )


def _parse_content_type(element: ET.Element) -> ContentType:
    return ContentType(
        contentTypeId=_text(_child(element, "contentTypeId")),
        contentTypeName=_text(_child(element, "contentTypeName")),
        contentTypeScheme=_attr(element, "contentTypeScheme"),
    )


def _parse_institution_identifier(element: ET.Element) -> InstitutionIdentifier:
    return InstitutionIdentifier(
        institutionIdentifierType=_text(_child(element, "institutionIdentifierType")),
        institutionIdentifierUrl=_text(_child(element, "institutionIdentifierUrl")),
    )


def _parse_institution(element: ET.Element) -> Institution:
    name_element = _child(element, "institutionName")
    return Institution(
        institutionName=_parse_institution_name(name_element) if name_element is not None else None,
        institutionAdditionalName=[
            _parse_institution_additional_name(child) for child in _children(element, "institutionAdditionalName")
        ],
        institutionCountry=_text(_child(element, "institutionCountry")),
        responsibilityType=_texts(element, "responsibilityType"),
        institutionType=_text(_child(element, "institutionType")),
        institutionUrl=_text(_child(element, "institutionUrl")),
        institutionIdentifier=[_parse_institution_identifier(child) for child in _children(element, "institutionIdentifier")],
        responsibilityStartDate=_date_value(_text(_child(element, "responsibilityStartDate"))),
        responsibilityEndDate=_date_value(_text(_child(element, "responsibilityEndDate"))),
    )


def _parse_policy(element: ET.Element) -> Policy:
    return Policy(policyName=_text(_child(element, "policyName")), policyUrl=_text(_child(element, "policyUrl")))


def _parse_funder_identifier(element: ET.Element) -> FunderIdentifier:
    return FunderIdentifier(
        funderIdentifierType=_text(_child(element, "funderIdentifierType")),
        funderIdentifierValue=_text(_child(element, "funderIdentifierValue")),
    )


def _parse_funding_information(element: ET.Element) -> FundingInformation:
    return FundingInformation(
        funderName=_text(_child(element, "funderName")),
        funderIdentifier=[_parse_funder_identifier(child) for child in _children(element, "funderIdentifier")],
        grantIdentifier=_text(_child(element, "grantIdentifier")),
    )


def _parse_database_access(element: ET.Element) -> DatabaseAccess:
    return DatabaseAccess(
        databaseAccessType=_text(_child(element, "databaseAccessType")),
        databaseAccessRestriction=_texts(element, "databaseAccessRestriction"),
    )


def _parse_database_license(element: ET.Element) -> DatabaseLicense:
    return DatabaseLicense(
        databaseLicenseName=_text(_child(element, "databaseLicenseName")),
        databaseLicenseUrl=_text(_child(element, "databaseLicenseUrl")),
    )


def _parse_data_access(element: ET.Element) -> DataAccess:
    return DataAccess(
        dataAccessType=_text(_child(element, "dataAccessType")),
        dataAccessRestriction=_texts(element, "dataAccessRestriction"),
    )


def _parse_data_license(element: ET.Element) -> DataLicense:
    return DataLicense(
        dataLicenseName=_text(_child(element, "dataLicenseName")),
        dataLicenseUrl=_text(_child(element, "dataLicenseUrl")),
    )


def _parse_data_upload(element: ET.Element) -> DataUpload:
    return DataUpload(
        dataUploadType=_text(_child(element, "dataUploadType")),
        dataUploadRestriction=_texts(element, "dataUploadRestriction"),
    )


def _parse_data_upload_license(element: ET.Element) -> DataUploadLicense:
    return DataUploadLicense(
        dataUploadLicenseName=_text(_child(element, "dataUploadLicenseName")),
        dataUploadLicenseUrl=_text(_child(element, "dataUploadLicenseUrl")),
    )


def _parse_api(element: ET.Element) -> Api:
    return Api(
        apiType=_text(_child(element, "apiType")),
        apiUrl=_text(_child(element, "apiUrl")),
        apiDocumentation=_text(_child(element, "apiDocumentation")),
    )


def _parse_quality_management_measure(element: ET.Element) -> QualityManagementMeasure:
    return QualityManagementMeasure(
        qualityManagementMeasureName=_text(_child(element, "qualityManagementMeasureName")),
        qualityManagementMeasureUrl=_text(_child(element, "qualityManagementMeasureUrl")),
    )


def _parse_quality_management(element: ET.Element) -> QualityManagement:
    return QualityManagement(
        qualityManagementStatus=_text(_child(element, "qualityManagementStatus")),
        qualityManagementMeasure=[
            _parse_quality_management_measure(child) for child in _children(element, "qualityManagementMeasure")
        ],
    )


def _parse_certificate(element: ET.Element) -> Certificate:
    return Certificate(
        certificateName=_text(_child(element, "certificateName")),
        certificateStartDate=_date_value(_text(_child(element, "certificateStartDate"))),
        certificateEndDate=_date_value(_text(_child(element, "certificateEndDate"))),
        certificateUrl=_text(_child(element, "certificateUrl")),
        certificateWidget=_text(_child(element, "certificateWidget")),
    )


def _parse_profile(element: ET.Element) -> Profile:
    return Profile(profileName=_text(_child(element, "profileName")), profileUrl=_text(_child(element, "profileUrl")))


def _parse_metadata_standard(element: ET.Element) -> MetadataStandard:
    return MetadataStandard(
        metadataStandardName=_text(_child(element, "metadataStandardName")),
        metadataStandardUrl=_text(_child(element, "metadataStandardUrl")),
    )


def _parse_syndication(element: ET.Element) -> Syndication:
    return Syndication(
        syndicationType=_text(_child(element, "syndicationType")),
        syndicationUrl=_text(_child(element, "syndicationUrl")),
    )


def _parse_repository(element: ET.Element) -> Repository:
    identifiers_element = _child(element, "identifiers")
    end_date_element = _child(element, "endDate")
    quality_management_element = _child(element, "qualityManagement")
    database_access_element = _child(element, "databaseAccess")
    return Repository(
        identifiers=(
            Identifiers(
                re3data=_text(_child(identifiers_element, "re3data")),
                doi=_text(_child(identifiers_element, "doi")),
            )
            if identifiers_element is not None
            else None
        ),
        repositoryName=(
            _parse_repository_name(name_element)
            if (name_element := _child(element, "repositoryName")) is not None
            else None
        ),
        additionalName=[_parse_additional_name(child) for child in _children(element, "additionalName")],
        repositoryUrl=_text(_child(element, "repositoryUrl")),
        repositoryIdentifier=[_parse_repository_identifier(child) for child in _children(element, "repositoryIdentifier")],
        description=[_parse_description(child) for child in _children(element, "description")],
        repositoryContact=[_parse_repository_contact(child) for child in _children(element, "repositoryContact")],
        type=_texts(element, "type"),
        size=_text(_child(element, "size")),
        startDate=_date_value(_text(_child(element, "startDate"))),
        endDate=_parse_end_date(end_date_element) if end_date_element is not None else None,
        relatedRepository=[_parse_related_repository(child) for child in _children(element, "relatedRepository")],
        repositoryLanguage=_texts(element, "repositoryLanguage"),
        subject=[_parse_subject(child) for child in _children(element, "subject")],
        missionStatementUrl=_text(_child(element, "missionStatementUrl")),
        contentType=[_parse_content_type(child) for child in _children(element, "contentType")],
        providerType=_texts(element, "providerType"),
        keyword=_texts(element, "keyword"),
        institution=[_parse_institution(child) for child in _children(element, "institution")],
        policy=[_parse_policy(child) for child in _children(element, "policy")],
        fundingInformation=[_parse_funding_information(child) for child in _children(element, "fundingInformation")],
        databaseAccess=_parse_database_access(database_access_element) if database_access_element is not None else None,
        databaseLicense=[_parse_database_license(child) for child in _children(element, "databaseLicense")],
        dataAccess=[_parse_data_access(child) for child in _children(element, "dataAccess")],
        dataLicense=[_parse_data_license(child) for child in _children(element, "dataLicense")],
        dataUpload=[_parse_data_upload(child) for child in _children(element, "dataUpload")],
        dataUploadLicense=[_parse_data_upload_license(child) for child in _children(element, "dataUploadLicense")],
        software=_texts(element, "software"),
        versioning=_text(_child(element, "versioning")),
        api=[_parse_api(child) for child in _children(element, "api")],
        pidSystem=_texts(element, "pidSystem"),
        citationReference=_texts(element, "citationReference"),
        metrics=_texts(element, "metrics"),
        citationGuidelineUrl=_text(_child(element, "citationGuidelineUrl")),
        aidSystem=_texts(element, "aidSystem"),
        enhancedPublication=_text(_child(element, "enhancedPublication")),
        qualityManagement=(
            _parse_quality_management(quality_management_element) if quality_management_element is not None else None
        ),
        certificate=[_parse_certificate(child) for child in _children(element, "certificate")],
        profile=[_parse_profile(child) for child in _children(element, "profile")],
        metadataStandard=[_parse_metadata_standard(child) for child in _children(element, "metadataStandard")],
        syndication=[_parse_syndication(child) for child in _children(element, "syndication")],
        remarks=_text(_child(element, "remarks")),
        entryDate=_date_value(_text(_child(element, "entryDate"))),
        lastUpdate=_date_value(_text(_child(element, "lastUpdate"))),
    )


def _parse_link(element: ET.Element) -> Link:
    return Link(href=_attr(element, "href"), rel=_attr(element, "rel"))


def _parse_repository_summary(element: ET.Element) -> RepositorySummary:
    link_element = _child(element, "link")
    return RepositorySummary(
        id=_text(_child(element, "id")),
        doi=_text(_child(element, "doi")),
        name=_text(_child(element, "name")),
        link=_parse_link(link_element) if link_element is not None else None,
    )


def parse_re3data(text: str) -> Re3Data:
    """Parse a repository detail XML document into a :class:`Re3Data` object.

    Args:
        text: The XML document text as returned by ``GET /api/v40/repository/{id}``.

    Returns:
        The parsed document; repositories may be empty if the document carries none.

    Raises:
        Re3dataError: If the document is not well-formed XML.
    """
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise Re3dataError(f"Unable to parse re3data XML response: {error}") from error
    repositories = [_parse_repository(child) for child in _children(root, "repository")]
    return Re3Data(repository=repositories)


def parse_repository(text: str) -> Repository:
    """Parse a repository detail XML document and return its single repository.

    Raises:
        Re3dataError: If the document is not well-formed XML or contains no repository.
    """
    document = parse_re3data(text)
    if not document.repository:
        raise Re3dataError("re3data XML response contains no repository element")
    return document.repository[0]


def parse_repository_list(text: str) -> RepositoryList:
    """Parse a repository index list XML document into a :class:`RepositoryList`.

    Args:
        text: The XML document text as returned by ``GET /api/v40/repositories``.

    Returns:
        The parsed list; entries may be empty if the document carries none.

    Raises:
        Re3dataError: If the document is not well-formed XML.
    """
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise Re3dataError(f"Unable to parse re3data XML response: {error}") from error
    summaries = [_parse_repository_summary(child) for child in _children(root, "repository")]
    return RepositoryList(repository=summaries)
