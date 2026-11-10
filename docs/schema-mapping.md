# Schema 2-2 → 4-0 字段对照表

来源：schema 2-2（python-re3data 0.10.0 内嵌 XSD）与 [schema 4.0 XSD](https://schema.re3data.org/4-0/re3dataV4-0.xsd) 逐字段比对，并经真实 v40 API 响应验证。

图例：`→` 重命名/重组；`+` 4.0 新增；`−` 4.0 移除；`≈` 结构微调。

## Repository 顶层字段

| schema 2-2 | schema 4.0 | 备注 |
|---|---|---|
| `re3data.orgIdentifier` | `identifiers/re3data` | 结构重组 |
| — | `identifiers/doi` | + DOI 成为一级字段 |
| `repositoryName` | `repositoryName` | 保留（value + @language） |
| `additionalName` | `additionalName` | 保留 |
| `repositoryURL` | `repositoryUrl` | 命名统一小写 url |
| `repositoryIdentifier` (str 列表) | `repositoryIdentifier{Type,Value}` | ≈ 结构化 |
| `description` | `description` | 保留 |
| `repositoryContact` (str 列表) | `repositoryContact{Information,Type}` | ≈ 结构化 |
| `type` (3 值枚举) | `type` (6 值) | + governmental, multidisciplinary, project-related |
| `size` (+@updated) | `size` (纯文本) | − updated 日期属性 |
| `startDate` | `startDate` | 保留 |
| `endDate` (日期) | `endDate{closed,offline}` | ≈ 标志位 |
| — | `relatedRepository{Id,Type}` | + 前任/后任库 |
| `repositoryLanguage` | `repositoryLanguage` | 保留 |
| `subject{value,@subjectScheme}` | `subject{subjectId,subjectName,@subjectScheme}` | ≈ DFG 数字 ID 体系 |
| `missionStatementURL` | `missionStatementUrl` | 命名 |
| `contentType{value,@contentTypeScheme}` | `contentType{contentTypeId,contentTypeName,@contentTypeScheme}` | ≈ COAR URI 体系 |
| `providerType` | `providerType` | 保留 |
| `keyword` | `keyword` | 保留 |
| `institution` | `institution` | 见下 |
| `policy{policyName,policyURL}` | `policy{policyName,policyUrl}` | 命名 |
| — | `fundingInformation` | + 资助信息 |
| `databaseAccess` | `databaseAccess` | 保留（restriction 去掉 other） |
| `databaseLicense{Name,URL}` | `databaseLicense{Name,Url}` | 命名；Name 放宽为 str |
| `dataAccess` | `dataAccess` | restriction 值 `"institutional membership"`→`institutionalMembership`（实测数据仍带空格） |
| `dataLicense{Name,URL}` | `dataLicense{Name,Url}` | 命名；Name 放宽 |
| `dataUpload` | `dataUpload` | + storageLimit |
| `dataUploadLicense{Name,URL}` | `dataUploadLicense{Name,Url}` | 命名 |
| `software` (SoftwareNames 枚举) | `software` (str) | 放宽 |
| `versioning` | `versioning` | 保留 |
| `api{value,@apiType}` | `api{apiType,apiUrl,apiDocumentation}` | ≈ 结构化 + 文档链接 |
| `pidSystem` (枚举) | `pidSystem` (str) | 放宽 |
| — | `citationReference` | + |
| — | `metrics` | + |
| `citationGuidelineURL` | `citationGuidelineUrl` | 命名 |
| `aidSystem` (枚举) | `aidSystem` (str) | 放宽 |
| `enhancedPublication` | `enhancedPublication` | 保留 |
| `qualityManagement` (yes/no/unknown) | `qualityManagement{Status,Measure[]}` | ≈ 结构化 |
| `certificate` (枚举列表) | `certificate{Name,StartDate,EndDate,Url,Widget}` | ≈ 结构化 |
| — | `profile{Name,Url}` | + |
| `metadataStandard{Name,URL,@scheme}` | `metadataStandard{Name,Url}` | 命名；无 scheme |
| `syndication{value,@syndicationType}` | `syndication{syndicationType,syndicationUrl}` | ≈ 结构化 |
| `remarks` | `remarks` | 保留 |
| `entryDate` | `entryDate` | 保留 |
| `lastUpdate` | `lastUpdate` | 保留 |

## Institution 字段

| schema 2-2 | schema 4.0 | 备注 |
|---|---|---|
| `institutionName` | `institutionName` | 保留 |
| `institutionAdditionalName` | `institutionAdditionalName` | 保留 |
| `institutionCountry` | `institutionCountry` | 保留（ISO 3166-1 alpha-3） |
| `responsibilityType` | `responsibilityType` | − sponsoring |
| `institutionType` | `institutionType` | 保留 commercial/non-profit |
| `institutionURL` | `institutionUrl` | 命名 |
| `institutionIdentifier` (str 列表) | `institutionIdentifier{Type,Url}` | ≈ 结构化（ROR/RRID 等） |
| — | `responsibilityStartDate` | + |
| — | `responsibilityEndDate` | + |

## FundingInformation（4.0 新增）

| 字段 | 类型 |
|---|---|
| `funderName` | str |
| `funderIdentifier{funderIdentifierType, funderIdentifierValue}` | 列表 |
| `grantIdentifier` | str，可选 |

## 值域速查（4.0）

- `repositoryType`: disciplinary, governmental, institutional, multidisciplinary, project-related, other
- `dataAccessType`: open, embargoed, restricted, closed
- `dataAccessRestriction`: feeRequired, institutionalMembership, registration
- `dataUploadType`: open, restricted, closed
- `dataUploadRestriction`: feeRequired, institutionalMembership, registration, storageLimit
- `databaseAccessType`: open, restricted, closed
- `databaseAccessRestriction`: feeRequired, registration
- `institutionType`: commercial, non-profit
- `responsibilityType`: funding, general, technical
- `relatedRepositoryType`: predecessor, successor
- `subjectId/subjectName`: DFG 分类 281 项
- `contentTypeId/contentTypeName`: COAR resource type 22 项（如 `http://purl.org/coar/resource_type/c_ddb1` / dataset）
