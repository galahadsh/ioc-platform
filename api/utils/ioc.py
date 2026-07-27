import ipaddress
import re
from urllib.parse import urlparse


HASH_PATTERNS = {
    "md5": re.compile(r"^[a-fA-F0-9]{32}$"),
    "sha1": re.compile(r"^[a-fA-F0-9]{40}$"),
    "sha256": re.compile(r"^[a-fA-F0-9]{64}$"),
}


def detectar_tipo(valor: str) -> str:
    valor = valor.strip()

    if not valor:
        return "unknown"

    try:
        ipaddress.ip_address(valor)
        return "ip"
    except ValueError:
        pass

    for tipo, patron in HASH_PATTERNS.items():
        if patron.fullmatch(valor):
            return tipo

    parsed = urlparse(valor)

    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return "url"

    return "domain"