from __future__ import annotations

import sys

import build_deck_workbench as workbench


def main() -> int:
    template_path = workbench.ROOT / "workbench_template.html"
    if not template_path.exists():
        raise SystemExit("Missing external workbench template file")

    rows = workbench.to_dicts()
    if len(rows) != 30:
        raise SystemExit(f"Expected 30 slides, got {len(rows)}")

    expected_numbers = [str(i) for i in range(1, 31)]
    actual_numbers = [row["slide_number"] for row in rows]
    if actual_numbers != expected_numbers:
        raise SystemExit(f"Unexpected slide number sequence: {actual_numbers}")

    special = workbench.build_special_data()
    required_keys = {"8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "22", "23", "24", "25", "26", "27", "29", "30", "41", "42", "43", "44", "45", "46", "47"}
    missing = required_keys.difference(special)
    if missing:
        raise SystemExit(f"Missing special-data keys: {sorted(missing)}")

    if not special["22"]["series"]:
        raise SystemExit("YouTube share series is empty")
    if not special["30"]["yearly_counts"]:
        raise SystemExit("Vietnam movie revenue series is empty")

    html = workbench.build_html(workbench.csv_text(rows))
    for marker in ("__FIELDS__", "__SEED__", "__SPECIAL_DATA__"):
        if marker in html:
            raise SystemExit(f"Template placeholder still present: {marker}")
    if "VN Gaming Deck Workbench" not in html:
        raise SystemExit("Expected HTML title not found")

    print("Workbench smoke check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
