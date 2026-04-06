from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import CloudPrintClient, PAPER_SIZE_DIMENSIONS_MM, SUPPORTED_MEDIA_FORMATS


app = FastMCP(
    name="webprinter",
    instructions=(
        "Tools for WebPrinter cloud printing, including installation checks, "
        "file upload, printer queries, roaming print tasks, and direct print jobs."
    ),
)


def get_client() -> CloudPrintClient:
    return CloudPrintClient()


@app.tool()
def check_install_progress() -> dict:
    """Check whether the user's cloud print environment is fully configured."""
    return get_client().check_install_progress()


@app.tool()
def query_printers() -> dict:
    """List printers available to the current user."""
    return get_client().query_printers()


@app.tool()
def query_printer_detail(
    printer_name: str | None = None,
    share_sn: str | None = None,
    device_type: str | None = None,
) -> dict:
    """Query printer capabilities for a specific printer or shared device."""
    return get_client().query_printer_detail(
        printer_name=printer_name,
        share_sn=share_sn,
        device_type=device_type,
    )


@app.tool()
def upload_file(file_path: str) -> dict:
    """Upload a local file and return a public URL that the print service can read."""
    return get_client().upload_file(file_path)


@app.tool()
def create_roaming_task(file_name: str, url: str, media_format: str) -> dict:
    """Create a roaming print task from a public document URL."""
    normalized = media_format.upper()
    if normalized not in SUPPORTED_MEDIA_FORMATS:
        raise ValueError(f"Unsupported media_format: {media_format}")
    return get_client().create_roaming_task(
        file_name=file_name,
        url=url,
        media_format=normalized,
    )


@app.tool()
def update_printer_side(task_id: str, side: str | None = None) -> dict:
    """Update simplex or duplex settings for an existing roaming task."""
    return get_client().update_printer_side(task_id=task_id, side=side)


@app.tool()
def update_printer_color(task_id: str, color: str | None = None) -> dict:
    """Update color mode for an existing roaming task."""
    normalized = color.upper() if color else None
    if normalized not in {None, "COLOR", "MONOCHROME"}:
        raise ValueError(f"Unsupported color: {color}")
    return get_client().update_printer_color(task_id=task_id, color=normalized)


@app.tool()
def update_printer_copies(task_id: str, copies: int) -> dict:
    """Update copy count for an existing roaming task."""
    if copies < 1:
        raise ValueError("copies must be greater than or equal to 1")
    return get_client().update_printer_copies(task_id=task_id, copies=copies)


@app.tool()
def update_printer_paper(task_id: str, paper: str | dict[str, Any]) -> dict:
    """Update paper size for an existing roaming task using a preset name or custom dimensions in millimeters."""
    normalized_paper = _normalize_paper_config(paper)
    return get_client().update_printer_paper(task_id=task_id, paper=normalized_paper)


@app.tool()
def direct_print_document(
    file_name: str,
    url: str,
    media_format: str,
    device_name: str,
    control_sn: str,
) -> dict:
    """Send a document directly to a specific printer."""
    normalized = media_format.upper()
    if normalized not in SUPPORTED_MEDIA_FORMATS:
        raise ValueError(f"Unsupported media_format: {media_format}")
    return get_client().direct_print_document(
        file_name=file_name,
        url=url,
        media_format=normalized,
        device_name=device_name,
        control_sn=control_sn,
    )


def _normalize_paper_config(paper: str | dict[str, Any]) -> dict[str, float]:
    if isinstance(paper, str):
        normalized = paper.strip().upper().replace(" ", "")
        if normalized in PAPER_SIZE_DIMENSIONS_MM:
            width, height = PAPER_SIZE_DIMENSIONS_MM[normalized]
            return {"width": width, "height": height}
        raise ValueError(f"Unsupported paper preset: {paper}")

    if isinstance(paper, dict):
        width = paper.get("width")
        height = paper.get("height")
        if width is None or height is None:
            raise ValueError("paper must include width and height")
        try:
            normalized_width = float(width)
            normalized_height = float(height)
        except (TypeError, ValueError) as exc:
            raise ValueError("paper width and height must be numbers") from exc
        if normalized_width <= 0 or normalized_height <= 0:
            raise ValueError("paper width and height must be greater than 0")
        return {"width": normalized_width, "height": normalized_height}

    raise ValueError("paper must be a preset name like 'A4' or an object with width and height")
