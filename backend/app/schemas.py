from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    base_url: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    base_url: str | None = None
    description: str | None = None


class ProjectOut(ProjectCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ImportSpec(BaseModel):
    document_url: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def exactly_one_source(self):
        if bool(self.document_url) == bool(self.content):
            raise ValueError("Provide exactly one of document_url or content")
        return self


class EndpointOut(BaseModel):
    id: str
    method: str
    path: str
    summary: str | None
    parameters: list
    request_schema: dict | None
    response_schemas: dict
    model_config = {"from_attributes": True}


class TestCaseOut(BaseModel):
    id: str
    endpoint_id: str
    name: str
    test_type: str
    request_data: dict
    expected_result: dict
    enabled: bool
    model_config = {"from_attributes": True}


class TestRunOut(BaseModel):
    id: str
    project_id: str
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    started_at: datetime | None
    finished_at: datetime | None
    model_config = {"from_attributes": True}


class TestResultOut(BaseModel):
    id: str
    test_run_id: str
    test_case_id: str
    status: str
    actual_status_code: int | None
    expected_result: dict
    actual_result: dict
    error_message: str | None
    duration_ms: int | None
    executed_at: datetime
    model_config = {"from_attributes": True}
