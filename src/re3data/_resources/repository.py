"""API resources for the /repository/{id} endpoint (v40, schema 4.0).

Typed models mirroring the `re3data.org Metadata Schema for the Description of
Research Data Repositories, Version 4.0 (August 2023)
<https://doi.org/10.48440/re3.014>`_. The authoritative XSD is served at
https://schema.re3data.org/4-0/re3dataV4-0.xsd.

Design notes:

- Dataclass field names intentionally mirror the XML element/attribute names
  (camelCase), so ``dataclasses.asdict`` reproduces the document structure
  with XML-style keys, matching the dict contract established by the original
  python-re3data library.
- Elements carrying text plus attributes (e.g. ``repositoryName`` with a
  ``language`` attribute) are modelled as ``{"value": ..., "language": ...}``.
- Vocabulary fields are typed as plain ``str`` instead of enums. Schema 4.0
  data has already shown drift against the XSD vocabularies (the upstream API
  team keeps extending values); parsing therefore never fails on unknown
  values. The controlled vocabularies are exported as reference enums below
  for callers that want to compare against known values.
- Dates (``entryDate``, ``lastUpdate``, ...) are parsed to ``datetime.date``
  and serialized back to ISO-8601 strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

__NAMESPACE__ = "http://www.re3data.org/schema/4-0"


# ------------------------------------------------------------------------------
# Reference vocabularies (schema 4.0 simpleTypes)
# ------------------------------------------------------------------------------


class RepositoryType(StrEnum):
    """Repository types (schema 4.0: 6 values, up from 3 in schema 2-2)."""

    DISCIPLINARY = "disciplinary"
    GOVERNMENTAL = "governmental"
    INSTITUTIONAL = "institutional"
    MULTIDISCIPLINARY = "multidisciplinary"
    PROJECT_RELATED = "project-related"
    OTHER = "other"


class ProviderType(StrEnum):
    DATA_PROVIDER = "dataProvider"
    SERVICE_PROVIDER = "serviceProvider"


class DatabaseAccessType(StrEnum):
    OPEN = "open"
    RESTRICTED = "restricted"
    CLOSED = "closed"


class DatabaseAccessRestriction(StrEnum):
    FEE_REQUIRED = "feeRequired"
    REGISTRATION = "registration"


class DataAccessType(StrEnum):
    OPEN = "open"
    EMBARGOED = "embargoed"
    RESTRICTED = "restricted"
    CLOSED = "closed"


class DataAccessRestriction(StrEnum):
    FEE_REQUIRED = "feeRequired"
    INSTITUTIONAL_MEMBERSHIP = "institutionalMembership"
    REGISTRATION = "registration"


class DataUploadType(StrEnum):
    OPEN = "open"
    RESTRICTED = "restricted"
    CLOSED = "closed"


class DataUploadRestriction(StrEnum):
    FEE_REQUIRED = "feeRequired"
    INSTITUTIONAL_MEMBERSHIP = "institutionalMembership"
    REGISTRATION = "registration"
    STORAGE_LIMIT = "storageLimit"


class InstitutionType(StrEnum):
    COMMERCIAL = "commercial"
    NON_PROFIT = "non-profit"


class ResponsibilityType(StrEnum):
    """Institution responsibility types (schema 4.0 dropped "sponsoring")."""

    FUNDING = "funding"
    GENERAL = "general"
    TECHNICAL = "technical"


class RelatedRepositoryType(StrEnum):
    PREDECESSOR = "predecessor"
    SUCCESSOR = "successor"


class YesNo(StrEnum):
    YES = "yes"
    NO = "no"


# ------------------------------------------------------------------------------
# Leaf wrapper elements
# ------------------------------------------------------------------------------


@dataclass(slots=True)
class Identifiers:
    """Wrapper of the persistent identifiers of the repository.

    Attributes:
        re3data: The re3data identifier, e.g. "r3d100012417".
        doi: The re3data DOI, e.g. "https://doi.org/10.17616/R34F41".
    """

    re3data: str | None = None
    doi: str | None = None


@dataclass(slots=True)
class RepositoryName:
    """The full name of the repository, with an optional language attribute."""

    value: str = ""
    language: str | None = None


@dataclass(slots=True)
class AdditionalName:
    """The alternative name or acronym of the repository."""

    value: str = ""
    language: str | None = None


@dataclass(slots=True)
class Description:
    """A textual description of the repository (primary language is English)."""

    value: str = ""
    language: str | None = None


@dataclass(slots=True)
class RepositoryIdentifier:
    """A globally unique identifier referring to the repository.

    Attributes:
        repositoryIdentifierType: The type of the identifier, e.g. "DOI", "ROR".
        repositoryIdentifierValue: The identifier value, usually a URL.
    """

    repositoryIdentifierType: str | None = None
    repositoryIdentifierValue: str | None = None


@dataclass(slots=True)
class RepositoryContact:
    """Contact information of the repository.

    New in schema 4.0: a wrapper element instead of a plain string.

    Attributes:
        repositoryContactInformation: An email address or contact form URL.
        repositoryContactType: Optional type of the contact information.
    """

    repositoryContactInformation: str | None = None
    repositoryContactType: str | None = None


@dataclass(slots=True)
class EndDate:
    """Date details when the repository went offline or stopped ingesting.

    New in schema 4.0: the closed/offline flags replace the former date value.
    """

    closed: bool = False
    offline: bool = False


@dataclass(slots=True)
class RelatedRepository:
    """A related (predecessor/successor) repository. New in schema 4.0."""

    relatedRepositoryId: str | None = None
    relatedRepositoryType: str | None = None


@dataclass(slots=True)
class Subject:
    """A subject of the repository, based on the DFG classification.

    New in schema 4.0: subjects are identified by ``subjectId`` (e.g. "11204")
    instead of the former free text ("11204 Business Administration").

    Attributes:
        subjectId: The DFG subject identifier, e.g. "11204".
        subjectName: The DFG subject name, e.g. "Business Administration".
        subjectScheme: The subject scheme attribute, e.g. "DFG".
    """

    subjectId: str | None = None
    subjectName: str | None = None
    subjectScheme: str | None = None


@dataclass(slots=True)
class ContentType:
    """A content type available in the repository, based on COAR resource types.

    New in schema 4.0: content types moved from the former "parse" text list
    to COAR resource type URIs.

    Attributes:
        contentTypeId: The COAR resource type URI.
        contentTypeName: The COAR resource type name, e.g. "dataset".
        contentTypeScheme: The content type scheme attribute, e.g. "COAR".
    """

    contentTypeId: str | None = None
    contentTypeName: str | None = None
    contentTypeScheme: str | None = None


@dataclass(slots=True)
class InstitutionName:
    """The name of an institution, with an optional language attribute."""

    value: str = ""
    language: str | None = None


@dataclass(slots=True)
class InstitutionAdditionalName:
    """The alternative name of an institution."""

    value: str = ""
    language: str | None = None


@dataclass(slots=True)
class InstitutionIdentifier:
    """An identifier of an institution.

    New in schema 4.0: structured type/url pair instead of a plain string.

    Attributes:
        institutionIdentifierType: e.g. "ROR", "RRID".
        institutionIdentifierUrl: e.g. "https://ror.org/02jx3x895".
    """

    institutionIdentifierType: str | None = None
    institutionIdentifierUrl: str | None = None


@dataclass(slots=True)
class Institution:
    """An institution responsible for funding, creating and/or running the repository.

    Attributes:
        institutionName: The name of the institution.
        institutionAdditionalName: Alternative names of the institution.
        institutionCountry: The country of the institution (ISO 3166-1 alpha-3).
        responsibilityType: The types of responsibility, e.g. "funding".
        institutionType: The type of institution, e.g. "non-profit".
        institutionUrl: The URL of the institution.
        institutionIdentifier: Identifiers of the institution.
        responsibilityStartDate: Start of the responsibility (new in 4.0).
        responsibilityEndDate: End of the responsibility (new in 4.0).
    """

    institutionName: InstitutionName | None = None
    institutionAdditionalName: list[InstitutionAdditionalName] = field(default_factory=list)
    institutionCountry: str | None = None
    responsibilityType: list[str] = field(default_factory=list)
    institutionType: str | None = None
    institutionUrl: str | None = None
    institutionIdentifier: list[InstitutionIdentifier] = field(default_factory=list)
    responsibilityStartDate: date | None = None
    responsibilityEndDate: date | None = None


@dataclass(slots=True)
class Policy:
    """A policy of the repository, e.g. a data policy."""

    policyName: str | None = None
    policyUrl: str | None = None


@dataclass(slots=True)
class FunderIdentifier:
    """An identifier of a funder. New in schema 4.0."""

    funderIdentifierType: str | None = None
    funderIdentifierValue: str | None = None


@dataclass(slots=True)
class FundingInformation:
    """Funding information of the repository. New in schema 4.0.

    Attributes:
        funderName: The name of the funder.
        funderIdentifier: Identifiers of the funder.
        grantIdentifier: The identifier of the grant.
    """

    funderName: str | None = None
    funderIdentifier: list[FunderIdentifier] = field(default_factory=list)
    grantIdentifier: str | None = None


@dataclass(slots=True)
class DatabaseAccess:
    """The access restrictions of the repository database (wrapper element)."""

    databaseAccessType: str | None = None
    databaseAccessRestriction: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DatabaseLicense:
    """The license of the repository database."""

    databaseLicenseName: str | None = None
    databaseLicenseUrl: str | None = None


@dataclass(slots=True)
class DataAccess:
    """The access restrictions of the data (wrapper element)."""

    dataAccessType: str | None = None
    dataAccessRestriction: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DataLicense:
    """The license of the data available in the repository."""

    dataLicenseName: str | None = None
    dataLicenseUrl: str | None = None


@dataclass(slots=True)
class DataUpload:
    """The upload restrictions of the repository (wrapper element)."""

    dataUploadType: str | None = None
    dataUploadRestriction: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DataUploadLicense:
    """The license for data upload."""

    dataUploadLicenseName: str | None = None
    dataUploadLicenseUrl: str | None = None


@dataclass(slots=True)
class Api:
    """An API provided by the repository.

    New in schema 4.0: ``apiUrl`` is a dedicated child element (formerly the
    element text) and ``apiDocumentation`` was added.

    Attributes:
        apiType: The type of the API, e.g. "OAI-PMH", "REST".
        apiUrl: The URL of the API.
        apiDocumentation: URL or text pointing to the API documentation.
    """

    apiType: str | None = None
    apiUrl: str | None = None
    apiDocumentation: str | None = None


@dataclass(slots=True)
class QualityManagementMeasure:
    """A quality management measure. New in schema 4.0."""

    qualityManagementMeasureName: str | None = None
    qualityManagementMeasureUrl: str | None = None


@dataclass(slots=True)
class QualityManagement:
    """Quality management information.

    New in schema 4.0: a wrapper with an explicit status and measures,
    replacing the former yes/no/unknown element.
    """

    qualityManagementStatus: str | None = None
    qualityManagementMeasure: list[QualityManagementMeasure] = field(default_factory=list)


@dataclass(slots=True)
class Certificate:
    """A certificate, seal or standard the repository complies with.

    New in schema 4.0: structured name/dates/url instead of a plain enum value.
    """

    certificateName: str | None = None
    certificateStartDate: date | None = None
    certificateEndDate: date | None = None
    certificateUrl: str | None = None
    certificateWidget: str | None = None


@dataclass(slots=True)
class Profile:
    """A profile the repository complies with, e.g. "Helmholtz Association". New in schema 4.0."""

    profileName: str | None = None
    profileUrl: str | None = None


@dataclass(slots=True)
class MetadataStandard:
    """A metadata standard the repository adheres to."""

    metadataStandardName: str | None = None
    metadataStandardUrl: str | None = None


@dataclass(slots=True)
class Syndication:
    """An alerting service provided by the repository, e.g. RSS."""

    syndicationType: str | None = None
    syndicationUrl: str | None = None


# ------------------------------------------------------------------------------
# Repository and root element
# ------------------------------------------------------------------------------


@dataclass(slots=True)
class Repository:
    """A research data repository described with the re3data schema 4.0.

    Attributes:
        identifiers: The persistent identifiers (re3data id and DOI).
        repositoryName: The full name of the repository.
        additionalName: Alternative names or acronyms of the repository.
        repositoryUrl: The URL referencing the repository.
        repositoryIdentifier: Identifiers referring to the repository.
        description: Textual descriptions of the repository.
        repositoryContact: Contact information of the repository.
        type: The types of the repository.
        size: The number of items contained in the repository.
        startDate: The releasing date of the repository.
        endDate: Details if the repository went offline.
        relatedRepository: Predecessor/successor repositories.
        repositoryLanguage: The user interface languages of the repository.
        subject: The subjects of the repository (DFG classification).
        missionStatementUrl: URL of the mission statement.
        contentType: The types of resources available (COAR resource types).
        providerType: The types of provider.
        keyword: English keywords describing the subject focus.
        institution: The institutions responsible for the repository.
        policy: Policies of the repository.
        fundingInformation: Funding information of the repository.
        databaseAccess: The database access restrictions.
        databaseLicense: The database licenses.
        dataAccess: The data access restrictions.
        dataLicense: The licenses of the data.
        dataUpload: The data upload restrictions.
        dataUploadLicense: The licenses for data upload.
        software: The software used to run the repository.
        versioning: Whether the repository supports versioning ("yes"/"no").
        api: The APIs provided by the repository.
        pidSystem: The persistent identifier systems used.
        citationReference: Citation references (new in 4.0).
        metrics: Metrics in use, e.g. "Altmetric" (new in 4.0).
        citationGuidelineUrl: URL describing how to cite the research data.
        aidSystem: The author identifier systems used.
        enhancedPublication: Whether publications and data are interlinked.
        qualityManagement: Quality management information.
        certificate: Certificates, seals or standards complied with.
        profile: Profiles complied with (new in 4.0).
        metadataStandard: Metadata standards adhered to.
        syndication: Alerting services of the repository.
        remarks: Additional remarks.
        entryDate: The date the repository was indexed in re3data.org.
        lastUpdate: The date the metadata was last updated.
    """

    identifiers: Identifiers | None = None
    repositoryName: RepositoryName | None = None
    additionalName: list[AdditionalName] = field(default_factory=list)
    repositoryUrl: str | None = None
    repositoryIdentifier: list[RepositoryIdentifier] = field(default_factory=list)
    description: list[Description] = field(default_factory=list)
    repositoryContact: list[RepositoryContact] = field(default_factory=list)
    type: list[str] = field(default_factory=list)
    size: str | None = None
    startDate: date | None = None
    endDate: EndDate | None = None
    relatedRepository: list[RelatedRepository] = field(default_factory=list)
    repositoryLanguage: list[str] = field(default_factory=list)
    subject: list[Subject] = field(default_factory=list)
    missionStatementUrl: str | None = None
    contentType: list[ContentType] = field(default_factory=list)
    providerType: list[str] = field(default_factory=list)
    keyword: list[str] = field(default_factory=list)
    institution: list[Institution] = field(default_factory=list)
    policy: list[Policy] = field(default_factory=list)
    fundingInformation: list[FundingInformation] = field(default_factory=list)
    databaseAccess: DatabaseAccess | None = None
    databaseLicense: list[DatabaseLicense] = field(default_factory=list)
    dataAccess: list[DataAccess] = field(default_factory=list)
    dataLicense: list[DataLicense] = field(default_factory=list)
    dataUpload: list[DataUpload] = field(default_factory=list)
    dataUploadLicense: list[DataUploadLicense] = field(default_factory=list)
    software: list[str] = field(default_factory=list)
    versioning: str | None = None
    api: list[Api] = field(default_factory=list)
    pidSystem: list[str] = field(default_factory=list)
    citationReference: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    citationGuidelineUrl: str | None = None
    aidSystem: list[str] = field(default_factory=list)
    enhancedPublication: str | None = None
    qualityManagement: QualityManagement | None = None
    certificate: list[Certificate] = field(default_factory=list)
    profile: list[Profile] = field(default_factory=list)
    metadataStandard: list[MetadataStandard] = field(default_factory=list)
    syndication: list[Syndication] = field(default_factory=list)
    remarks: str | None = None
    entryDate: date | None = None
    lastUpdate: date | None = None

    @property
    def id(self) -> str | None:
        """The re3data identifier of the repository."""
        return self.identifiers.re3data if self.identifiers else None


@dataclass(slots=True)
class Re3Data:
    """The root element of a repository detail response."""

    repository: list[Repository] = field(default_factory=list)
