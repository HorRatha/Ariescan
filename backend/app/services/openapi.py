import json

import yaml
from fastapi import HTTPException

METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def parse_document(content):
    try:
        data = json.loads(content)
        fmt = "json"
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(content)
            fmt = "yaml"
        except yaml.YAMLError as e:
            raise HTTPException(422, f"Invalid OpenAPI document: {e}")
    if not isinstance(data, dict) or not str(data.get("openapi", "")).startswith("3."):
        raise HTTPException(422, "Only OpenAPI 3.x documents are supported")
    if not isinstance(data.get("paths"), dict):
        raise HTTPException(422, "OpenAPI document has no paths")
    return data, fmt


def resolve(spec, value):
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    node = spec
    try:
        for part in value["$ref"].removeprefix("#/").split("/"):
            node = node[part]
        return node
    except (KeyError, TypeError):
        return value


def dereference(spec, value, seen=None):
    """Inline local OpenAPI references so stored schemas are self-contained."""
    seen = seen or set()
    if isinstance(value, list):
        return [dereference(spec, item, seen.copy()) for item in value]
    if not isinstance(value, dict):
        return value
    ref = value.get("$ref")
    if ref:
        if ref in seen or not ref.startswith("#/"):
            return value
        return dereference(spec, resolve(spec, value), seen | {ref})
    return {key: dereference(spec, item, seen.copy()) for key, item in value.items()}


def extract_endpoints(spec):
    result = []
    for path, item in spec["paths"].items():
        shared = item.get("parameters", []) if isinstance(item, dict) else []
        for method, operation in item.items():
            if method.lower() not in METHODS or not isinstance(operation, dict):
                continue
            params = [resolve(spec, p) for p in shared + operation.get("parameters", [])]
            body = resolve(spec, operation.get("requestBody", {}))
            request_schema = (
                dereference(spec, next(iter(body.get("content", {}).values()), {}).get("schema")) if body else None
            )
            responses = {}
            for code, response in operation.get("responses", {}).items():
                response = resolve(spec, response)
                schema = next(iter(response.get("content", {}).values()), {}).get("schema") or {}
                responses[str(code)] = dereference(spec, schema)
            result.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "summary": operation.get("summary") or operation.get("description"),
                    "parameters": params,
                    "request_schema": request_schema,
                    "response_schemas": responses,
                }
            )
    return result
