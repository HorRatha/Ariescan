import json

import pytest
from fastapi import HTTPException

from app.services.openapi import extract_endpoints, parse_document

POSTMAN_COLLECTION = json.dumps(
    {
        "info": {
            "name": "Sample deployed API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Create a user",
                "request": {
                    "method": "POST",
                    "url": {
                        "raw": "https://api.example.com/users/:userId?verbose=true",
                        "query": [{"key": "verbose", "value": "true"}],
                    },
                    "body": {"mode": "raw", "raw": '{"name": "Ada"}'},
                },
            }
        ],
    }
)


def test_parses_postman_collection_export():
    spec, document_format = parse_document(POSTMAN_COLLECTION)
    endpoint = extract_endpoints(spec)[0]

    assert document_format == "postman-collection"
    assert endpoint["method"] == "POST"
    assert endpoint["path"] == "/users/{userId}"
    assert endpoint["request_schema"]["example"] == {"name": "Ada"}
    assert {item["name"] for item in endpoint["parameters"]} == {"userId", "verbose"}


def test_rejects_postman_documenter_page_with_an_actionable_error():
    with pytest.raises(HTTPException, match="Postman documentation webpage"):
        parse_document("<html><script>documenter.getpostman.com</script></html>")
