from __future__ import annotations

from pathlib import Path
import os
from typing import Any

import requests


DEFAULT_BASE_URL = "https://any.webprinter.cn"
TOKEN_HELP_URL = "http://get-ai-token.webprinter.cn"
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


def build_token_help_message(detail: str | None = None) -> str:
    base = (
        "WebPrinter token is missing or invalid. "
        f"Please get a token from {TOKEN_HELP_URL} and set WEBPRINTER_ACCESS_TOKEN."
    )
    if detail:
        return f"{base} Upstream detail: {detail}"
    return base


def build_hidden_printer_message(printer_name: str | None = None) -> str:
    target = f"Printer '{printer_name}'" if printer_name else "This printer"
    return f"{target} is hidden and only supports roaming print tasks. Please create a roaming task instead of direct printing."


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
            raise CloudPrintError(build_token_help_message())

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
        self._raise_for_http_error(response)
        return {"success": True, "taskId": response.text.strip()}

    @staticmethod
    def _iter_printer_records(payload: Any) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    records.append(item)
            return records
        if isinstance(payload, dict):
            for key in ("data", "rows", "list", "records", "result"):
                value = payload.get(key)
                if isinstance(value, list):
                    records.extend(item for item in value if isinstance(item, dict))
                elif isinstance(value, dict):
                    records.extend(CloudPrintClient._iter_printer_records(value))
        return records

    @staticmethod
    def _normalize_hidden_printers(payload: dict[str, Any]) -> dict[str, Any]:
        for printer in CloudPrintClient._iter_printer_records(payload):
            if printer.get("hidden") is True:
                printer["directPrintAllowed"] = False
                printer["usageHint"] = "This printer is hidden and only supports roaming print tasks."
            elif "directPrintAllowed" not in printer:
                printer["directPrintAllowed"] = True
        return payload

    def _find_printer_for_direct_print(self, device_name: str, control_sn: str) -> dict[str, Any] | None:
        payload = self.query_printers()
        normalized_device_name = device_name.strip()
        normalized_control_sn = control_sn.strip()
        for printer in self._iter_printer_records(payload):
            candidate_names = {
                str(printer.get("deviceName", "")).strip(),
                str(printer.get("printerName", "")).strip(),
                str(printer.get("name", "")).strip(),
                str(printer.get("alias", "")).strip(),
            }
            candidate_serials = {
                str(printer.get("controlSn", "")).strip(),
                str(printer.get("shareSn", "")).strip(),
                str(printer.get("sn", "")).strip(),
            }
            if normalized_device_name in candidate_names and normalized_control_sn in candidate_serials:
                return printer
        return None

    @staticmethod
    def _raise_for_http_error(response: requests.Response) -> None:
        if response.status_code in {401, 403}:
            detail = response.text.strip() or None
            raise CloudPrintError(build_token_help_message(detail))
        response.raise_for_status()

    @staticmethod
    def _looks_like_auth_error(detail: str) -> bool:
        lowered = detail.lower()
        auth_markers = (
            "login",
            "not login",
            "not logged in",
            "unauthorized",
            "authorization",
            "access token",
            "token",
            "未登录",
            "未授权",
            "未认证",
            "登录",
            "令牌",
            "token无效",
            "token失效",
        )
        return any(marker in lowered for marker in auth_markers)

    @classmethod
    def _parse_json_response(cls, response: requests.Response) -> dict[str, Any]:
        cls._raise_for_http_error(response)
        data = response.json()
        if isinstance(data, dict):
            detail = None
            for key in ("error", "message", "msg"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    detail = value.strip()
                    break
            code = data.get("code")
            success = data.get("success")
            if detail and cls._looks_like_auth_error(detail):
                raise CloudPrintError(build_token_help_message(detail))
            if code in {401, 403}:
                raise CloudPrintError(build_token_help_message(detail))
            if success is False and detail:
                raise CloudPrintError(detail)
            if data.get("error"):
                raise CloudPrintError(str(data["error"]))
        return data

    def check_install_progress(self) -> dict[str, Any]:
        return self._post_json("/openapi/platform/checkInstallProgressMCP")

    def query_printers(self) -> dict[str, Any]:
        return self._normalize_hidden_printers(self._post_json("/openapi/control/queryPrinters"))

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
        printer = self._find_printer_for_direct_print(device_name=device_name, control_sn=control_sn)
        if printer and printer.get("hidden") is True:
            printer_name = (
                str(printer.get("deviceName") or "").strip()
                or str(printer.get("printerName") or "").strip()
                or device_name
            )
            raise CloudPrintError(build_hidden_printer_message(printer_name))
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
