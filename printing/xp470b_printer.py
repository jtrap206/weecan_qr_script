"""
XPrinter XP-470B – TSPL over USB.

- On Windows with a real printer: builds TSPL and sends raw bytes.
- On Mac / without the device: dry-run mode prints the TSPL to the console.

Wire it in main.py:

    from printing.xp470b_printer import XP470BPrinter
    printer = XP470BPrinter(dry_run=True)   # Mac / testing
    # printer = XP470BPrinter(dry_run=False)  # Windows + real device
"""

from __future__ import annotations

import sys
from typing import Optional

from printing.printer import Printer


# ── DPI of XP-470B (203 dpi) ───────────────────────────────────────────────
DPI = 203
DOTS_PER_MM = DPI / 25.4  # ≈ 8 dots per mm


class XP470BPrinter(Printer):
    def __init__(
        self,
        dry_run: bool = False,
        # Optional: force a specific Windows printer name or USB path later
        printer_name: Optional[str] = None,
    ):
        self.dry_run = dry_run
        self.printer_name = printer_name  # e.g. "Xprinter XP-470B"

    # ── Public API (same signature as MockPrinter) ─────────────────────────
    def print_qr(
        self,
        data: str,
        width_mm: float,
        height_mm: float,
        qr_size_mm: float,
        quantity: int,
    ) -> None:
        tspl = self._build_tspl(
            data=data,
            width_mm=width_mm,
            height_mm=height_mm,
            qr_size_mm=qr_size_mm,
            quantity=quantity,
        )

        if self.dry_run or sys.platform != "win32":
            self._dry_run(tspl)
            return

        self._send_usb(tspl)

    # ── TSPL builder ───────────────────────────────────────────────────────
    def _build_tspl(
        self,
        data: str,
        width_mm: float,
        height_mm: float,
        qr_size_mm: float,
        quantity: int,
    ) -> str:
        """
        Build a minimal TSPL job for a centered QR code on a label.

        QRCODE syntax (TSPL):
            QRCODE x,y,ECC,cell_width,mode,rotation,"content"
            ECC      = L | M | Q | H
            cell_width = 1–10 (module size in dots)
            mode     = A (auto) | M (manual)
            rotation = 0 | 90 | 180 | 270
        """
        # Convert mm → dots
        label_w = int(round(width_mm * DOTS_PER_MM))
        label_h = int(round(height_mm * DOTS_PER_MM))

        # Approximate QR module size so the whole code ≈ qr_size_mm
        # (version is auto; we pick a reasonable cell size)
        cell = max(1, min(10, int(round(qr_size_mm * DOTS_PER_MM / 25))))
        # Rough QR side in dots (version ~4–5 with border ≈ 25–33 modules)
        qr_side_dots = cell * 29  # safe middle estimate

        # Center the QR on the label
        x = max(0, (label_w - qr_side_dots) // 2)
        y = max(0, (label_h - qr_side_dots) // 2)

        # Escape any double quotes inside the data
        safe_data = data.replace('"', "'")

        lines = [
            f"SIZE {width_mm} mm,{height_mm} mm",
            "GAP 2 mm,0",          # adjust if your stock uses different gap
            "DIRECTION 1",
            "CLS",
            f'QRCODE {x},{y},L,{cell},A,0,"{safe_data}"',
            f"PRINT {max(1, quantity)},1",
        ]
        return "\r\n".join(lines) + "\r\n"

    # ── Dry-run (Mac / testing) ────────────────────────────────────────────
    def _dry_run(self, tspl: str) -> None:
        print()
        print("========== XP-470B DRY RUN (TSPL) ==========")
        print(tspl)
        print("============================================")
        print()

    # ── USB / RAW send (Windows) ───────────────────────────────────────────
    def _send_usb(self, tspl: str) -> None:
        """
        Send raw TSPL bytes to the printer on Windows.

        Two common approaches (pick one and flesh it out):

        A) win32print – use the installed driver in RAW mode
        B) pyusb      – talk to the USB device directly

        Below is a win32print sketch. Install:  pip install pywin32
        """
        try:
            import win32print
        except ImportError as e:
            raise RuntimeError(
                "pywin32 is required for Windows printing. "
                "Run: pip install pywin32"
            ) from e

        printer_name = self.printer_name or self._find_xprinter(win32print)
        if not printer_name:
            raise RuntimeError(
                "No XPrinter found. Install the XP-470B driver or pass "
                "printer_name='Your Printer Name' to XP470BPrinter()."
            )

        raw_data = tspl.encode("utf-8")  # TSPL is ASCII; utf-8 is fine

        hprinter = win32print.OpenPrinter(printer_name)
        try:
            # RAW job – driver passes bytes straight through
            job = win32print.StartDocPrinter(
                hprinter, 1, ("QR Label", None, "RAW")
            )
            try:
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, raw_data)
                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)

    @staticmethod
    def _find_xprinter(win32print) -> Optional[str]:
        """Best-effort: find a printer whose name contains 'xprinter' / 'xp-470'."""
        for flags in (
            win32print.PRINTER_ENUM_LOCAL,
            win32print.PRINTER_ENUM_CONNECTIONS,
        ):
            try:
                printers = win32print.EnumPrinters(flags)
            except Exception:
                continue
            for p in printers:
                name = p[2] if len(p) > 2 else ""
                lower = name.lower()
                if "xprinter" in lower or "xp-470" in lower or "xp470" in lower:
                    return name
        return None