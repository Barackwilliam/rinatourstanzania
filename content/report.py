"""Print a gap report over packages.json so William knows what to ask the client for."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
pkgs = json.loads((HERE / "packages.json").read_text(encoding="utf-8"))
cats = json.loads((HERE / "categories.json").read_text(encoding="utf-8"))


def label(p):
    return f"[{p['source_file'][:2]}-{p['source_number']}] {p['title']}"


print("=" * 70)
print(f"RINA TOURS — {len(pkgs)} packages across {len(set(p['category'] for p in pkgs))} categories")
print("=" * 70)

by_cat = Counter(p["category"] for p in pkgs)
for c, n in by_cat.items():
    print(f"  {n:>3}  {c}")

# ---------------------------------------------------------------- gaps
print("\n" + "=" * 70)
print("MISSING CONTENT — what to send back to the client")
print("=" * 70)

checks = [
    ("No title", lambda p: not p["title"]),
    ("No price", lambda p: p["price_from"] is None),
    ("No duration", lambda p: p["duration_days"] is None),
    ("No short description", lambda p: not p["short_description"]),
    ("No full description", lambda p: not p["description"]),
    ("No Includes list", lambda p: not p["includes"]),
    ("No Excludes list", lambda p: not p["excludes"]),
    ("No Best For", lambda p: not p["best_for"]),
    ("Multi-day but no day-by-day itinerary",
     lambda p: (p["duration_days"] or 0) > 1 and not p["itinerary"]),
]

gap_by_pkg = defaultdict(list)
for name, test in checks:
    hits = [p for p in pkgs if test(p)]
    if not hits:
        continue
    print(f"\n{name}  ({len(hits)})")
    for p in hits:
        print(f"    {label(p)}")
        gap_by_pkg[label(p)].append(name)

# ---------------------------------------------------- worst offenders
print("\n" + "=" * 70)
print("PACKAGES WITH THE MOST GAPS (fix these first — highest priced)")
print("=" * 70)
ranked = sorted(
    ((lbl, gaps) for lbl, gaps in gap_by_pkg.items()),
    key=lambda x: -len(x[1]),
)
price_by_label = {label(p): (p["price_from"] or 0) for p in pkgs}
ranked = sorted(ranked, key=lambda x: (-len(x[1]), -price_by_label.get(x[0], 0)))
for lbl, gaps in ranked[:15]:
    price = price_by_label.get(lbl, 0)
    print(f"  ${price:>7,.0f}  {len(gaps)} gaps  {lbl}")
    print(f"            missing: {', '.join(gaps)}")

# ------------------------------------------------------ duplicate slugs
print("\n" + "=" * 70)
print("DUPLICATE SLUGS (URL collisions — must be resolved)")
print("=" * 70)
slugs = Counter(p["slug"] for p in pkgs)
dupes = {s: n for s, n in slugs.items() if n > 1}
if dupes:
    for s, n in dupes.items():
        print(f"\n  {s}  ({n}x)")
        for p in pkgs:
            if p["slug"] == s:
                print(f"      {label(p)}")
else:
    print("  none")

# -------------------------------------------- near-duplicate packages
print("\n" + "=" * 70)
print("SAME EXPERIENCE APPEARING IN SEVERAL CATEGORIES")
print("=" * 70)


def key(p):
    t = p["title"].lower()
    t = re.sub(r"\b(tour|safari|experience|adventure|day trip|escape|package|"
               r"tanzania|zanzibar|nature|cultural|camping|trekking|marine|"
               r"hike|trip|holiday|and|the|of|a|an|&)\b", " ", t)
    return tuple(sorted(set(w for w in re.findall(r"[a-z]+", t) if len(w) > 3)))


groups = defaultdict(list)
for p in pkgs:
    k = key(p)
    if k:
        groups[k].append(p)

overlaps = {k: v for k, v in groups.items() if len({x["category"] for x in v}) > 1}
for k, v in sorted(overlaps.items(), key=lambda x: -len(x[1]))[:20]:
    print(f"\n  {' + '.join(k)}")
    for p in v:
        print(f"      ${p['price_from'] or 0:>6,.0f}  {p['category']:<32} {p['title']}")

# ------------------------------------------------- destination cleanup
print("\n" + "=" * 70)
print("DESTINATION NAMES — need normalising before they become filters")
print("=" * 70)
dest = Counter()
for p in pkgs:
    for d in p["destinations"]:
        for piece in re.split(r"\s*/\s*", d):
            dest[piece.strip()] += 1

print(f"\n  {len(dest)} distinct strings across {sum(dest.values())} references\n")
for d, n in sorted(dest.items()):
    print(f"    {n:>3}  {d}")

# ------------------------------------------------------- price basis
print("\n" + "=" * 70)
print("PRICE BASIS (affects how the site displays 'from' prices)")
print("=" * 70)
for b, n in Counter(p["price_basis"] for p in pkgs).most_common():
    print(f"  {n:>3}  {b}")
    if b != "per person":
        for p in pkgs:
            if p["price_basis"] == b:
                print(f"          {label(p)}  —  {p['price_raw']}")

# ---------------------------------------------------- category blocks
print("\n" + "=" * 70)
print("CATEGORY BLOCKS")
print("=" * 70)
have = {c.get("name") for c in cats}
print(f"  {len(cats)} supplied: {', '.join(sorted(x for x in have if x))}")
missing_cat = set(by_cat) - {c.get("name") for c in cats}
if missing_cat:
    print(f"  MISSING category block: {', '.join(missing_cat)}")

# featured names that don't match any real package title
titles = {p["title"].lower() for p in pkgs}
print("\n  Featured/recommended names that match no package title:")
found_any = False
for c in cats:
    bad = []
    for f in c.get("featured", []):
        if f.lower() not in titles:
            bad.append(f)
    for k, v in c.get("recommendations", {}).items():
        if v and v.lower() not in titles:
            bad.append(f"{k} -> {v}")
    if bad:
        found_any = True
        print(f"\n    {c.get('name')}")
        for b in bad:
            print(f"        {b}")
if not found_any:
    print("    none")

print()
