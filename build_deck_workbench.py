from __future__ import annotations

import csv
import json
import math
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESEARCH_DIR = ROOT / "research"
CSV_NAME = "vn_gaming_deck_working.csv"
HTML_NAME = "vn_gaming_deck_workbench.html"
PYRAMID_JSON_NAME = "demographics_analysis/vietnam_population_pyramid_1950_2025.json"
MOVIE_REVENUE_CSV_NAME = "moveek_vietnam_monthly_movies_with_boxofficevietnam_recovered_v5_and_vietnamese_flag_gpt54nano_20260528T044609Z.csv"
YOUTUBE_SHARE_WITH_PCT_CSV_NAME = "most_popular_vn_daily_video_language_counts_with_pct.csv"
YOUTUBE_SHARE_RAW_CSV_NAME = "most_popular_vn_daily_video_language_counts.csv"
YOUTUBE_TRENDING_VIDEOS_CSV_NAME = "most_popular_vn_with_is_vietnamese_video.csv"
VN_MOBILE_GAMES_DOWNLOADS_CSV_NAME = "[Research] Examining VN Gaming Market Opportunity 2026 - Data Sheet - VN Mobile Games (top by downloads).csv"
YOUTUBE_TRENDING_SNAPSHOT_DATE = "2025-06-30"
DONOR_SUPPLY_SPECIAL_DATA_JSON_NAME = "donor_supply_specialdata_21_27.json"
EXEC_SUMMARY_ANALYSIS_CSV_NAME = "[Research] Examining VN Gaming Market Opportunity 2026 - Data Sheet - [Analysis] Executive Summary.csv"

FIELDS = [
    "slide_number",
    "template_id",
    "slide_type",
    "part_number",
    "part_name",
    "section",
    "subsection",
    "category",
    "title",
    "purpose",
    "evidence",
    "visual",
    "takeaway",
    "status",
    "owner",
    "notes",
]



