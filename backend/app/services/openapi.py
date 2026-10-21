import json
import re
from urllib.parse import parse_qsl, urlparse

import yaml
from fastapi import HTTPException

METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _schema_for_value(value):
    """Create a small JSON Schema from a Postman example value."""
    if isinstance(value, dict):
        return {
            "type": "object",
            "properties": {key: _schema_for_value(item) for key, item in value.items()},
            "required": list(value),
            "example": value,
        }
    if isinstance(value, list):
        return {"type": "array", "items": _schema_for_value(value[0]) if value else {}, "example": value}
    if isinstance(value, bool):
        return {"type": "boolean", "example": value}
    if isinstance(value, int):
        return {"type": "integer", "example": value}
    if isinstance(value, float):
        return {"type": "number", "example": value}
    return {"type": "string", "example": value}


def _postman_path(request):
    url = request.get("url", {})
    raw = url.get("raw", "") if isinstance(url, dict) else str(url)
    parsed = urlparse(raw)
    path = parsed.path or "/"
    if not path and isinstance(url, dict):
        parts = url.get("path", [])
        path = "/" + "/".join(parts if isinstance(parts, list) else [str(parts)])
    return re.sub(r":([A-Za-z_][A-Za-z0-9_-]*)", r"{\1}", path)


def postman_to_openapi(collection):
    """Normalize a Postman Collection v2 JSON export for the existing test pipeline."""
    info = collection.get("info", {})
    paths = {}

    def visit(items):
        for item in items or []:
            if "item" in item:
                visit(item["item"])
                continue
            request = item.get("request", {})
            if not isinstance(request, dict) or request.get("method", "").lower() not in METHODS:
                continue
            method = request["method"].lower()
            path = _postman_path(request)
            parameters = []
            raw_url = request.get("url", {})
            queries = raw_url.get("query", []) if isinstance(raw_url, dict) else parse_qsl(urlparse(str(raw_url)).query)
            for query in queries:
                if isinstance(query, tuple):
                    key, value = query
                    disabled = False
                else:
                    key, value = query.get("key"), query.get("value", "")
                    disabled = query.get("disabled", False)
                if key and not disabled:
                    parameters.append(
                        {"name": key, "in": "query", "required": False, "schema": {"type": "string", "example": value}}
                    )
            for name in re.findall(r"\{([^}]+)\}", path):
                parameters.append(
                    {"name": name, "in": "path", "required": True, "schema": {"type": "string", "example": "1"}}
                )
            operation = {
                "summary": item.get("name"),
                "parameters": parameters,
                "responses": {"200": {"description": "Documented request"}},
            }
            body = request.get("body", {})
            if body.get("mode") == "raw" and body.get("raw"):
                try:
                    example = json.loads(body["raw"])
                    operation["requestBody"] = {"content": {"application/json": {"schema": _schema_for_value(example)}}}
                except json.JSONDecodeError:
                    pass
            paths.setdefault(path, {})[method] = operation

    visit(collection.get("item", []))
    return {
        "openapi": "3.0.3",
        "info": {"title": info.get("name", "Postman Collection"), "version": "postman"},
        "paths": paths,
    }


def parse_document(content):
    if "documenter.getpostman.com" in content.lower() or "<html" in content[:500].lower():
        raise HTTPException(
            422,
            "That URL is a Postman documentation webpage, not an API definition. "
            "Export its collection as JSON and upload it, or provide the API's OpenAPI JSON/YAML URL.",
        )
    try:
        data = json.loads(content)
        fmt = "json"
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(content)
            fmt = "yaml"
        except yaml.YAMLError as e:
            raise HTTPException(422, f"Invalid OpenAPI document: {e}")
    if isinstance(data, dict) and str(data.get("info", {}).get("schema", "")).startswith(
        "https://schema.getpostman.com/json/collection/"
    ):
        data = postman_to_openapi(data)
        fmt = "postman-collection"
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
