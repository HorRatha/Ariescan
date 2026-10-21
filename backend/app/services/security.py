import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException

from ..core.config import settings

SENSITIVE = {"authorization", "cookie", "set-cookie", "api-key", "password", "token", "secret"}


def validate_target_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(422, "URL must be an absolute HTTP(S) URL")
    host = parsed.hostname.lower()
    if host in {"169.254.169.254", "metadata.google.internal"}:
        raise HTTPException(422, "Cloud metadata targets are blocked")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)}
    except socket.gaierror:
        raise HTTPException(422, "Target host could not be resolved")
    for raw_address in addresses:
        address = ipaddress.ip_address(raw_address)
        if address.is_multicast or address.is_unspecified or address.is_reserved:
            raise HTTPException(422, "Unsafe target address is blocked")
        if (address.is_private or address.is_loopback or address.is_link_local) and not settings.allow_private_targets:
            raise HTTPException(422, "Private network targets are disabled")
    return value.rstrip("/")


def redact(value):
    if isinstance(value, dict):
        return {
            k: ("[REDACTED]" if any(marker in k.lower() for marker in SENSITIVE) else redact(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value
