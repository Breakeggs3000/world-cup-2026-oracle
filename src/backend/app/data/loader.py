"""Data loading and team name normalization."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
CACHE_DIR = DATA_DIR / "cache"
RESULTS_CSV = CACHE_DIR / "results.csv"
ALIASES_PATH = DATA_DIR / "team_aliases.json"
CONFED_PATH = DATA_DIR / "confederations.json"
WC2026_PATH = DATA_DIR / "wc2026_fixtures.json"

WORLD_CUP_YEARS = list(range(1990, 2023, 4))


@lru_cache(maxsize=1)
def load_aliases() -> dict[str, str]:
    with ALIASES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_confederations() -> dict[str, str]:
    with CONFED_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_team(name: str | None) -> str:
    if not name or not str(name).strip():
        return ""
    cleaned = str(name).strip()
    return load_aliases().get(cleaned, cleaned)


def load_results(use_cache: bool = True) -> pd.DataFrame:
    if not RESULTS_CSV.exists():
        raise FileNotFoundError(
            f"Results CSV not found at {RESULTS_CSV}. Run scripts/fetch_data.py first."
        )

    df = pd.read_csv(RESULTS_CSV)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])
    df["home_team"] = df["home_team"].map(normalize_team)
    df["away_team"] = df["away_team"].map(normalize_team)
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["tournament"] = df["tournament"].fillna("").astype(str)
    df["city"] = df.get("city", pd.Series([""] * len(df))).fillna("").astype(str)
    df["country"] = df.get("country", pd.Series([""] * len(df))).fillna("").astype(str)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def outcome_label(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "W"
    if home_score < away_score:
        return "L"
    return "D"


def is_world_cup_row(tournament: str) -> bool:
    t = tournament.lower()
    return "fifa world cup" in t


def is_knockout_stage(tournament: str, city: str = "") -> bool:
    text = f"{tournament} {city}".lower()
    keywords = (
        "round of 16",
        "quarter",
        "semi",
        "final",
        "knockout",
        "round of 32",
        "3rd place",
        "third place",
    )
    return any(k in text for k in keywords)


def world_cup_year(tournament: str, match_date: pd.Timestamp) -> int | None:
    if not is_world_cup_row(tournament):
        return None
    year = int(match_date.year)
    if year in WORLD_CUP_YEARS:
        return year
    return None


def get_world_cup_matches(df: pd.DataFrame | None = None, year: int | None = None) -> pd.DataFrame:
    data = load_results() if df is None else df
    wc = data[data["tournament"].map(is_world_cup_row)].copy()
    wc["wc_year"] = wc.apply(lambda r: world_cup_year(r["tournament"], r["date"]), axis=1)
    wc = wc.dropna(subset=["wc_year"])
    wc["wc_year"] = wc["wc_year"].astype(int)
    if year is not None:
        wc = wc[wc["wc_year"] == year]
    return wc.reset_index(drop=True)


def list_world_cup_years() -> list[int]:
    wc = get_world_cup_matches()
    years = sorted(wc["wc_year"].unique().tolist())
    return [y for y in years if y >= 1990]


def load_wc2026_fixtures() -> list[dict[str, Any]]:
    with WC2026_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    fixtures = data["fixtures"] if isinstance(data, dict) and "fixtures" in data else data
    for fx in fixtures:
        fx["home_team"] = normalize_team(fx.get("home_team"))
        fx["away_team"] = normalize_team(fx.get("away_team"))
        stage = str(fx.get("stage", "Group"))
        fx["stage"] = "Group" if stage.lower() == "group" else stage
        if "status" not in fx:
            if fx.get("home_score") is not None:
                fx["status"] = "played"
            else:
                fx["status"] = "upcoming"
    return fixtures


def filter_wc2026_fixtures(status: str = "all") -> list[dict[str, Any]]:
    fixtures = load_wc2026_fixtures()
    if status == "all":
        return fixtures
    return [f for f in fixtures if f.get("status") == status]


def get_team_confederation(team: str) -> str | None:
    return load_confederations().get(normalize_team(team))
