from ..core.config import settings
from ..models import TestCase


def example_for(schema):
    if not schema:
        return None
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    if schema.get("type") == "object":
        return {k: example_for(v) for k, v in schema.get("properties", {}).items() if k in schema.get("required", [])}
    return {"string": "example", "integer": 1, "number": 1.0, "boolean": True, "array": []}.get(schema.get("type"))


def generate(endpoint):
    codes = [int(k) for k in endpoint.response_schemas if k.isdigit() and 200 <= int(k) < 300]
    success = min(codes) if codes else 200
    cases = []
    query = {
        p["name"]: example_for(p.get("schema", {}))
        for p in endpoint.parameters
        if p.get("in") == "query" and p.get("required")
    }
    if endpoint.method != "DELETE" or settings.allow_destructive_tests:
        cases.append(
            TestCase(
                endpoint_id=endpoint.id,
                name="Documented valid request",
                test_type="valid_request",
                request_data={"json": example_for(endpoint.request_schema), "params": query},
                expected_result={"status_codes": [success], "schema": endpoint.response_schemas.get(str(success), {})},
            )
        )
    required = [p for p in endpoint.parameters if p.get("required") and p.get("in") == "query"]
    if required:
        cases.append(
            TestCase(
                endpoint_id=endpoint.id,
                name="Missing required parameter",
                test_type="missing_required_parameter",
                request_data={"omit_parameter": required[0].get("name")},
                expected_result={"status_codes": [400, 422]},
            )
        )
    schema = endpoint.request_schema or {}
    fields = schema.get("required", [])
    if fields:
        payload = example_for(schema) or {}
        payload.pop(fields[0], None)
        cases.append(
            TestCase(
                endpoint_id=endpoint.id,
                name=f"Missing required field: {fields[0]}",
                test_type="missing_required_field",
                request_data={"json": payload},
                expected_result={"status_codes": [400, 422]},
            )
        )
    return cases
