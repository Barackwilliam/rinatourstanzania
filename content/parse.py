"""
Parse Rina Tours' package text files into structured JSON.

Handles both layouts the client used:
  - title on the line after "PACKAGE 01", fields as "Label:" then value on next line
  - title inline as "PACKAGE 01: TITLE", fields as "Label: value"

Usage:
    python3 parse.py            # every *.txt in this folder
    python3 parse.py 01-*.txt   # or just the ones you name

Writes packages.json + categories.json.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SPLIT = re.compile(r"^={10,}\s*$", re.M)

LIST_FIELDS = {"highlights", "includes", "excludes"}

FIELD_ALIASES = {
    "category": "category",
    "duration": "duration",
    "starting point": "starting_point",
    "destination": "destinations",
    "destinations": "destinations",
    "route": "route",
    "price": "price",
    "short description": "short_description",
    "full description": "full_description",
    "typical itinerary": "typical_itinerary",
    "highlights": "highlights",
    "includes": "includes",
    "excludes": "excludes",
    "best for": "best_for",
    "important": "important",
}

LABEL = re.compile(
    r"^(" + "|".join(re.escape(k) for k in FIELD_ALIASES) + r"):[ \t]*(.*)$",
    re.I | re.M,
)

CATEGORY_FIELDS = {
    "category name": "name",
    "category slug": "slug",
    "category code": "code",
    "category description": "description",
    "featured packages": "featured",
    "category featured packages": "featured",
    "main destinations": "main_destinations",
}
CAT_LABEL = re.compile(
    r"^(" + "|".join(re.escape(k) for k in CATEGORY_FIELDS)
    + r"|recommended [a-z/& ]+):[ \t]*(.*)$",
    re.I | re.M,
)


def slugify(text):
    s = text.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def parse_duration(text):
    days = nights = None
    m = re.search(r"(\d+)\s*Days?\b", text, re.I)
    if m:
        days = int(m.group(1))
    m = re.search(r"(\d+)\s*Nights?\b", text, re.I)
    if m:
        nights = int(m.group(1))
    return days, nights


def parse_price(text):
    amount = currency = basis = None
    m = re.search(r"(USD|TZS|EUR|\$)\s*([\d,]+(?:\.\d+)?)", text, re.I)
    if m:
        currency = "USD" if m.group(1) == "$" else m.group(1).upper()
        amount = float(m.group(2).replace(",", ""))
    m = re.search(r"\bper\s+([a-z ]+)", text, re.I)
    if m:
        basis = "per " + m.group(1).strip().lower()
    return amount, currency, basis


def parse_days(text):
    if not text:
        return [], ""
    parts = re.split(r"^Day\s+(\d+)\s*:\s*$", text, flags=re.M)
    if len(parts) < 3:
        parts = re.split(r"^Day\s+(\d+)\s*:[ \t]*", text, flags=re.M)
        if len(parts) < 3:
            return [], text.strip()

    intro = parts[0].strip()
    days = []
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1].strip()
        if not body:
            continue
        title = re.split(r"(?<=[.!?])\s", body)[0].strip().rstrip(".")
        days.append({
            "day_number": int(parts[i]),
            "title": title[:200],
            "description": body,
        })
    return days, intro


def parse_fields(body):
    fields = {}
    matches = list(LABEL.finditer(body))
    for i, m in enumerate(matches):
        key = FIELD_ALIASES[m.group(1).lower()]
        inline = m.group(2).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[m.end():end].strip()
        value = inline if inline else block

        if key in LIST_FIELDS:
            src = block or inline
            fields[key] = [
                ln.lstrip("-\u2022").strip()
                for ln in src.splitlines()
                if ln.strip().startswith("-")
            ]
        elif key == "destinations":
            fields.setdefault("destinations", [])
            fields["destinations"] += [
                ln.strip() for ln in value.splitlines() if ln.strip()
            ]
        else:
            fields[key] = value
    return fields


def parse_category_block(body, source):
    cat = {"source_file": source, "recommendations": {}}
    matches = list(CAT_LABEL.finditer(body))
    for i, m in enumerate(matches):
        raw = m.group(1).lower().strip()
        inline = m.group(2).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[m.end():end].strip()
        value = inline if inline else block

        if raw.startswith("recommended"):
            cat["recommendations"][raw] = value.splitlines()[0].strip() if value else ""
        elif raw in CATEGORY_FIELDS:
            key = CATEGORY_FIELDS[raw]
            if key in ("featured", "main_destinations"):
                cat[key] = [
                    ln.lstrip("-").strip()
                    for ln in block.splitlines()
                    if ln.strip().startswith("-")
                ]
            else:
                cat[key] = value
    return cat


def parse_file(path):
    raw = path.read_text(encoding="utf-8")
    chunks = SPLIT.split(raw)

    packages, categories = [], []
    pending = None
    pending_kind = None

    for chunk in chunks:
        stripped = chunk.strip()
        if not stripped:
            continue
        head = stripped.splitlines()[0].strip()

        if head.upper().startswith("PACKAGE"):
            if ":" in head:
                number = re.sub(r"\D", "", head.split(":")[0])
                title = head.split(":", 1)[1].strip()
            else:
                number = re.sub(r"\D", "", head)
                lines = stripped.splitlines()
                title = lines[1].strip() if len(lines) > 1 else ""
            pending = {"number": number, "title": title, "source": path.name}
            pending_kind = "package"
            continue

        if head.upper().startswith("DATABASE CATEGORY"):
            pending_kind = "category"
            pending = None
            continue

        if pending_kind == "category":
            categories.append(parse_category_block(chunk, path.name))
            pending_kind = None
            continue

        if pending_kind != "package" or pending is None:
            continue

        f = parse_fields(chunk)
        days, nights = parse_duration(f.get("duration", ""))
        amount, currency, basis = parse_price(f.get("price", ""))

        itinerary, _ = parse_days(f.get("typical_itinerary", ""))
        if itinerary:
            description = f.get("full_description", "").strip()
        else:
            itinerary, description = parse_days(f.get("full_description", ""))

        packages.append({
            "source_file": pending["source"],
            "source_number": pending["number"],
            "title": pending["title"],
            "slug": slugify(pending["title"]),
            "category": f.get("category", ""),
            "duration_raw": f.get("duration", ""),
            "duration_days": days,
            "duration_nights": nights,
            "starting_point": f.get("starting_point", ""),
            "destinations": f.get("destinations", []),
            "route": f.get("route", ""),
            "price_raw": f.get("price", ""),
            "price_from": amount,
            "currency": currency,
            "price_basis": basis,
            "short_description": f.get("short_description", ""),
            "description": description,
            "itinerary": itinerary,
            "highlights": f.get("highlights", []),
            "includes": f.get("includes", []),
            "excludes": f.get("excludes", []),
            "best_for": f.get("best_for", ""),
            "important": f.get("important", ""),
        })
        pending = None
        pending_kind = None

    return packages, categories


def main():
    args = sys.argv[1:]
    files = [Path(a) for a in args] if args else sorted(HERE.glob("*.txt"))

    all_packages, all_categories = [], []
    for f in files:
        pk, ct = parse_file(f)
        print(f"{f.name}: {len(pk)} packages, {len(ct)} category block(s)")
        all_packages += pk
        all_categories += ct

    (HERE / "packages.json").write_text(
        json.dumps(all_packages, indent=2, ensure_ascii=False), encoding="utf-8")
    (HERE / "categories.json").write_text(
        json.dumps(all_categories, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nTOTAL: {len(all_packages)} packages")
    return all_packages, all_categories


if __name__ == "__main__":
    main()
