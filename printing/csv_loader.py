import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BulkItem:
    data: str
    quantity: int = 1


def load_urls_from_csv(path: str | Path) -> List[BulkItem]:
    """
    Load QR data from a CSV file.

    Supported layouts:
      - Header with a column named url / URL / data / qr / link
      - No header → first column is used as data
      - Optional quantity column (defaults to 1)
    """
    path = Path(path)
    items: List[BulkItem] = []

    with path.open(newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(f, dialect=dialect)

        # Detect whether we actually have a header
        fieldnames = [fn.strip().lower() if fn else "" for fn in (reader.fieldnames or [])]
        url_keys = {"url", "data", "qr", "link", "qr_url", "qr-url"}
        qty_keys = {"quantity", "qty", "count", "copies"}

        url_col = next((fn for fn in fieldnames if fn in url_keys), None)
        qty_col = next((fn for fn in fieldnames if fn in qty_keys), None)

        # Fallback: treat first column as data when no known header
        if url_col is None and fieldnames:
            # Re-open as plain reader (no DictReader header assumption)
            f.seek(0)
            plain = csv.reader(f, dialect=dialect)
            first_row = next(plain, None)
            if first_row is None:
                return []

            # If first cell looks like a header, skip it
            if first_row[0].strip().lower() in url_keys:
                rows = plain
            else:
                rows = [first_row] + list(plain)

            for row in rows:
                if not row or not row[0].strip():
                    continue
                qty = 1
                if len(row) > 1 and row[1].strip().isdigit():
                    qty = max(1, int(row[1].strip()))
                items.append(BulkItem(data=row[0].strip(), quantity=qty))
            return items

        # DictReader path
        for row in reader:
            raw = (row.get(url_col) or "").strip() if url_col else ""
            if not raw:
                # try first value
                raw = next((v.strip() for v in row.values() if v and v.strip()), "")
            if not raw:
                continue

            qty = 1
            if qty_col:
                try:
                    qty = max(1, int(str(row.get(qty_col, "1")).strip()))
                except ValueError:
                    qty = 1
            items.append(BulkItem(data=raw, quantity=qty))

    return items