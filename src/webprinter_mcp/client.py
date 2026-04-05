from __future__ import annotations

from pathlib import Path
import os
from typing import Any

import requests


DEFAULT_BASE_URL = "https://any.webprinter.cn"
SUPPORTED_MEDIA_FORMATS = (
    "HTML",
    "PNG",
    "JPG",
    "PDF",
    "BMP",
    "WEBP",
    "WORD",
    "EXCEL",
    "PPT",
    "TEXT",
    "WPS",
    "ODF",
    "ODT",
    "ODS",
    "ODP",
    "ODG",
    "XPS",
    "PWG",
)


class CloudPrintError(RuntimeError):
    """Raised when the upstream cloud print API returns an error."""


class CloudPrintClient:
    """Small wrapper around the WebPrinter open API."""

    def __init__(
        self,
        access_token: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        token = access_token or os.getenv("WEBPRINTER_ACCESS_TOKEN")

        if not token:
            raise CloudPrintError(
                "Missing access token. Set WEBPRINTER_ACCESS_TOKEN first."
            )

        self.base_url = (base_url or os.getenv("WEBPRINTER_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _post_json(self, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=payload or {},
            timeout=self.timeout,
        )
        return self._parse_json_response(response)

    def _post_text(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return {"success": True, "taskId": response.text.strip()}

    @staticmethod
    def _parse_json_response(response: requests.Response) -> dict[str, Any]:
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise CloudPrintError(str(data["error"]))
        return data

    def check_install_progress(self) -> dict[str, Any]:
        return self._post_json("/openapi/platform/checkInstallProgressMCP")

    def query_printers(self) -> dict[str, Any]:
        return self._post_json("/openapi/control/queryPrinters")

    def upload_file(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            raise CloudPrintError(f"File does not exist: {path}")
        with path.open("rb") as handle:
            response = self.session.post(
                f"{self.base_url}/openapi/mcpClient/uploadFileMCP",
                files={"file": (path.name, handle)},
                headers={"Authorization": self.session.headers["Authorization"]},
                timeout=max(self.timeout, 60.0),
            )
        return self._parse_json_response(response)

    def query_printer_detail(
        self,
        printer_name: str | None = None,
        share_sn: str | None = None,
        device_type: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if printer_name:
            payload["printerName"] = printer_name
        if share_sn:
            payload["shareSn"] = share_sn
        if device_type:
            payload["deviceType"] = device_type
        return self._post_json("/openapi/control/queryPrinterDetail", payload)

    def create_roaming_task(
        self,
        file_name: str,
        url: str,
        media_format: str,
    ) -> dict[str, Any]:
        return self._post_text(
            "/openapi/task/createRoamingTask",
            {
                "fileName": file_name,
                "url": url,
                "mediaFormat": media_format,
            },
        )

    def update_printer_side(self, task_id: str, side: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"taskId": task_id}
        if side:
            payload["side"] = side
        return self._post_json("/openapi/task/config/updatePrinterSideMCP", payload)

    def direct_print_document(
        self,
        file_name: str,
        url: str,
        media_format: str,
        device_name: str,
        control_sn: str,
    ) -> dict[str, Any]:
        return self._post_json(
            "/openapi/task/directPrintDocumentMCP",
            {
                "fileName": file_name,
                "url": url,
                "mediaFormat": media_format,
                "deviceName": device_name,
                "controlSn": control_sn,
            },
        )