def build_seed_rows():
    path = ROOT / CSV_NAME
    if not path.exists():
        raise FileNotFoundError(f"Missing seed CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return [[row.get(field, "") for field in FIELDS] for row in reader]


def to_dicts():
    rows = []
    for i, row in enumerate(build_seed_rows(), 1):
        item = dict(zip(FIELDS, row))
        item["slide_number"] = str(i)
        template_id = str(item.get("template_id", "")).strip()
        item["template_id"] = template_id if template_id.isdigit() else str(i)
        rows.append(item)
    return rows


def csv_text(rows):
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def read_csv_dicts(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def read_data_csv(path_name: str):
    return read_csv_dicts(DATA_DIR / path_name)


def read_research_csv_rows(path_name: str):
    path = RESEARCH_DIR / path_name
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.reader(fh))


def parse_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def parse_int(value, default: int = 0) -> int:
    if value is None:
        return default
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def is_true_flag(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def load_population_pyramid():
    raw = json.loads((ROOT / PYRAMID_JSON_NAME).read_text(encoding="utf-8"))
    years = []
    max_value = 0
    for item in raw:
        groups = []
        for group in item["ageGroups"]:
            groups.append(
                {
                    "label": group["ageRange"],
                    "male": group["male"],
                    "female": group["female"],
                    "total": group["total"],
                }
            )
            max_value = max(max_value, group["male"], group["female"])
        years.append(
            {
                "year": item["year"],
                "population": item["totalPopulation"],
                "medianAge": item["medianAge"],
                "malePopulation": item["malePopulation"],
                "femalePopulation": item["femalePopulation"],
                "groups": groups,
            }
        )
    return {
        "maxValue": max_value,
        "quickYears": [1950, 1980, 1990, 2000, 2010, 2020, 2025],
        "startYear": 2025,
        "years": years,
    }


def load_daily_vietnamese_video_share():
    pct_path = DATA_DIR / YOUTUBE_SHARE_WITH_PCT_CSV_NAME
    raw_path = DATA_DIR / YOUTUBE_SHARE_RAW_CSV_NAME
    rows = []
    if pct_path.exists():
        for row in read_csv_dicts(pct_path):
            rows.append(
                {
                    "date": row["date"],
                    "pct": round(parse_float(row["pct_vietnamese_videos"]), 2),
                }
            )
    else:
        for row in read_csv_dicts(raw_path):
            total = parse_float(row["unique_trending_videos_total"])
            vn = parse_float(row["unique_trending_videos_vietnamese"])
            pct = (vn / total * 100.0) if total else 0.0
            rows.append({"date": row["date"], "pct": round(pct, 2)})
    marker_dates = [
        ("2022-07-01", "Jul 2022"),
        ("2023-01-01", "2023"),
        ("2024-01-01", "2024"),
        ("2025-01-01", "2025"),
        ("2025-06-30", "Jun 2025"),
    ]
    markers = []
    index_lookup = {row["date"]: i for i, row in enumerate(rows)}
    for key, label in marker_dates:
        if key in index_lookup:
            markers.append({"index": index_lookup[key], "label": label})
    avg_pct = round(sum(r["pct"] for r in rows) / len(rows), 2) if rows else 0
    return {
        "series": rows,
        "avgPct": avg_pct,
        "latestPct": rows[-1]["pct"] if rows else 0,
        "minPct": min(r["pct"] for r in rows) if rows else 0,
        "maxPct": max(r["pct"] for r in rows) if rows else 0,
        "markers": markers,
    }


def load_trending_videos_for_day(target_date: str, limit: int | None = None):
    by_video = {}
    for row in read_data_csv(YOUTUBE_TRENDING_VIDEOS_CSV_NAME):
        collection_date = str(row.get("collection_date", ""))
        if not collection_date.startswith(target_date):
            continue
        video_id = row.get("video_id", "").strip()
        if not video_id:
            continue
        rank = parse_int(row.get("rank"), 9999)
        view_count = parse_int(row.get("view_count"))
        current = by_video.get(video_id)
        candidate = {
            "rank": rank,
            "title": row.get("title", "").strip(),
            "channel": row.get("channel_title", "").strip(),
            "isVietnamese": is_true_flag(row.get("is_vietnamese_video")),
            "viewCount": view_count,
        }
        if current is None or rank < current["rank"] or (rank == current["rank"] and view_count > current["viewCount"]):
            by_video[video_id] = candidate
    items = sorted(by_video.values(), key=lambda x: (x["rank"], -x["viewCount"], x["title"]))
    return (items[:limit] if limit else items), len(items)


def load_wide_csv_table(path_name: str):
    rows = []
    for row in read_data_csv(path_name):
        rows.append(
            {
                "bucket": row["Price bucket"],
                "y2023": row["2023"],
                "y2024": row["2024"],
                "y2025": row["2025"],
                "total": row["Total"],
            }
        )
    return rows


def load_donor_supply_special_data():
    path = DATA_DIR / DONOR_SUPPLY_SPECIAL_DATA_JSON_NAME
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    key_map = {
        "29": "41",
        "26": "42",
        "27": "43",
        "28": "44",
        "30": "45",
        "31": "46",
        "32": "47",
    }
    return {new_key: raw[old_key] for old_key, new_key in key_map.items() if old_key in raw}


def load_vn_mobile_game_downloads_summary():
    rows = read_data_csv(VN_MOBILE_GAMES_DOWNLOADS_CSV_NAME)
    yearly = {}
    total_vietnam = 0
    total_foreign = 0
    vietnam_titles = []

    for row in rows:
        year = parse_int(row.get("year"))
        downloads = parse_int(row.get("downloads"))
        if not year or not downloads:
            continue
        bucket = yearly.setdefault(
            year,
            {
                "year": year,
                "vietnam": 0,
                "foreign": 0,
                "total": 0,
                "vn_titles": [],
                "games": [],
            },
        )
        game_item = {
            "name": str(row.get("game_name", "")).strip(),
            "rank": parse_int(row.get("rank_in_year")),
            "downloads": downloads,
            "is_vietnamese": is_true_flag(row.get("is_vietnamese_game")),
        }
        bucket["games"].append(game_item)
        if is_true_flag(row.get("is_vietnamese_game")):
            bucket["vietnam"] += downloads
            bucket["vn_titles"].append(
                {
                    "name": game_item["name"],
                    "rank": game_item["rank"],
                    "downloads": downloads,
                }
            )
            vietnam_titles.append(
                {
                    "year": year,
                    "name": game_item["name"],
                    "rank": game_item["rank"],
                    "downloads": downloads,
                }
            )
            total_vietnam += downloads
        else:
            bucket["foreign"] += downloads
            total_foreign += downloads
        bucket["total"] += downloads

    yearly_counts = []
    for year in sorted(yearly):
        item = yearly[year]
        item["vn_titles"].sort(key=lambda x: (x["rank"], -x["downloads"], x["name"]))
        item["games"].sort(key=lambda x: (x["rank"], -x["downloads"], x["name"]))
        yearly_counts.append(
            {
                "year": item["year"],
                "vietnam": item["vietnam"],
                "foreign": item["foreign"],
                "total": item["total"],
                "vn_title_label": " / ".join(x["name"] for x in item["vn_titles"]),
                "vn_rank_label": ", ".join(f"#{x['rank']}" for x in item["vn_titles"]),
                "games": item["games"],
            }
        )

    max_total = max((item["total"] for item in yearly_counts), default=0)
    tick_step = max(1000000, math.ceil(max_total / 4 / 1000000) * 1000000) if max_total else 1000000
    max_y = tick_step * 4
    highlights = [
        {
            "year": item["year"],
            "title": item["name"],
            "rank": item["rank"],
            "downloads": item["downloads"],
        }
        for item in sorted(vietnam_titles, key=lambda x: (x["year"], x["rank"], -x["downloads"], x["name"]))
    ]

    return {
        "yearly_counts": yearly_counts,
        "totalVietnam": total_vietnam,
        "totalForeign": total_foreign,
        "vietnamYears": sum(1 for item in yearly_counts if item["vietnam"] > 0),
        "peakTotal": max_total,
        "peakVietnam": max((item["vietnam"] for item in yearly_counts), default=0),
        "peakForeign": max((item["foreign"] for item in yearly_counts), default=0),
        "maxY": max_y,
        "ticks": [tick_step * i for i in range(5)],
        "highlights": highlights,
        "source": VN_MOBILE_GAMES_DOWNLOADS_CSV_NAME,
    }


def load_vietnam_movie_revenue_summary():
    yearly = {year: {"vietnamese": 0.0, "foreign": 0.0} for year in range(2021, 2026)}
    top_by_year = {year: {"vietnamese": [], "foreign": []} for year in range(2021, 2026)}
    seen = set()
    for row in read_data_csv(MOVIE_REVENUE_CSV_NAME):
        year = parse_int(row.get("listing_year"), default=-1)
        if year < 2021 or year > 2025:
            continue
        slug = str(row.get("movie_slug", "")).strip()
        if not slug:
            continue
        key = (year, slug)
        if key in seen:
            continue
        revenue = parse_float(row.get("estimated_total_revenue_vnd") or row.get("boxofficevietnam_total_revenue_vnd"))
        if not revenue:
            continue
        is_vietnamese = is_true_flag(row.get("is_vietnamese_movie"))
        bucket = yearly.setdefault(year, {"vietnamese": 0.0, "foreign": 0.0})
        title = (
            str(row.get("movie_title", "")).strip()
            or str(row.get("boxofficevietnam_name", "")).strip()
            or str(row.get("boxofficevietnam_candidate_vi_title", "")).strip()
            or str(row.get("boxofficevietnam_candidate_en_title", "")).strip()
            or slug
        )
        candidate = {
            "year": year,
            "slug": slug,
            "title": title,
            "revenue_vnd": revenue,
        }
        if is_vietnamese:
            bucket["vietnamese"] += revenue
            top_by_year[year]["vietnamese"].append(candidate)
        else:
            bucket["foreign"] += revenue
            top_by_year[year]["foreign"].append(candidate)
        seen.add(key)

    yearly_counts = []
    total_vietnamese = 0.0
    total_foreign = 0.0
    for year in range(2021, 2026):
        vn = yearly.get(year, {}).get("vietnamese", 0.0)
        foreign = yearly.get(year, {}).get("foreign", 0.0)
        total = vn + foreign
        share = (vn / total * 100) if total else 0.0
        yearly_counts.append({
            "year": year,
            "vietnamese": vn,
            "foreign": foreign,
            "total": total,
            "share": share,
        })
        total_vietnamese += vn
        total_foreign += foreign

    latest = yearly_counts[-1]
    peak = max(yearly_counts, key=lambda item: item["total"])
    top_rows = []
    for year in range(2021, 2026):
        vn_top = max(top_by_year.get(year, {}).get("vietnamese", []), key=lambda item: item["revenue_vnd"], default=None)
        foreign_top = max(top_by_year.get(year, {}).get("foreign", []), key=lambda item: item["revenue_vnd"], default=None)
        top_rows.append({
            "year": year,
            "vietnamese_title": vn_top["title"] if vn_top else "",
            "vietnamese_revenue_vnd": vn_top["revenue_vnd"] if vn_top else 0.0,
            "foreign_title": foreign_top["title"] if foreign_top else "",
            "foreign_revenue_vnd": foreign_top["revenue_vnd"] if foreign_top else 0.0,
        })
    return {
        "yearly_counts": yearly_counts,
        "top_rows": top_rows,
        "totalVietnamese": total_vietnamese,
        "totalForeign": total_foreign,
        "latestVietnamese": latest["vietnamese"],
        "latestForeign": latest["foreign"],
        "latestShare": latest["share"],
        "peakYear": peak["year"],
        "source": f"{MOVIE_REVENUE_CSV_NAME}; revenue estimated from Box Office Vietnam and web research.",
    }


def merge_special_data(*sections):
    merged = {}
    for section in sections:
        merged.update(section)
    return merged

def build_market_special_data(population_pyramid):
    return {
        "8": {
            "years": ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
            "values": [2577.57, 2735.06, 2956.11, 3222.31, 3440.9, 3534.04, 3704.19, 4147.7, 4323.35, 4717.29],
            "benchmarks": [
                {"name": "Viet Nam", "cagr": 6.95, "highlight": True},
                {"name": "Indonesia", "cagr": 4.59, "highlight": False},
                {"name": "Philippines", "cagr": 3.55, "highlight": False},
                {"name": "Thailand", "cagr": 2.88, "highlight": False},
                {"name": "Malaysia", "cagr": 2.33, "highlight": False},
            ],
            "current": 4717.29,
            "cagr": 6.95,
            "totalGrowth": 83.0,
            "maxY": 5000,
        },
        "9": {
            "years": ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
            "info": [29392, 31840, 34293, 37793, 40881, 42493, 295916, 334272, 354381, 387489],
            "arts": [24969, 27128, 29990, 32418, 35291, 35573, 49404, 56059, 64316, 71488],
            "infoCagr": 33.18,
            "artsCagr": 12.40,
            "maxY": 400000,
        },
        "10": {
            "buckets": [
                {"key": "18", "label": "0-17", "color": "#2563eb"},
                {"key": "25", "label": "18-24", "color": "#ef4444"},
                {"key": "35", "label": "25-34", "color": "#f59e0b"},
                {"key": "45", "label": "35-44", "color": "#64748b"},
                {"key": "55", "label": "45-54", "color": "#111827"},
            ],
            "portfolio": {"under35": 70.8, "age25": 40.8, "male": 72.0, "avgAge": 29.6},
            "games": [
                {"name": "Garena Free Fire", "revenueM": 128.54, "age18": 33.7, "age25": 36.1, "age35": 20.7, "age45": 7.4, "age55": 2.2},
                {"name": "Arena of Valor", "revenueM": 73.41, "age18": 32.8, "age25": 44.5, "age35": 14.3, "age45": 6.4, "age55": 1.9},
                {"name": "Roblox", "revenueM": 56.62, "age18": 19.6, "age25": 42.6, "age35": 26.5, "age45": 9.3, "age55": 2.1},
                {"name": "PUBG MOBILE", "revenueM": 40.33, "age18": 36.1, "age25": 43.2, "age35": 13.4, "age45": 5.7, "age55": 1.6},
                {"name": "Play Together", "revenueM": 36.48, "age18": 19.7, "age25": 31.2, "age35": 33.3, "age45": 12.9, "age55": 2.9},
                {"name": "Wild Rift", "revenueM": 32.23, "age18": 37.9, "age25": 50.2, "age35": 7.4, "age45": 3.2, "age55": 1.4},
                {"name": "TFT", "revenueM": 30.48, "age18": 37.8, "age25": 47.6, "age35": 8.8, "age45": 3.9, "age55": 1.8},
                {"name": "Last War", "revenueM": 23.08, "age18": 24.1, "age25": 45.3, "age35": 21.6, "age45": 7.5, "age55": 1.5},
                {"name": "ICA", "revenueM": 16.90, "age18": 28.2, "age25": 44.6, "age35": 19.5, "age45": 6.1, "age55": 1.6},
                {"name": "Coin Master", "revenueM": 16.10, "age18": 25.3, "age25": 35.4, "age35": 26.2, "age45": 10.7, "age55": 2.4},
            ],
            "source": "SensorTower (Revenue-adjusted for Vietnam market; Demographics of SE_ASIA is used as proxy for VN and app variants are combined using average 2025 VN DAU weights).",
        },
        "11": population_pyramid,
        "12": {
            "years": [1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            "people": [32160241, 32806999, 33423497, 34027280, 34648624, 35249864, 35867616, 36433926, 36907313, 37409647, 37975179, 38588556, 39203382, 39755059, 40209632, 40554354, 40763802, 40847248, 40817893, 40691288, 40510440, 40303891, 40080456, 39843468, 39591159, 39309806, 39078379, 38936967, 38839696, 38656010, 38397652, 38234968, 38147910, 38083357, 38053183, 37988506, 37807199, 37581281, 37364207, 37206403, 37130318, 37107883, 37126859, 37184411, 37235428, 37209509],
            "share": [61.3, 61.0, 60.8, 60.4, 60.0, 59.7, 59.4, 59.2, 58.7, 58.3, 58.0, 57.7, 57.4, 57.1, 56.7, 56.3, 55.7, 55.0, 54.2, 53.3, 52.5, 51.7, 50.9, 50.1, 49.3, 48.5, 47.6, 46.6, 45.6, 44.7, 43.9, 43.2, 42.6, 42.0, 41.5, 40.9, 40.2, 39.5, 38.8, 38.3, 37.9, 37.5, 37.2, 37.1, 36.9, 36.6],
            "maxPeople": 42000000,
            "maxShare": 65.0,
        },
        "13": {
            "headline": [
                {"value": "100.7M", "label": "smartphone subscribers", "note": "Feb 2024"},
                {"value": "127.6", "label": "mobile subs per 100 people", "note": "2024"},
            ],
            "bars": [
                {"label": "4G population coverage", "value": 99.0, "display": "99%", "note": "Nov 2024"},
                {"label": "5G population coverage", "value": 90.0, "display": "90%", "note": "Feb 2026"},
                {"label": "smartphone share of mobile users", "value": 88.7, "display": "88.7%", "note": "Oct 2024"},
                {"label": "internet users", "value": 84.15, "display": "84.15%", "note": "2024"},
                {"label": "fiber-connected households", "value": 82.3, "display": "82.3%", "note": "Oct 2024"},
                {"label": "mobile broadband subs per 100 people", "value": 91.9, "display": "91.9", "note": "Jul 2024"},
            ],
            "pcUrban": 68,
            "consoleNiche": "<5%",
            "youngCue": "Pew found that 88% of Vietnamese aged 18-36 already used the internet at least occasionally or owned a smartphone in 2017, and smartphone use among Vietnamese aged 18-29 was nine-in-ten or more in 2018. Combined with today's subscriber and coverage data, under-35 mobile access is likely already close to saturation.",
            "pcRead": "Q&Me's September 2017 urban survey found that 68% of 18-39 respondents in Hanoi and Ho Chi Minh City owned either a desktop or a laptop, including 21% who owned both.",
            "consoleRead": "Console is still a niche channel. Digital in Asia's March 2026 Vietnam market synthesis says console gaming penetration remains below 5%, with only Sony maintaining official retail presence.",
            "source": "Sources: Freedom House; World Bank/TradingEconomics; Vietnam+; VietnamNet; VnExpress; Pew Research; Q&Me; Digital in Asia.",
        },
    }

def build_movie_revenue_data(vietnam_movie_revenue):
    return {
        "30": {
            **vietnam_movie_revenue,
        },
    }

def build_history_special_data():
    return {
        "14": {
            "era_key": "console-button",
            "era_title": "Dawn of Gaming & Console Button Era",
            "years": "1990s",
            "summary": "Following Doi Moi, game devices entered Vietnam through informal trade channels. The market had no official publishers, and NES clones, Sega Mega Drive units, and later PS1 machines were still luxury items.",
            "visual_label": "Placeholder collage: 4-button electronics, cartridge console shops, arcade corners, PS1 rental counters",
            "visual_note": "Representative image for cartridge-console culture and neighborhood play.",
            "image_url": "images/era1.jpg",
            "image_credit": "Image: local file - era1.jpg",
            "milestones": [
                "Imported and hand-carried electronics seeded Vietnam's first game market in the 1990s.",
                "NES-style '4-button electronics' and later PS1 machines became iconic but still premium devices.",
                "Hourly rented cartridge-console shops and arcade centers became the first gaming venues."
            ],
            "culture": "Gaming was hyper-local and face-to-face. Spectators often outnumbered players, shouting advice and cheering while neighborhood kids waited for their turns. The slang term 'pha dao' came from this era.",
            "acceptance": "There was effectively no legal framework because the market was tiny and spontaneous. Parents mainly saw gaming as a childish waste of time linked to laziness and delinquency.",
            "source": "The Evolution of Gaming in Vietnam research document.",
        },
        "15": {
            "era_key": "pc-internet",
            "era_title": "Golden Age of PC Gaming & Internet Boom",
            "years": "2000 - 2010",
            "summary": "ADSL spread quickly from 2003 to 2004, enabling the first major local publishers such as Vinagame, VTC Game, and FPT Online. Vietnam shifted from offline play into the first large online-game boom.",
            "visual_label": "Placeholder collage: Quan Net rows, Counter-Strike, AoE, Vo Lam Truyen Ky, scratch cards",
            "visual_note": "Representative image for Quan Net culture, LAN classics, and the first online-game boom.",
            "image_url": "images/era2.webp",
            "image_credit": "Image: local file - era2.webp",
            "milestones": [
                "ADSL rollout and Quan Net expansion made PC gaming the dominant format.",
                "Counter-Strike, AoE, Warcraft III DotA, and online titles like Vo Lam Truyen Ky and MU defined the era.",
                "Scratch cards, 'cam chuot', guilds, and real-money item trading became everyday behavior."
            ],
            "culture": "Quan Net culture became a defining social phenomenon for the 8x and 9x generations. Virtual guilds spilled into nationwide offline meetups, and the in-game black market peaked.",
            "acceptance": "Government regulation tightened through curfews, playtime restrictions, and licensing. Social stigma also hit its peak, with mainstream media turning games into a scapegoat for addiction and academic failure.",
            "source": "The Evolution of Gaming in Vietnam research document.",
        },
        "16": {
            "era_key": "mobile-esports",
            "era_title": "Mobile Shift & the Dawn of Esports",
            "years": "2011 - 2020",
            "summary": "3G and 4G infrastructure, affordable smartphones, and Garena's free-to-play model reshaped the market. Flappy Bird then proved that a Vietnamese developer could create a game with global impact.",
            "visual_label": "Placeholder collage: smartphones, Flappy Bird, Lien Quan, Free Fire, streamers, esports stages",
            "visual_note": "Representative image for smartphone-led play, streaming culture, and the rise of esports.",
            "image_url": "images/era3.png",
            "image_credit": "Image: local file - era3.png",
            "milestones": [
                "Affordable smartphones and 3G/4G shifted gaming from cafes into daily mobile routines.",
                "League of Legends, Lien Quan Mobile, PUBG Mobile, and Free Fire became defining hits.",
                "Streaming and esports professionalized with big prize pools, clubs, and visible gaming celebrities."
            ],
            "culture": "Gaming became mass audiovisual entertainment. Streamers like Do Mixi, PewPew, and Cris Devil Gamer turned play into a spectator format, while esports became a structured entertainment ecosystem.",
            "acceptance": "Government adopted a more open and pragmatic stance by recognizing esports as a competitive sport. Society became more accepting of professional gamers and streamers, though parents still worried about screen time.",
            "source": "The Evolution of Gaming in Vietnam research document.",
        },
        "17": {
            "era_key": "digital-economy",
            "era_title": "Cross-Platform Games & the Digital Economy Era",
            "years": "2021 - Present",
            "summary": "5G, cloud technology, and stronger engines pushed Vietnam into a cross-platform and globally visible phase. Amanotes, iKame, and Sky Mavis showed that Vietnamese studios could build for global audiences at scale, while GameVerse and new university majors signaled that the ecosystem itself was becoming more formal and visible.",
            "visual_label": "Placeholder collage: GameVerse, Amanotes, iKame, Axie Infinity, cross-platform play, university majors",
            "visual_note": "Representative image for GameVerse, the creative-tech narrative, and Vietnam's globalized game ecosystem.",
            "image_url": "images/era4.jpeg",
            "image_credit": "Image: local file - era4.jpeg",
            "milestones": [
                "Amanotes, iKame, and Sky Mavis became high-visibility proof that Vietnamese studios could scale globally rather than only publish imported games locally.",
                "The 2021-2022 blockchain wave, led by Axie Infinity, briefly put Vietnam at the center of global Web3 gaming discussion.",
                "In 2024, Vietnamese apps and games generated more than 2,000 billion VND from international users on Google Play.",
                "In 2025, Vietnamese-made mobile games reached 4.9 billion global downloads."
            ],
            "culture": "Gaming now blends into the lifestyle of Gen Z and Gen Alpha, but the defining shift is that Vietnam is no longer just consuming games. Public-facing events like GameVerse and globally successful studios make production itself part of gaming culture.",
            "acceptance": "Government now frames gaming as a spearhead digital-economy sector, and major urban audiences increasingly view it as a high-tech creative industry rather than a social problem. This is also the first era when export success, education, and public events clearly move in the same direction.",
            "source": "The Evolution of Gaming in Vietnam research document; ABEI; Google App Summit 2025; VnExpress GameVerse 2026.",
        },
        "18": {
            "columns": [
                "Aspect",
                "Console Button\n1990s",
                "PC & Internet Boom\n2000 - 2010",
                "Mobile Shift & Esports\n2011 - 2020",
                "Digital Economy Era\n2021 - Present",
            ],
            "rows": [
                {
                    "aspect": "Gaming Culture",
                    "c1": "Hyper-local and face-to-face. Play revolved around rented consoles, arcade corners, and neighborhood spectatorship.",
                    "c2": "Quan Net culture became a mass youth ritual. Guilds, LAN titles, scratch cards, and online communities defined daily play.",
                    "c3": "Gaming turned personal, mobile, and highly social. Streaming and esports made play both participatory and spectator-friendly.",
                    "c4": "Gaming blends into digital lifestyle, but production is now part of the culture too through globally visible Vietnamese studios.",
                },
                {
                    "aspect": "Social Acceptance",
                    "c1": "Mostly seen as a childish distraction. Public debate stayed limited because the market was still small and informal.",
                    "c2": "This was the peak era of stigma. Curfews, licensing pressure, and media panic framed gaming as addiction and academic risk.",
                    "c3": "Acceptance improved as smartphones normalized gaming and esports gained recognition, though family concern over screen time remained.",
                    "c4": "Gaming is increasingly seen as a creative-tech and digital-economy sector, even if concerns about youth behavior still coexist.",
                },
                {
                    "aspect": "VN Game Production",
                    "c1": "There was no real domestic production base. Hardware and content mainly arrived through informal imports and gray channels.",
                    "c2": "Vietnam built its first large-scale publishing and operations layer by localizing imported online titles for the domestic market.",
                    "c3": "Vietnamese studios became more visible through mobile-first development, while local publishers expanded into esports and live operations.",
                    "c4": "Domestic studios now produce for global audiences at export scale, with names like Amanotes, iKame, and Sky Mavis proving outward reach.",
                },
            ],
            "source": "The Evolution of Gaming in Vietnam research document.",
        },
        "19": {
            "columns": [
                "Foundational Factor",
                "1990s\nPost-Doi Moi & Analog",
                "2000s\nIndustrializing & Broadband",
                "2010s\nMobile Leapfrog & Startup Boom",
                "2021 - 2026\nDigital Economy & Global Export",
            ],
            "rows": [
                {
                    "aspect": "Economic Condition",
                    "c1": "- Post-embargo recovery.\n- Low disposable income.\n- Survival-oriented economy.",
                    "c2": "- Rapid GDP growth.\n- Emerging middle class.\n- Early industrialization & urbanization.",
                    "c3": "- Transition to lower-middle-income status.\n- Massive FDI inflows.\n- Tech startup ecosystem takes root.",
                    "c4": "- High-growth digital economy.\n- Venture capital hub.\n- Surge in premium/discretionary spending.",
                },
                {
                    "aspect": "State of Technology",
                    "c1": "- Purely analog.\n- Fixed landlines are a luxury.\n- CRT screens & physical media.",
                    "c2": "- Fixed-line ADSL broadband.\n- Desktop computing boom.\n- Basic local server architecture.",
                    "c3": "- 3G/4G mobile network ubiquity.\n- Mass smartphone democratization.\n- Early cloud infrastructure.",
                    "c4": "- 5G infrastructure & fiber-to-the-home.\n- Pervasive cloud computing.\n- Advanced AI & software automation.",
                },
                {
                    "aspect": "Human Resource Capability",
                    "c1": "- High basic literacy.\n- Severe lack of software/tech skills.\n- Focus on mechanical/hardware vocational training.",
                    "c2": "- First wave of Computer Science graduates.\n- Emergence of IT System Administrators.\n- Basic software localization & data entry skills.",
                    "c3": "- Boom of self-taught mobile developers.\n- Growth of large-scale IT outsourcing.\n- Rise of professional digital content creators.",
                    "c4": "- World-class creative-tech workforce.\n- High-tier software engineers & UI/UX designers.\n- Formalized tech university pipelines.",
                },
                {
                    "aspect": "Global Cultural Integration",
                    "c1": "- Geopolitically isolated.\n- Delayed trickle of foreign media via border trade.\n- Absolute English language barriers.",
                    "c2": "- Regional Asian integration.\n- Massive cultural influence from China/South Korea pop culture.",
                    "c3": "- Global Western & Asian cultural blend.\n- High English proficiency among urban youth.\n- Heavy social media assimilation.",
                    "c4": "- Native global citizens (Gen Z/Alpha).\n- Real-time synchronization with global internet culture.\n- Transition from cultural consumer to global cultural exporter.",
                },
                {
                    "aspect": "Consumerism & Payment",
                    "c1": "- Strict cash-only society.\n- Deeply ingrained saving culture.\n- Consumerism limited to basic, physical commodities.",
                    "c2": "- Early spending on intangible leisure.\n- Prepaid telecom \"scratch cards\" act as primitive digital currency.",
                    "c3": "- Shift to digital entertainment spending.\n- Emergence of e-wallets (MoMo).\n- Normalization of micro-transactions.",
                    "c4": "- Ubiquitous cashless economy.\n- Standardized QR payments (VietQR).\n- Fully matured digital consumerism focused on instant emotional/experiential value.",
                },
            ],
            "source": "Vietnam_Macro_Transformation_Bedrock.pptx, slide 3.",
        },
    }

def build_media_special_data(youtube_share, youtube_top_videos, youtube_day_unique, mobile_game_downloads):
    return {
        "20": {
            "yearly_counts": [
                {"year": 2010, "vietnamese": 4, "non_vietnamese": 18, "total": 22},
                {"year": 2011, "vietnamese": 12, "non_vietnamese": 88, "total": 100},
                {"year": 2012, "vietnamese": 22, "non_vietnamese": 126, "total": 148},
                {"year": 2013, "vietnamese": 20, "non_vietnamese": 172, "total": 192},
                {"year": 2014, "vietnamese": 26, "non_vietnamese": 169, "total": 195},
                {"year": 2015, "vietnamese": 40, "non_vietnamese": 187, "total": 227},
                {"year": 2016, "vietnamese": 41, "non_vietnamese": 195, "total": 236},
                {"year": 2017, "vietnamese": 35, "non_vietnamese": 235, "total": 270},
                {"year": 2018, "vietnamese": 38, "non_vietnamese": 238, "total": 276},
                {"year": 2019, "vietnamese": 40, "non_vietnamese": 225, "total": 265},
                {"year": 2020, "vietnamese": 22, "non_vietnamese": 168, "total": 190},
                {"year": 2021, "vietnamese": 14, "non_vietnamese": 94, "total": 108},
                {"year": 2022, "vietnamese": 34, "non_vietnamese": 198, "total": 232},
                {"year": 2023, "vietnamese": 25, "non_vietnamese": 267, "total": 292},
                {"year": 2024, "vietnamese": 28, "non_vietnamese": 251, "total": 279},
                {"year": 2025, "vietnamese": 46, "non_vietnamese": 232, "total": 278},
            ],
            "top_movies": [
                {"release_year": 2025, "movie_name": "Mưa Đỏ", "revenue_vnd": 714030389098},
                {"release_year": 2024, "movie_name": "Mai", "revenue_vnd": 551219434134},
                {"release_year": 2024, "movie_name": "Lật Mặt 7: Một Điều Ước", "revenue_vnd": 482735908932},
                {"release_year": 2023, "movie_name": "Nhà Bà Nữ", "revenue_vnd": 459587516927},
                {"release_year": 2021, "movie_name": "Bố Già", "revenue_vnd": 395129426000},
                {"release_year": 2025, "movie_name": "Bộ Tứ Báo Thủ", "revenue_vnd": 332177505723},
                {"release_year": 2023, "movie_name": "Lật Mặt 6: Tấm Vé Định Mệnh", "revenue_vnd": 273105461926},
                {"release_year": 2025, "movie_name": "Tử Chiến Trên Không", "revenue_vnd": 251893119016},
                {"release_year": 2025, "movie_name": "Thám Tử Kiên", "revenue_vnd": 248927360616},
                {"release_year": 2025, "movie_name": "Nhà Gia Tiên", "revenue_vnd": 242523470236},
                {"release_year": 2025, "movie_name": "Lật Mặt 8", "revenue_vnd": 231998509909},
                {"release_year": 2025, "movie_name": "Nụ Hôn Bạc Tỷ", "revenue_vnd": 211617608755},
                {"release_year": 2025, "movie_name": "Truy Tìm Long Điền Hương", "revenue_vnd": 206735411821},
                {"release_year": 2020, "movie_name": "Tiệc Trăng Máu", "revenue_vnd": 172745666799},
                {"release_year": 2025, "movie_name": "Địa Đạo: Mặt Trời Trong Bóng Tối", "revenue_vnd": 172474675105},
                {"release_year": 2019, "movie_name": "Mắt Biếc", "revenue_vnd": 165092870244},
                {"release_year": 2021, "movie_name": "Lật Mặt 5: 48H", "revenue_vnd": 156741535974},
                {"release_year": 2024, "movie_name": "Linh Miêu: Quỷ Nhập Tràng", "revenue_vnd": 149673909850},
            ],
            "source": "Moveek + Box Office Vietnam merged cinema dataset.",
        },
        "21": {
            "yearly_counts": [
                {"year": 2010, "vietnamese": 0, "non_vietnamese": 5, "total": 5},
                {"year": 2011, "vietnamese": 0, "non_vietnamese": 13, "total": 13},
                {"year": 2012, "vietnamese": 0, "non_vietnamese": 20, "total": 20},
                {"year": 2013, "vietnamese": 0, "non_vietnamese": 20, "total": 20},
                {"year": 2014, "vietnamese": 0, "non_vietnamese": 17, "total": 17},
                {"year": 2015, "vietnamese": 0, "non_vietnamese": 20, "total": 20},
                {"year": 2016, "vietnamese": 6, "non_vietnamese": 23, "total": 29},
                {"year": 2017, "vietnamese": 0, "non_vietnamese": 22, "total": 22},
                {"year": 2018, "vietnamese": 0, "non_vietnamese": 27, "total": 27},
                {"year": 2019, "vietnamese": 5, "non_vietnamese": 40, "total": 45},
                {"year": 2020, "vietnamese": 5, "non_vietnamese": 9, "total": 14},
                {"year": 2021, "vietnamese": 0, "non_vietnamese": 3, "total": 3},
                {"year": 2022, "vietnamese": 11, "non_vietnamese": 29, "total": 40},
                {"year": 2023, "vietnamese": 10, "non_vietnamese": 54, "total": 64},
                {"year": 2024, "vietnamese": 10, "non_vietnamese": 29, "total": 39},
                {"year": 2025, "vietnamese": 48, "non_vietnamese": 35, "total": 83},
            ],
            "image_url": "images/anh-trai-say-hi-concert.jpg",
            "image_title": "Anh Trai Say Hi as a local-concert breakout",
            "image_caption": "Anh Trai Say Hi helps illustrate how Vietnamese-produced concerts are now capable of generating stadium-scale hype and visual identity that fans once associated mainly with imported acts.",
            "image_credit": "Image: Vie Channel via VnExpress, article 'Concert Anh trai say hi tao suc hut' (October 3, 2024).",
            "source": "concertarchives.org concert sheet for counts; Vie Channel / VnExpress for the image.",
        },
        "22": {
            "series": youtube_share["series"],
            "avgPct": youtube_share["avgPct"],
            "latestPct": youtube_share["latestPct"],
            "minPct": youtube_share["minPct"],
            "maxPct": youtube_share["maxPct"],
            "markers": youtube_share["markers"],
            "dayUniqueVideos": youtube_day_unique,
            "topVideos": youtube_top_videos,
            "source": "most_popular_vn_daily_video_language_counts.csv and most_popular_vn_with_is_vietnamese_video.csv.",
        },
        "23": {
            **mobile_game_downloads,
        },
        "24": {
            "eras": [
                {
                    "name": "Console Button Era",
                    "years": "1990s",
                    "summary": "Informal rented consoles and neighborhood play seeded the first generation of gamers before any formal industry existed.",
                },
                {
                    "name": "PC & Internet Boom",
                    "years": "2000 - 2010",
                    "summary": "ADSL, Quan Net culture, and the first online publishers turned gaming into a mass youth habit.",
                },
                {
                    "name": "Mobile Shift & Esports",
                    "years": "2011 - 2020",
                    "summary": "Smartphones, free-to-play, streaming, and esports normalized gaming as everyday entertainment.",
                },
                {
                    "name": "Digital Economy Era",
                    "years": "2021 - Present",
                    "summary": "Vietnam now consumes, produces, and exports games as part of a broader creative-tech ecosystem.",
                },
            ],
            "factors": [
                {
                    "name": "Population & Demographics",
                    "copy": "Vietnam still has a large gamer-relevant youth base today, but the under-25 share is already trending down. Near-term demand remains healthy; medium-term growth may slow unless products win older cohorts such as 35-44.",
                },
                {
                    "name": "Income",
                    "copy": "GDP per capita keeps rising and has outgrown several ASEAN peers, which supports more discretionary spending on games, live services, and in-game purchases.",
                },
                {
                    "name": "Hardware & Internet Infrastructure",
                    "copy": "Smartphone access, 4G/5G coverage, and internet penetration are already mass-market, making distribution and everyday play structurally easy across the country.",
                },
                {
                    "name": "Consumerism & Payment",
                    "copy": "Vietnam has moved from cash-only habits toward digital payments, e-wallets, and instant digital spending, which makes monetized gaming behavior much easier to sustain.",
                },
            ],
            "source": "Slides 8-23 synthesis: World Bank; NSO Vietnam; PopulationPyramids/UN WPP; SensorTower; Q&Me; concert/cinema/YouTube/mobile local datasets; The Evolution of Gaming in Vietnam research document.",
        },
        "25": {
            "cards": [
                {
                    "name": "Movies",
                    "metric": "46 local titles in 2025",
                    "headline": "Domestic cinema is scaling up",
                    "copy": "Vietnamese movies are still the minority of the total slate, but their yearly count is clearly up versus 2010 and the top box-office table now includes multiple major local hits.",
                    "image_url": "https://bcp.cdnchinhphu.vn/thumb_w/777/334894974524682240/2025/11/23/5320458781221940676663682014244556147326010710n-1763867996083893343946.jpg",
                    "image_credit": "Image: Bao Chinh Phu / Mua Do Oscar 2026 article.",
                },
                {
                    "name": "Concerts",
                    "metric": "48 VN vs 35 non-VN in 2025",
                    "headline": "Local live entertainment can now lead",
                    "copy": "Historically foreign acts dominated the listed concert market, yet local concerts surged after 2022 and in 2025 local concerts even outnumbered non-Vietnamese ones in the dataset.",
                    "image_url": "https://backstage.vn/storage/2025/08/concert-em-xinh-say-hi-2.jpg",
                    "image_credit": "Image: Backstage.vn concert-em-xinh-say-hi-2.jpg.",
                },
                {
                    "name": "YouTube",
                    "metric": "70.8% average VN share",
                    "headline": "Everyday attention is more mixed",
                    "copy": "Vietnamese videos still dominate trending overall, but the share has been easing over time. This suggests stronger exposure to international creators as language fluency and global integration deepen.",
                    "image_url": "https://www.tubefilter.com/wp-content/uploads/2024/06/mrbeast-wilderness-1400x825.jpg",
                    "image_credit": "Image: TubeFilter / MrBeast wilderness article.",
                },
            ],
            "source": "Slides 16-23 synthesis: Moveek + Box Office Vietnam; concertarchives.org; most_popular_vn_daily_video_language_counts.csv; most_popular_vn_with_is_vietnamese_video.csv.",
        },
    }


def build_entertainment_market_comparison_special_data():
    return {
        "26": {
            "rows": [
                {
                    "group": "Movies",
                    "number": "Vietnamese cinema releases rose from 4 titles in 2010 to 46 in 2025. Vietnamese films also reached 59% of box-office revenue in 2025.",
                    "story": "Local films are no longer a niche alternative. They are increasingly competitive with foreign releases on both scale and commercial traction.",
                    "dominator": "VN",
                    "gaining": "VN",
                },
                {
                    "group": "Large Concerts",
                    "number": "Vietnamese large-scale concerts grew from virtually none to 48 in 2025, overtaking foreign concerts in the dataset.",
                    "story": "Vietnamese organizers and artists now have both the audience pull and production confidence to lead major live events.",
                    "dominator": "VN",
                    "gaining": "VN",
                },
                {
                    "group": "Ticketbox Physical Events",
                    "number": "From 2023 to 2025, Vietnamese organizers dominated Ticketbox event supply and covered a wider spread of price tiers, from budget to ultra-premium.",
                    "story": "Domestic event operators are not only larger on the platform; they also appear better at serving multiple audience segments and premium tiers.",
                    "dominator": "VN",
                    "gaining": "VN",
                },
                {
                    "group": "YouTube",
                    "number": "Vietnamese videos still held the majority overall, but share fell from 92% in July 2022 to a low of 44% in February 2025.",
                    "story": "YouTube remains locally strong, but international content is gaining ground as Vietnamese users consume more borderless, globally distributed entertainment.",
                    "dominator": "VN",
                    "gaining": "Foreign",
                },
                {
                    "group": "Mobile Games",
                    "number": "Vietnam's top-10 most-downloaded mobile games remain overwhelmingly foreign-led, though Vietnamese titles still break into the leaderboard occasionally.",
                    "story": "Mobile gaming is still foreign-dominated, but local titles such as Tro Ve Tuoi Tho show that Vietnamese-made products can still win meaningful visibility.",
                    "dominator": "Foreign",
                    "gaining": "VN",
                },
            ],
            "note": "YouTube and mobile games face more borderless competition because they are free or low-friction, high-frequency formats. Physical and higher-investment formats leave more room for local cultural fit and domestic supply strength.",
            "source": "[Research] Examining VN Gaming Market Opportunity 2026 - Data Sheet - [Analysis] Comparing Entertainment Markets.csv",
        },
    }


def build_executive_summary_special_data():
    raw_rows = read_research_csv_rows(EXEC_SUMMARY_ANALYSIS_CSV_NAME)
    content_map = {}
    for row in raw_rows:
        if len(row) < 3:
            continue
        title = str(row[1]).strip()
        content = str(row[2]).strip()
        if title and content:
            content_map[title] = content

    return {
        "38": {
            "headline": "Vietnam's gaming market matured from an informal gray market into a full-fledged digital-entertainment ecosystem.",
            "cards": [
                {
                    "label": "Industry Development",
                    "headline": "The market gained real depth in both consumption and domestic production over roughly three decades.",
                    "points": [
                        "From the 1990s to 2025, Vietnam moved from a niche black market of Chinese-made NES clones into a developed gaming market with strength on both the demand side and the local-production side.",
                        "This was not just a rise in play volume. It was a transition into a more complete gaming economy with broader participation, stronger monetization, and visible local studio capability.",
                    ],
                },
                {
                    "label": "Regulation & Acceptance",
                    "headline": "Public framing shifted from social-risk containment toward mainstream habit and strategic tech-business value.",
                    "points": [
                        "Government regulation and social acceptance changed materially as gaming moved from being framed around addiction and academic risk toward becoming an everyday behavior in a smartphone-led market.",
                        "Gaming is now also viewed more credibly as a technology business with export and economic upside, not only as a youth-management problem.",
                    ],
                },
                {
                    "label": "Macro Tailwinds",
                    "headline": "Five structural tailwinds underpin that industry expansion.",
                    "points": [
                        "Economics: from post-embargo recovery and survival spending to a bustling digital economy with discretionary demand.",
                        "Technology: from analog lines and CRT screens to 5G connectivity and pervasive mobile usage.",
                        "Human resources: from basic literacy and hardware training to a creative-tech workforce and formal university pipeline.",
                        "Global integration: from geopolitical isolation to native global citizens and the first signs of cultural export.",
                        "Consumerism and payment: from cash-only habits to a cashless economy and mature digital consumption.",
                    ],
                },
            ],
            "source": content_map.get("The Development of Gaming Industry in Vietnam", EXEC_SUMMARY_ANALYSIS_CSV_NAME),
        },
        "39": {
            "demand": [
                "Most near-term demand factors are favorable: income is rising relatively fast, digital-entertainment demand is increasing, the installed internet/mobile base is strong, and Vietnam still has a large youth audience.",
                "The main structural risk is demographic aging: the under-25 cohort is shrinking as a share of population, which may reduce the long-run target audience for youth-skewing games.",
                "Across movies, concerts, YouTube, and other entertainment formats, Vietnamese audiences no longer show an automatic bias toward foreign content; local entertainment is already dominating or gaining ground in multiple categories.",
                "Mobile gaming remains the clearest exception: foreign titles still dominate the top-download charts, although domestically made titles such as Tro Ve Tuoi Tho show that breakthrough local demand is possible if quality and marketing can match foreign competition.",
            ],
            "supply": [
                "Government now provides visible support for domestic game development through official recognition, lower tax rates, and the opening of formal university pathways for game education.",
                "Vietnamese studios have already proven global capability through names such as Amanotes, iKame, and Sky Mavis rather than remaining only low-end service providers.",
                "The main mismatch is strategic direction: much studio effort and policy logic still point toward export-first success under a 'Do local, go global' model, likely because export markets offer easier monetization and better profitability than pushing Made-in-Vietnam games for Vietnamese players.",
            ],
            "source": content_map.get("Demand & Supply for Gaming", EXEC_SUMMARY_ANALYSIS_CSV_NAME),
        },
    }


def build_supply_special_data():
    return {
        "31": {
            "yearly_counts": [
                {"year": 2023, "vietnam": 408, "foreign": 32},
                {"year": 2024, "vietnam": 508, "foreign": 106},
                {"year": 2025, "vietnam": 1437, "foreign": 222},
            ],
            "peakVietnam": 1437,
            "peakForeign": 222,
            "totalVietnam": 2353,
            "totalForeign": 360,
            "readthrough": "Data from Ticketbox, the most popular e-commerce platform in Vietnam for event tickets, also highlights the dominance of domestic events' sold-out ticket tiers versus foreign. In 2025, 86.6% of all sold-out ticket tiers on Ticketbox are Vietnamese domestic events.",
            "note": "Sold-out ticket-tier counts are joined to the event-level foreign_event flag and filtered to entertainment categories only: music, theatersandart, others, and sport.",
            "source": "Ticketbox event-level source joined to entertainment-only Vietnam/foreign sold-out tier summaries; categories kept: music, theatersandart, others, sport.",
        },
        "29": {
            "foreign": {
                "ticketCount": load_wide_csv_table("ticketbox_foreign_events_entertainment_only_yearly_price_bucket_ticket_tier_count_2023_2025_wide.csv"),
                "soldCount": load_wide_csv_table("ticketbox_foreign_events_entertainment_only_yearly_price_bucket_soldout_ticket_tier_count_2023_2025_wide.csv"),
                "soldRate": load_wide_csv_table("ticketbox_foreign_events_entertainment_only_yearly_price_bucket_soldout_rate_2023_2025_wide.csv"),
            },
            "vietnam": {
                "ticketCount": load_wide_csv_table("ticketbox_vietnam_events_entertainment_only_yearly_price_bucket_ticket_tier_count_2023_2025_wide.csv"),
                "soldCount": load_wide_csv_table("ticketbox_vietnam_events_entertainment_only_yearly_price_bucket_soldout_ticket_tier_count_2023_2025_wide.csv"),
                "soldRate": load_wide_csv_table("ticketbox_vietnam_events_entertainment_only_yearly_price_bucket_soldout_rate_2023_2025_wide.csv"),
            },
            "source": "Ticketbox tier rows joined to the foreign_event event sheet; entertainment-only categories: music, theatersandart, others, sport.",
        },
        "34": {
            "timeline": [
                {
                    "label": "Early internet era",
                    "years": "2013 and earlier",
                    "copy": "Policy was mainly defensive. Games were framed around addiction, academic decline, and social control rather than as a legitimate creative-tech industry.",
                },
                {
                    "label": "Strategic policy pivot",
                    "years": "2024-2025",
                    "copy": "The state officially reclassified gaming as part of the national cultural and digital-content economy and began promoting local studios under a 'do local, go global' logic.",
                },
                {
                    "label": "Compliance-heavy growth",
                    "years": "Decree 147 era",
                    "copy": "Support now coexists with strict localization rules, real-name verification, content control, and app-store enforcement that favor serious local operators over casual cross-border entrants.",
                },
            ],
            "left_title": "What changed in the state's stance",
            "left_points": [
                "Gaming moved from a containment problem to one of Vietnam's key cultural industries by late 2025.",
                "The policy objective is no longer only harm reduction; it is also to commercialize, professionalize, and export domestic game production.",
                "This reflects a broader national push to move from low-cost assembly into higher-value digital content and creative technology.",
            ],
            "right_title": "What Decree 147 means in practice",
            "right_points": [
                "Foreign operators can no longer serve Vietnam remotely without local legal presence and compliance infrastructure.",
                "Games are split into G1-G4 tiers with different licensing steps, but all require formal domestic approval.",
                "Platforms must support real-name checks, youth playtime limits, localized data handling, and strict content restrictions.",
                "Full pre-launch compliance can still require roughly 8-15 months and substantial setup cost, raising the entry barrier.",
            ],
            "bottom_kpis": [
                {"value": "20 days", "label": "G1 review window after Decree 147"},
                {"value": "184", "label": "active G1 licenses left by Q1 2026"},
                {"value": "$0.5M-$2.0M", "label": "estimated compliant pre-launch capital"},
            ],
            "source": "Vietnamese Game Development Government Support.docx",
        },
        "35": {
            "direct_support": [
                "Resolutions 79 and 80 position digital cultural products, including games, inside a broader national cultural-industry plan.",
                "The state targets 5,000 specialists for history-focused educational game development and links support to digitizing heritage into interactive products.",
                "GameVerse and the GameHub competition function as state-backed promotional and incubation platforms for local studios.",
            ],
            "indirect_support": [
                "Qualified software producers can access a 10% CIT rate for 15 years, versus the normal 20% rate.",
                "Studios can receive a 4-year full CIT exemption followed by a 50% reduction for the next 9 years.",
                "Additional tools include VAT exemption, 200% R&D deduction, SME startup incentives, and tax-deductible science & technology funds.",
            ],
            "talent_pipeline": [
                "PTIT launched Vietnam's first public Game Design and Development degree in 2024 and expanded into Game Art and Digital Cinema Technology in 2026.",
                "UIT partnered with VNGGames and Roblox to train students through publishable game projects on the Roblox platform.",
                "RMIT, FPT Polytechnic, and SAMA expand the pipeline beyond pure computer science into game design, art, and production practice.",
            ],
            "highlight": {
                "value": "50,000",
                "label": "GameVerse 2026 visitors",
                "note": "up from about 20,000 at its 2023 launch",
            },
            "source": "Vietnamese Game Development Government Support.docx",
        },
        "36": {
            "evolution": [
                {
                    "phase": "Outsourcing & training academies",
                    "copy": "Glass Egg and Gameloft gave Vietnam its first disciplined pipelines in 3D art, QA, and structured mobile production.",
                },
                {
                    "phase": "Mobile self-publishing breakout",
                    "copy": "Flappy Bird proved a Vietnamese developer could reach the world directly, then Amanotes, ABI/Onesoft, and Zitga scaled high-volume mobile publishing.",
                },
                {
                    "phase": "Premium PC and global innovation",
                    "copy": "Sky Mavis, Hoa, Than Trung, God of Weapons, and Tai Uong show that local teams can now build exportable premium and technically sophisticated products.",
                },
            ],
            "studios": [
                "Glass Egg: AAA art workflows for Call of Duty, Spider-Man, Need for Speed, and Forza.",
                "Amanotes: first Southeast Asian publisher to reach the 3B-download club in 2023.",
                "Sky Mavis: Axie Infinity and Ronin proved global-scale product and infrastructure ambition.",
                "Premium indies: Hoa, Than Trung, God of Weapons, and Tai Uong show credible PC/Steam capability.",
            ],
            "kpis": [
                {"value": "27,388", "label": "new game titles launched in 2025"},
                {"value": "8.5B", "label": "Google Play downloads by local publishers in 2025"},
                {"value": "94.47%", "label": "estimated export share of VN-made downloads"},
            ],
            "source": "Vietnam Game Production Ecosystem_ Evolution.docx",
        },
    }

def build_special_data():
    youtube_share = load_daily_vietnamese_video_share()
    youtube_top_videos, youtube_day_unique = load_trending_videos_for_day(YOUTUBE_TRENDING_SNAPSHOT_DATE)
    mobile_game_downloads = load_vn_mobile_game_downloads_summary()
    vietnam_movie_revenue = load_vietnam_movie_revenue_summary()
    population_pyramid = load_population_pyramid()
    return merge_special_data(
        build_market_special_data(population_pyramid),
        build_movie_revenue_data(vietnam_movie_revenue),
        build_history_special_data(),
        build_media_special_data(youtube_share, youtube_top_videos, youtube_day_unique, mobile_game_downloads),
        build_executive_summary_special_data(),
        build_entertainment_market_comparison_special_data(),
        build_supply_special_data(),
        load_donor_supply_special_data(),
    )

HTML_TEMPLATE = (ROOT / "workbench_template.html").read_text(encoding="utf-8")


def build_html(seed_csv):
    template = HTML_TEMPLATE.replace("{{", "{").replace("}}", "}")
    return (
        template
        .replace("__FIELDS__", json.dumps(FIELDS))
        .replace("__SEED__", json.dumps(seed_csv))
        .replace("__SPECIAL_DATA__", json.dumps(json.dumps(build_special_data(), separators=(",", ":"))))
    )


def main():
    rows = to_dicts()
    seed = csv_text(rows)
    (ROOT / CSV_NAME).write_text(seed, encoding="utf-8-sig")
    (ROOT / HTML_NAME).write_text(build_html(seed), encoding="utf-8")
    print(f"Wrote {CSV_NAME}")
    print(f"Wrote {HTML_NAME}")
    print(f"Slides: {len(rows)}")


if __name__ == "__main__":
    main()

