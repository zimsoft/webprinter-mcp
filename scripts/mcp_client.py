#!/usr/bin/env python3
"""CLI helper for manually testing the WebPrinter MCP backend."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from webprinter_mcp.client import CloudPrintClient


def print_result(result: dict[str, Any]) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ZIM / WebPrinter cloud print CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check-install-progress", help="Check installation progress")
    subparsers.add_parser("query-printers", help="Query printers")

    upload_parser = subparsers.add_parser("upload-file", help="Upload a local file")
    upload_parser.add_argument("--file-path", required=True)

    detail_parser = subparsers.add_parser("query-printer-detail", help="Query printer detail")
    detail_parser.add_argument("--printer-name")
    detail_parser.add_argument("--share-sn")
    detail_parser.add_argument("--device-type", choices=["printer", "scanner", "camera"])

    roaming_parser = subparsers.add_parser("create-roaming-task", help="Create roaming task")
    roaming_parser.add_argument("--file-name", required=True)
    roaming_parser.add_argument("--url", required=True)
    roaming_parser.add_argument("--media-format", required=True)

    side_parser = subparsers.add_parser("update-printer-side", help="Update simplex/duplex mode")
    side_parser.add_argument("--task-id", required=True)
    side_parser.add_argument("--side", choices=["ONESIDE", "DUPLEX", "TUMBLE"])

    color_parser = subparsers.add_parser("update-printer-color", help="Update color mode")
    color_parser.add_argument("--task-id", required=True)
    color_parser.add_argument("--color", choices=["COLOR", "MONOCHROME"])

    copies_parser = subparsers.add_parser("update-printer-copies", help="Update print copies")
    copies_parser.add_argument("--task-id", required=True)
    copies_parser.add_argument("--copies", required=True, type=int)

    print_parser = subparsers.add_parser("print-document", help="Direct print")
    print_parser.add_argument("--file-name", required=True)
    print_parser.add_argument("--url", required=True)
    print_parser.add_argument("--media-format", required=True)
    print_parser.add_argument("--device-name", required=True)
    print_parser.add_argument("--control-sn", required=True)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    client = CloudPrintClient()

    if args.command == "check-install-progress":
        print_result(client.check_install_progress())
        return

    if args.command == "query-printers":
        print_result(client.query_printers())
        return

    if args.command == "upload-file":
        print_result(client.upload_file(args.file_path))
        return

    if args.command == "query-printer-detail":
        print_result(
            client.query_printer_detail(
                printer_name=args.printer_name,
                share_sn=args.share_sn,
                device_type=args.device_type,
            )
        )
        return

    if args.command == "create-roaming-task":
        print_result(
            client.create_roaming_task(
                file_name=args.file_name,
                url=args.url,
                media_format=args.media_format.upper(),
            )
        )
        return

    if args.command == "update-printer-side":
        print_result(client.update_printer_side(task_id=args.task_id, side=args.side))
        return

    if args.command == "update-printer-color":
        print_result(client.update_printer_color(task_id=args.task_id, color=args.color))
        return

    if args.command == "update-printer-copies":
        print_result(client.update_printer_copies(task_id=args.task_id, copies=args.copies))
        return

    if args.command == "print-document":
        print_result(
            client.direct_print_document(
                file_name=args.file_name,
                url=args.url,
                media_format=args.media_format.upper(),
                device_name=args.device_name,
                control_sn=args.control_sn,
            )
        )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
