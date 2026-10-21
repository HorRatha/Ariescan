from app.services.openapi import extract_endpoints, parse_document

DOCUMENT = """
openapi: 3.0.3
info: {title: Demo API, version: '1.0'}
paths:
  /products/{product_id}:
    parameters:
      - name: product_id
        in: path
        required: true
        schema: {type: integer}
    get:
      summary: Get a product
      responses:
        '200':
          description: Found
          content:
            application/json:
              schema: {type: object}
"""


def test_parses_openapi_yaml_and_discovers_endpoint():
    spec, document_format = parse_document(DOCUMENT)
    endpoints = extract_endpoints(spec)

    assert document_format == "yaml"
    assert endpoints == [
        {
            "method": "GET",
            "path": "/products/{product_id}",
            "summary": "Get a product",
            "parameters": [{"name": "product_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "request_schema": None,
            "response_schemas": {"200": {"type": "object"}},
        }
    ]
