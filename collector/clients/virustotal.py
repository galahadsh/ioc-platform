import base64
from dataclasses import dataclass
from typing import Any

import requests

from config import (
    VT_API_KEY,
    VT_BASE_URL,
    VT_REQUEST_TIMEOUT,
)


@dataclass
class VTResponse:
    success: bool
    status_code: int | None
    attributes: dict[str, Any] | None = None
    error: str | None = None
    retryable: bool = False


class VirusTotalClient:
    def __init__(self) -> None:
        self.headers = {
            "x-apikey": VT_API_KEY,
        }

    @staticmethod
    def _url_id(value: str) -> str:
        encoded = base64.urlsafe_b64encode(
            value.encode("utf-8")
        ).decode("utf-8")

        return encoded.rstrip("=")

    def _build_url(
        self,
        ioc_type: str,
        value: str,
    ) -> str | None:
        if ioc_type == "ip":
            return f"{VT_BASE_URL}/ip_addresses/{value}"

        if ioc_type == "domain":
            return f"{VT_BASE_URL}/domains/{value}"

        if ioc_type in {"md5", "sha1", "sha256"}:
            return f"{VT_BASE_URL}/files/{value}"

        if ioc_type == "url":
            return (
                f"{VT_BASE_URL}/urls/"
                f"{self._url_id(value)}"
            )

        return None

    def lookup(
        self,
        ioc_type: str,
        value: str,
    ) -> VTResponse:
        url = self._build_url(ioc_type, value)

        if not url:
            return VTResponse(
                success=False,
                status_code=None,
                error=f"Tipo de IOC no soportado: {ioc_type}",
                retryable=False,
            )

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=VT_REQUEST_TIMEOUT,
            )

        except requests.Timeout:
            return VTResponse(
                success=False,
                status_code=None,
                error="Timeout consultando VirusTotal",
                retryable=True,
            )

        except requests.RequestException as exc:
            return VTResponse(
                success=False,
                status_code=None,
                error=f"Error de red: {exc}",
                retryable=True,
            )

        if response.status_code == 200:
            try:
                attributes = response.json()["data"]["attributes"]
            except (ValueError, KeyError, TypeError):
                return VTResponse(
                    success=False,
                    status_code=200,
                    error="Respuesta inválida de VirusTotal",
                    retryable=False,
                )

            return VTResponse(
                success=True,
                status_code=200,
                attributes=attributes,
            )

        if response.status_code == 404:
            return VTResponse(
                success=False,
                status_code=404,
                error="IOC no encontrado en VirusTotal",
                retryable=False,
            )

        if response.status_code == 429:
            return VTResponse(
                success=False,
                status_code=429,
                error="Límite de consultas de VirusTotal",
                retryable=True,
            )

        if response.status_code in {500, 502, 503, 504}:
            return VTResponse(
                success=False,
                status_code=response.status_code,
                error="Error temporal de VirusTotal",
                retryable=True,
            )

        if response.status_code in {401, 403}:
            return VTResponse(
                success=False,
                status_code=response.status_code,
                error="API key inválida o sin permisos",
                retryable=False,
            )

        return VTResponse(
            success=False,
            status_code=response.status_code,
            error=f"Respuesta HTTP {response.status_code}",
            retryable=False,
        )
