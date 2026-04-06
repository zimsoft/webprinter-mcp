from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .client import CloudPrintClient, SUPPORTED_MEDIA_FORMATS


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
