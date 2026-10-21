import socket

import pytest
from fastapi import HTTPException

from app.services import security


def test_metadata_ip_is_always_rejected():
    with pytest.raises(HTTPException, match="metadata"):
        security.validate_target_url("http://169.254.169.254/latest/meta-data")


def test_private_addresses_can_be_disabled(monkeypatch):
    monkeypatch.setattr(security.settings, "allow_private_targets", False)
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [(None, None, None, None, ("127.0.0.1", 0))])
    with pytest.raises(HTTPException, match="Private network"):
        security.validate_target_url("http://example.test")
