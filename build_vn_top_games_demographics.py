from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
import psycopg2


PROJECT_DIR = Path(r"C:\Users\VEE0634\Desktop\Slide Making\Examining VN Gaming Market Opportunity 2026")
REPO_DIR = Path(r"C:\Users\VEE0634\Desktop\Coding\vn_strategy_data_system")
REPO_ENV_PATH = REPO_DIR / ".env"
REPO_LIB_DIR = REPO_DIR / "lib"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "demographics_analysis"


TOP_GAMES_SQL = """
with game_revenue as (
    select
        dai.unified_app_id,
        coalesce(dgi.name, max(dai.name)) as game_name,
        (
          sum(
            coalesce(f.revenue_android, 0)
          + coalesce(f.revenue_iphone, 0)
          + coalesce(f.revenue_ipad, 0)
          ) / 100.0
        )::numeric(18,2) as revenue_2025
    from core.fact_app_performance_daily f
    join core.dim_app_info dai
      on dai.app_id = f.app_id
    left join core.dim_game_info dgi
      on dgi.unified_app_id = dai.unified_app_id
    where f.date >= %(start_date)s
      and f.date < %(end_date)s
      and (
            %(country)s is null
         or f.country_android = %(country)s
         or f.country_ios = %(country)s
      )
    group by dai.unified_app_id, dgi.name
)
select
    unified_app_id,
    game_name,
    revenue_2025
from game_revenue
where unified_app_id is not null
order by revenue_2025 desc, unified_app_id
limit %(top_n)s
"""


APP_REVENUE_SQL = """
with top_games as (
    """ + TOP_GAMES_SQL + """
)
select
    tg.unified_app_id,
    tg.game_name,
    dai.app_id,
    dai.os,
    dai.name as app_name,
    dai.publisher_name,
    tg.revenue_2025 as game_revenue_2025,
    (
      sum(
        coalesce(f.revenue_android, 0)
      + coalesce(f.revenue_iphone, 0)
      + coalesce(f.revenue_ipad, 0)
      ) / 100.0
    )::numeric(18,2) as app_revenue_2025
from top_games tg
join core.dim_app_info dai
  on dai.unified_app_id = tg.unified_app_id
join core.fact_app_performance_daily f
  on f.app_id = dai.app_id
where f.date >= %(start_date)s
  and f.date < %(end_date)s
  and (
        %(country)s is null
     or f.country_android = %(country)s
     or f.country_ios = %(country)s
  )
group by
    tg.unified_app_id,
    tg.game_name,
    dai.app_id,
    dai.os,
    dai.name,
    dai.publisher_name,
    tg.revenue_2025
order by tg.revenue_2025 desc, app_revenue_2025 desc, dai.app_id
"""


DEMO_COLUMNS = [
    "average_age_total",
    "female",
    "male",
    "normalized_demographics_female_18",
    "normalized_demographics_female_25",
    "normalized_demographics_female_35",
    "normalized_demographics_female_45",
    "normalized_demographics_female_55",
    "normalized_demographics_male_18",
    "normalized_demographics_male_25",
    "normalized_demographics_male_35",
    "normalized_demographics_male_45",
    "normalized_demographics_male_55",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Vietnam top-games demographics extracts.")
    parser.add_argument("--top-n", type=int, default=50, help="How many top games to include.")
    parser.add_argument("--year", type=int, default=2025, help="Revenue year for ranking.")
    parser.add_argument("--country", default="VN", help="Country code filter for the warehouse revenue query.")
    parser.add_argument(
        "--demographics-country",
        default="SE_ASIA",
        help="Sensor Tower supported geography for demographics, such as SE_ASIA.",
    )
    parser.add_argument(
        "--outdir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for CSV and JSON files.",
    )
    parser.add_argument(
        "--skip-demographics",
        action="store_true",
        help="Only export the top-games revenue extracts.",
    )
    parser.add_argument(
        "--weight-country",
        default="VN",
        help="Country code used for active-user weighting, typically VN.",
    )
    return parser.parse_args()


def read_env_value(path: Path, key: str) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        env_key, env_value = line.split("=", 1)
        if env_key.strip() == key:
            return env_value.strip()
    raise KeyError(f"Missing {key} in {path}")


def run_query(sql: str, params: dict) -> pd.DataFrame:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        dbname="mydb",
        user="postgres",
        password="postgres",
    )
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def import_repo_library():
    sys.path.append(str(REPO_LIB_DIR))
    import library_st_data_processing as lsdp  # type: ignore

    return lsdp


