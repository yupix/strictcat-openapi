from typing import Optional, TypedDict


class IOpenAPIRequestBody(TypedDict):
    required: bool
    content: dict[str, dict[str, dict:[str, str]]]


class IOpenAPIParameter(TypedDict):
    name: str
    required: bool
    schema: dict[str, str]


class IOpenAPIPath(TypedDict):
    operationId: str
    parameters: list[IOpenAPIParameter]
    requestBody: Optional[IOpenAPIRequestBody]
    reposnses: dict[str : dict[str, str]]


class IOpenAPI(TypedDict):
    openapi: str
    paths: dict[dict[str, dict[str, IOpenAPIPath]]]


class IEnv(TypedDict):
    OPENAPI_URL: str
    USE_EXPORT: str
    USE_DEFAULT_VALUE: str
    EXPORT_SCHEMA_PATH: list[str]

