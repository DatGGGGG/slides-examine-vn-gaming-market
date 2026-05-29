import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


BASE = "https://api.worldbank.org/v2"
INDICATOR = "NY.GDP.PCAP.CD"
START_YEAR = 2015
END_YEAR = 2024
PER_PAGE = 20000


def fetch_json(url: str):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Codex-WorldBank-Downloader/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def build_url(path: str, **params) -> str:
    query = urllib.parse.urlencode(params)
    return f"{BASE}{path}?{query}"


def get_countries():
    countries = []
    page = 1
    while True:
        url = build_url("/country", format="json", per_page=400, page=page)
        payload = fetch_json(url)
        meta, rows = payload
        for row in rows:
            region = (row.get("region") or {}).get("value")
            if region == "Aggregates":
                continue
            countries.append(
                {
                    "id": row["id"],
                    "iso3": row.get("iso2Code") or "",
                    "iso3c": row.get("id") or "",
                    "name": row.get("name") or "",
                    "region": region or "",
                    "income_level": ((row.get("incomeLevel") or {}).get("value")) or "",
                    "lending_type": ((row.get("lendingType") or {}).get("value")) or "",
                    "capital_city": row.get("capitalCity") or "",
                }
            )
        if page >= int(meta["pages"]):
            break
        page += 1
    countries.sort(key=lambda x: x["name"])
    return countries


def get_indicator_rows():
    url = build_url(
        f"/country/all/indicator/{INDICATOR}",
        format="json",
        per_page=PER_PAGE,
        date=f"{START_YEAR}:{END_YEAR}",
        page=1,
    )
    payload = fetch_json(url)
    meta, rows = payload
    if int(meta["pages"]) > 1:
        all_rows = list(rows)
        for page in range(2, int(meta["pages"]) + 1):
            page_url = build_url(
                f"/country/all/indicator/{INDICATOR}",
                format="json",
                per_page=PER_PAGE,
                date=f"{START_YEAR}:{END_YEAR}",
                page=page,
            )
            _, page_rows = fetch_json(page_url)
            all_rows.extend(page_rows)
        return all_rows
    return rows


def main():
    root = Path(__file__).resolve().parent
    countries = get_countries()
    country_lookup = {c["iso3c"]: c for c in countries}

    raw_rows = get_indicator_rows()
    values = defaultdict(dict)

    for row in raw_rows:
        iso3c = row.get("countryiso3code") or ""
        if iso3c not in country_lookup:
            continue
        year = int(row["date"])
        if year < START_YEAR or year > END_YEAR:
            continue
        values[iso3c][year] = row.get("value")

    years = list(range(START_YEAR, END_YEAR + 1))
    long_path = root / "worldbank_gdp_per_capita_2015_2024_long.csv"
    wide_path = root / "worldbank_gdp_per_capita_2015_2024_wide.csv"

    with long_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "country_name",
                "country_code",
                "region",
                "income_level",
                "lending_type",
                "indicator_code",
                "indicator_name",
                "year",
                "gdp_per_capita_current_usd",
            ]
        )
        for country in countries:
            iso3c = country["iso3c"]
            for year in years:
                writer.writerow(
                    [
                        country["name"],
                        iso3c,
                        country["region"],
                        country["income_level"],
                        country["lending_type"],
                        INDICATOR,
                        "GDP per capita (current US$)",
                        year,
                        values.get(iso3c, {}).get(year, ""),
                    ]
                )

    with wide_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "country_name",
                "country_code",
                "region",
                "income_level",
                "lending_type",
                *years,
            ]
        )
        for country in countries:
            iso3c = country["iso3c"]
            writer.writerow(
                [
                    country["name"],
                    iso3c,
                    country["region"],
                    country["income_level"],
                    country["lending_type"],
                    *[values.get(iso3c, {}).get(year, "") for year in years],
                ]
            )

    country_count = len(countries)
    populated_cells = sum(
        1 for country in countries for year in years if values.get(country["iso3c"], {}).get(year) is not None
    )

    print(f"Countries written: {country_count}")
    print(f"Year columns: {START_YEAR}-{END_YEAR}")
    print(f"Non-empty country-year values: {populated_cells}")
    print(f"Long CSV: {long_path}")
    print(f"Wide CSV: {wide_path}")


if __name__ == "__main__":
    main()