def fetch_demographics_for_os(
    lsdp,
    *,
    api_key: str,
    base_url: str,
    os_name: str,
    app_ids: Iterable[str],
    country_code: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    unique_app_ids = [str(app_id) for app_id in dict.fromkeys(app_ids) if str(app_id).strip()]
    if not unique_app_ids:
        return pd.DataFrame()

    rows = lsdp.get_apps_demographics_all_time(
        api_key=api_key,
        base_url=base_url,
        os_name=os_name,
        app_ids=unique_app_ids,
        country_code=country_code,
        start_date=start_date,
        end_date=end_date,
        date_granularity="all_time",
        app_chunk_size=500,
        timeout=60.0,
        show_progress=True,
    )
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["app_id"] = df["app_id"].astype(str)
    df["os"] = os_name
    return df


def fetch_active_users(
    lsdp,
    *,
    api_key: str,
    base_url: str,
    app_revenue: pd.DataFrame,
    country_code: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    if app_revenue.empty:
        return pd.DataFrame()

    source_df = app_revenue[["app_id", "os"]].drop_duplicates().copy()
    rows = lsdp.get_apps_active_users(
        api_key=api_key,
        base_url=base_url,
        ios_app_ids=source_df.loc[source_df["os"].str.lower() == "ios", "app_id"].astype(str).tolist(),
        android_app_ids=source_df.loc[source_df["os"].str.lower() == "android", "app_id"].astype(str).tolist(),
        country_codes=country_code,
        start_date=start_date,
        end_date=end_date,
        max_periods=1000,
        data_model="DM_2025_Q2",
        app_chunk_size=500,
        request_timeout=60,
        show_progress=True,
    )
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["app_id"] = df["app_id"].astype(str)
    return df


def summarize_active_users(active_users: pd.DataFrame) -> pd.DataFrame:
    if active_users.empty:
        return pd.DataFrame(columns=["app_id", "avg_dau_2025", "days_with_dau"])

    work = active_users.copy()
    for column in ["dau_android", "dau_iphone", "dau_ipad"]:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    work["daily_total_dau"] = (
        work["dau_android"].fillna(0)
        + work["dau_iphone"].fillna(0)
        + work["dau_ipad"].fillna(0)
    )
    work["has_any_dau"] = work[["dau_android", "dau_iphone", "dau_ipad"]].notna().any(axis=1)

    summary = (
        work.loc[work["has_any_dau"]]
        .groupby("app_id", dropna=False)
        .agg(
            avg_dau_2025=("daily_total_dau", "mean"),
            days_with_dau=("daily_total_dau", "size"),
        )
        .reset_index()
    )
    return summary


def aggregate_weighted(df: pd.DataFrame, group_cols: list[str], weight_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=group_cols + ["weight_sum", "app_count", "confidence_mean"] + DEMO_COLUMNS)

    work = df.copy()
    work["weight_value"] = pd.to_numeric(work[weight_col], errors="coerce").fillna(0.0)
    work["fallback_weight"] = 1.0

    for column in DEMO_COLUMNS:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    def _summarize(group: pd.DataFrame) -> pd.Series:
        weights = group["weight_value"].fillna(0.0)
        if weights.sum() <= 0:
            weights = group["fallback_weight"]

        summary: dict[str, float | int] = {
            "weight_sum": float(weights.sum()),
            "app_count": int(group["app_id"].nunique()),
            "confidence_mean": float(pd.to_numeric(group["confidence"], errors="coerce").mean()),
        }

        for column in DEMO_COLUMNS:
            valid = group[column].notna()
            if valid.any():
                summary[column] = float((group.loc[valid, column] * weights.loc[valid]).sum() / weights.loc[valid].sum())
            else:
                summary[column] = float("nan")

        return pd.Series(summary)

    return work.groupby(group_cols, dropna=False).apply(_summarize).reset_index()


def add_combined_age_buckets(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["age_bucket_18_combined"] = out["normalized_demographics_female_18"] + out["normalized_demographics_male_18"]
    out["age_bucket_25_combined"] = out["normalized_demographics_female_25"] + out["normalized_demographics_male_25"]
    out["age_bucket_35_combined"] = out["normalized_demographics_female_35"] + out["normalized_demographics_male_35"]
    out["age_bucket_45_combined"] = out["normalized_demographics_female_45"] + out["normalized_demographics_male_45"]
    out["age_bucket_55_combined"] = out["normalized_demographics_female_55"] + out["normalized_demographics_male_55"]
    return out


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    start_date = f"{args.year}-01-01"
    end_date = f"{args.year + 1}-01-01"

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "country": args.country,
        "top_n": args.top_n,
    }

    top_games = run_query(TOP_GAMES_SQL, params)
    top_games.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}.csv", index=False)

    app_revenue = run_query(APP_REVENUE_SQL, params)
    app_revenue["app_id"] = app_revenue["app_id"].astype(str)
    app_revenue.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_apps.csv", index=False)

    summary = {
        "country": args.country,
        "year": args.year,
        "top_n": args.top_n,
        "demographics_country": args.demographics_country,
        "weight_country": args.weight_country,
        "top_games_count": int(len(top_games)),
        "top_apps_count": int(app_revenue["app_id"].nunique()),
        "total_revenue_top_games": float(top_games["revenue_2025"].sum()) if not top_games.empty else 0.0,
        "outputs": {
            "top_games_csv": str(outdir / f"vn_top_games_{args.year}_top_{args.top_n}.csv"),
            "top_apps_csv": str(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_apps.csv"),
        },
    }

    if args.skip_demographics:
        (outdir / f"vn_top_games_{args.year}_top_{args.top_n}_summary.json").write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(summary, indent=2))
        return

    api_key = read_env_value(REPO_ENV_PATH, "ST_API_KEY")
    lsdp = import_repo_library()

    active_users_raw = fetch_active_users(
        lsdp,
        api_key=api_key,
        base_url="https://api.sensortower.com",
        app_revenue=app_revenue,
        country_code=args.weight_country,
        start_date=start_date,
        end_date=end_date,
    )
    active_users_raw.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_active_users_raw.csv", index=False)
    active_users_summary = summarize_active_users(active_users_raw)
    active_users_summary.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_avg_dau.csv", index=False)

    os_series = app_revenue["os"].fillna("").str.lower()
    ios_ids = app_revenue.loc[os_series == "ios", "app_id"].tolist()
    android_ids = app_revenue.loc[os_series == "android", "app_id"].tolist()

    ios_demo = fetch_demographics_for_os(
        lsdp,
        api_key=api_key,
        base_url="https://api.sensortower.com",
        os_name="ios",
        app_ids=ios_ids,
        country_code=args.demographics_country,
        start_date=start_date,
        end_date=end_date,
    )
    android_demo = fetch_demographics_for_os(
        lsdp,
        api_key=api_key,
        base_url="https://api.sensortower.com",
        os_name="android",
        app_ids=android_ids,
        country_code=args.demographics_country,
        start_date=start_date,
        end_date=end_date,
    )

    demographics_raw = pd.concat([ios_demo, android_demo], ignore_index=True)
    if not demographics_raw.empty:
        demographics_raw["app_id"] = demographics_raw["app_id"].astype(str)

    merged = app_revenue.merge(demographics_raw, on=["app_id", "os"], how="left")
    merged = merged.merge(active_users_summary, on="app_id", how="left")
    merged.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_apps_with_demographics.csv", index=False)

    game_level = aggregate_weighted(merged, ["unified_app_id", "game_name"], "avg_dau_2025")
    game_level = add_combined_age_buckets(game_level)
    game_level = game_level.merge(
        top_games[["unified_app_id", "game_name", "revenue_2025"]],
        on=["unified_app_id", "game_name"],
        how="left",
    )
    game_level = game_level.sort_values(["revenue_2025", "game_name"], ascending=[False, True])
    game_level.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_game_demographics_weighted.csv", index=False)

    merged_for_portfolio = merged.copy()
    merged_for_portfolio["portfolio_scope"] = f"Top {args.top_n} VN games {args.year}"
    portfolio = aggregate_weighted(merged_for_portfolio, ["portfolio_scope"], "avg_dau_2025")
    if portfolio.empty:
        portfolio = pd.DataFrame([{"portfolio_scope": f"Top {args.top_n} VN games {args.year}"}])
    else:
        portfolio = add_combined_age_buckets(portfolio)
    portfolio.to_csv(outdir / f"vn_top_games_{args.year}_top_{args.top_n}_portfolio_demographics_weighted.csv", index=False)

    summary["demographics_rows"] = int(len(demographics_raw))
    summary["apps_with_demographics"] = int(merged["female"].notna().sum()) if "female" in merged.columns else 0
    summary["active_users_rows"] = int(len(active_users_raw))
    summary["apps_with_avg_dau"] = int(active_users_summary["app_id"].nunique())
    summary["outputs"]["apps_with_demographics_csv"] = str(
        outdir / f"vn_top_games_{args.year}_top_{args.top_n}_apps_with_demographics.csv"
    )
    summary["outputs"]["game_demographics_csv"] = str(
        outdir / f"vn_top_games_{args.year}_top_{args.top_n}_game_demographics_weighted.csv"
    )
    summary["outputs"]["portfolio_demographics_csv"] = str(
        outdir / f"vn_top_games_{args.year}_top_{args.top_n}_portfolio_demographics_weighted.csv"
    )
    summary["outputs"]["active_users_raw_csv"] = str(
        outdir / f"vn_top_games_{args.year}_top_{args.top_n}_active_users_raw.csv"
    )
    summary["outputs"]["avg_dau_csv"] = str(
        outdir / f"vn_top_games_{args.year}_top_{args.top_n}_avg_dau.csv"
    )

    (outdir / f"vn_top_games_{args.year}_top_{args.top_n}_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
