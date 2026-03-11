#!/usr/bin/env python3
"""
Keyword research script using Google Trends plus deterministic SEO heuristics.

Outputs:
- keywords/research_candidates.csv : enriched keyword candidates
- keywords/filtered_keywords.csv   : backward-compatible filtered export
"""

from __future__ import annotations

import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pytrends.request import TrendReq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.env_utils import load_project_env


load_project_env()


pytrends = TrendReq(hl="en-US", tz=360)


QUESTION_TERMS = {
    "how",
    "what",
    "why",
    "when",
    "where",
    "can",
    "should",
    "guide",
    "tips",
    "ways",
    "ideas",
    "examples",
    "tutorial",
    "beginner",
    "beginners",
}

COMMERCIAL_TERMS = {
    "best",
    "review",
    "reviews",
    "top",
    "vs",
    "versus",
    "compare",
    "comparison",
    "alternatives",
    "software",
    "app",
    "apps",
    "tool",
    "tools",
}

TRANSACTIONAL_TERMS = {
    "buy",
    "price",
    "pricing",
    "cost",
    "cheap",
    "coupon",
    "discount",
    "deal",
    "quote",
    "service",
    "calculator",
    "estimate",
    "near",
}

LOWER_DIFFICULTY_TERMS = {
    "for beginners",
    "step by step",
    "checklist",
    "template",
    "example",
    "examples",
}

SEO_DIFFICULTY_BASELINE = {
    "personal finance": 10,
    "technology": 9,
    "software": 9,
    "health & wellness": 8,
    "fitness": 7,
    "home improvement": 6,
    "gardening": 4,
    "cooking": 4,
    "travel": 6,
    "education": 5,
}

CPC_FALLBACK_BY_NICHE = {
    "personal finance": 4.8,
    "technology": 3.4,
    "software": 4.2,
    "health & wellness": 2.1,
    "fitness": 1.8,
    "home improvement": 2.9,
    "gardening": 1.2,
    "cooking": 1.1,
    "travel": 2.0,
    "education": 1.6,
}

GOOGLE_ADS_REQUIRED_ENV_VARS = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_CUSTOMER_ID",
]

PYTRENDS_MAX_RETRIES = 4
PYTRENDS_BASE_DELAY_SECONDS = 4
PYTRENDS_MAX_RESULTS_PER_SEED = 15
PYTRENDS_INTER_REQUEST_DELAY_SECONDS = 2.5


def parse_trend_value(value: Any) -> int:
    if isinstance(value, (int, float)):
        return max(0, min(100, int(value)))

    text = str(value).strip().lower()
    if text == "breakout":
        return 100

    try:
        return max(0, min(100, int(float(text))))
    except ValueError:
        return 0


def normalize_niche(seed: str) -> str:
    normalized = seed.strip().lower()

    if normalized in {"health", "wellness", "health & wellness"}:
        return "health & wellness"

    return normalized


def infer_intent(keyword: str) -> str:
    normalized = keyword.lower()
    tokens = set(normalized.split())

    if any(term in normalized for term in TRANSACTIONAL_TERMS):
        return "transactional"

    if tokens.intersection(COMMERCIAL_TERMS):
        return "commercial"

    return "informational"


def estimate_search_volume(trend_value: int) -> int:
    """
    Deterministic search-volume proxy from Google Trends values.
    Non-linear so high-trend terms separate more clearly.
    """
    if trend_value <= 0:
        return 0

    return int(round((trend_value ** 1.35) * 120))


def estimate_keyword_difficulty(keyword: str, niche: str, trend_value: int, source_type: str) -> float:
    """
    Deterministic heuristic difficulty score (0-100).
    This is still an estimate, but no longer random.
    """
    normalized = keyword.lower().strip()
    tokens = [token for token in normalized.replace("-", " ").split() if token]
    word_count = len(tokens)
    intent = infer_intent(normalized)

    score = 8.0
    score += SEO_DIFFICULTY_BASELINE.get(niche, 6)

    if word_count <= 2:
        score += 18
    elif word_count == 3:
        score += 10
    elif word_count == 4:
        score += 5
    elif word_count >= 6:
        score -= 6
    else:
        score -= 2

    if intent == "commercial":
        score += 8
    elif intent == "transactional":
        score += 10
    else:
        score -= 4

    if any(term in normalized for term in LOWER_DIFFICULTY_TERMS):
        score -= 6

    if "near me" in normalized:
        score -= 8

    if any(char.isdigit() for char in normalized):
        score -= 2

    if source_type == "top":
        score += 3
    elif source_type == "rising":
        score -= 1

    if trend_value >= 85:
        score += 10
    elif trend_value >= 70:
        score += 7
    elif trend_value >= 50:
        score += 4
    elif trend_value >= 30:
        score += 1
    else:
        score -= 2

    return round(max(1.0, min(65.0, score)), 1)


def estimate_cpc(keyword: str, niche: str, intent: str, search_volume: int) -> float:
    base_cpc = CPC_FALLBACK_BY_NICHE.get(niche, 1.5)
    normalized = keyword.lower()

    if intent == "commercial":
        base_cpc *= 1.35
    elif intent == "transactional":
        base_cpc *= 1.5
    else:
        base_cpc *= 0.75

    if "insurance" in normalized or "mortgage" in normalized or "loan" in normalized:
        base_cpc *= 1.8
    elif "calculator" in normalized or "software" in normalized:
        base_cpc *= 1.3

    volume_factor = min(1.35, max(0.85, 0.85 + math.log10(max(search_volume, 100)) / 10))
    return round(base_cpc * volume_factor, 2)


def google_ads_available() -> bool:
    return all(os.getenv(name) for name in GOOGLE_ADS_REQUIRED_ENV_VARS)


def micros_to_currency(micros: Any) -> float:
    try:
        return round(float(micros) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def competition_label_from_index(value: Optional[int]) -> str:
    if value is None:
        return "unknown"
    if value < 34:
        return "low"
    if value < 67:
        return "medium"
    return "high"


def build_google_ads_client():
    from google.ads.googleads.client import GoogleAdsClient

    config: Dict[str, Any] = {
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "use_proto_plus": True,
    }

    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    if login_customer_id:
        config["login_customer_id"] = login_customer_id.replace("-", "")

    return GoogleAdsClient.load_from_dict(config)


def fetch_google_ads_metrics(keywords: List[str]) -> Dict[str, Dict[str, Any]]:
    if not google_ads_available():
        return {}

    try:
        client = build_google_ads_client()
        service = client.get_service("KeywordPlanIdeaService")
        request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
        request.customer_id = os.environ["GOOGLE_ADS_CUSTOMER_ID"].replace("-", "")
        request.keywords.extend(keywords)

        language_id = os.getenv("GOOGLE_ADS_LANGUAGE_ID", "").strip()
        if language_id:
            request.language = f"languageConstants/{language_id}"

        geo_target_ids = [
            geo_id.strip()
            for geo_id in os.getenv("GOOGLE_ADS_GEO_TARGET_IDS", "").split(",")
            if geo_id.strip()
        ]
        if geo_target_ids:
            request.geo_target_constants.extend(
                [f"geoTargetConstants/{geo_id}" for geo_id in geo_target_ids]
            )

        network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        request.keyword_plan_network = network

        response = service.generate_keyword_historical_metrics(request=request)
    except ImportError:
        print("google-ads is not installed. Falling back to heuristic keyword metrics.")
        return {}
    except Exception as exc:
        print(f"Google Ads historical metrics unavailable, using fallback estimates: {exc}")
        return {}

    metrics_by_keyword: Dict[str, Dict[str, Any]] = {}

    for result in response.results:
        text = str(result.text).strip()
        metrics = result.keyword_metrics
        competition_index = getattr(metrics, "competition_index", None)

        monthly_searches = 0
        volumes = list(getattr(metrics, "monthly_search_volumes", []) or [])
        if volumes:
            monthly_searches = max(int(getattr(entry, "monthly_searches", 0) or 0) for entry in volumes)
        else:
            monthly_searches = int(getattr(metrics, "avg_monthly_searches", 0) or 0)

        metrics_by_keyword[text.lower()] = {
            "search_volume": monthly_searches,
            "competition": competition_label_from_index(competition_index),
            "competition_index": int(competition_index) if competition_index is not None else None,
            "low_top_of_page_bid": micros_to_currency(getattr(metrics, "low_top_of_page_bid_micros", 0)),
            "high_top_of_page_bid": micros_to_currency(getattr(metrics, "high_top_of_page_bid_micros", 0)),
            "avg_cpc": micros_to_currency(
                (
                    (getattr(metrics, "low_top_of_page_bid_micros", 0) or 0)
                    + (getattr(metrics, "high_top_of_page_bid_micros", 0) or 0)
                )
                / 2
            ),
            "metrics_source": "google_ads",
        }

    return metrics_by_keyword


def competition_from_kd(kd: float) -> str:
    if kd <= 18:
        return "low"
    if kd <= 35:
        return "medium"
    return "high"


def fetch_related_queries_for_seed(seed: str, max_results_per_seed: int) -> List[pd.DataFrame]:
    for attempt in range(1, PYTRENDS_MAX_RETRIES + 1):
        try:
            pytrends.build_payload([seed], timeframe="today 12-m")
            related = pytrends.related_queries()
            seed_related = related.get(seed) or {}
            result_frames: List[pd.DataFrame] = []

            if seed_related.get("top") is not None:
                top_df = seed_related["top"].copy().head(max_results_per_seed)
                top_df["seed"] = seed
                top_df["type"] = "top"
                result_frames.append(top_df)

            if seed_related.get("rising") is not None:
                rising_df = seed_related["rising"].copy().head(max_results_per_seed)
                rising_df["seed"] = seed
                rising_df["type"] = "rising"
                result_frames.append(rising_df)

            return result_frames
        except Exception as exc:
            message = str(exc)
            is_rate_limit = "429" in message or "Too Many Requests" in message

            if attempt >= PYTRENDS_MAX_RETRIES or not is_rate_limit:
                print(f"Error fetching keywords for '{seed}': {exc}")
                return []

            delay = (PYTRENDS_BASE_DELAY_SECONDS * (2 ** (attempt - 1))) + random.uniform(0.5, 1.5)
            print(
                f"Rate limited for '{seed}' on attempt {attempt}/{PYTRENDS_MAX_RETRIES}. "
                f"Retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

    return []


def get_related_keywords(seed_keywords: List[str], max_results_per_seed: int = 50) -> pd.DataFrame:
    """
    Get related keywords from Google Trends.
    Returns DataFrame with columns: keyword, trend_value, seed, type
    """
    all_keywords: List[pd.DataFrame] = []

    for seed in seed_keywords:
        seed_frames = fetch_related_queries_for_seed(seed, max_results_per_seed)
        all_keywords.extend(seed_frames)
        time.sleep(PYTRENDS_INTER_REQUEST_DELAY_SECONDS)

    if not all_keywords:
        return pd.DataFrame(columns=["keyword", "trend_value", "seed", "type"])

    df = pd.concat(all_keywords, ignore_index=True)
    df.columns = ["keyword", "trend_value", "seed", "type"]
    return df.drop_duplicates(subset=["keyword", "seed", "type"]).reset_index(drop=True)


def enrich_keywords(df: pd.DataFrame) -> pd.DataFrame:
    enriched_rows: List[Dict[str, Any]] = []
    google_ads_metrics = fetch_google_ads_metrics(
        [str(row["keyword"]).strip() for _, row in df.iterrows() if str(row["keyword"]).strip()]
    )

    for _, row in df.iterrows():
        keyword = str(row["keyword"]).strip()
        seed = str(row["seed"]).strip()
        source_type = str(row["type"]).strip().lower()
        niche = normalize_niche(seed)
        trend_value = parse_trend_value(row["trend_value"])
        intent = infer_intent(keyword)
        kd = estimate_keyword_difficulty(keyword, niche, trend_value, source_type)
        ads_metrics = google_ads_metrics.get(keyword.lower(), {})
        search_volume = int(ads_metrics.get("search_volume") or estimate_search_volume(trend_value))
        cpc = float(ads_metrics.get("avg_cpc") or estimate_cpc(keyword, niche, intent, search_volume))
        competition = str(ads_metrics.get("competition") or competition_from_kd(kd))
        competition_index = ads_metrics.get("competition_index")
        low_top_of_page_bid = float(ads_metrics.get("low_top_of_page_bid") or 0)
        high_top_of_page_bid = float(ads_metrics.get("high_top_of_page_bid") or 0)

        enriched_rows.append(
          {
              "keyword": keyword,
              "niche": niche,
              "search_volume": search_volume,
              "seo_difficulty_estimate": kd,
              "kd": kd,
              "cpc": cpc,
              "competition": competition,
              "competition_index": competition_index,
              "low_top_of_page_bid": low_top_of_page_bid,
              "high_top_of_page_bid": high_top_of_page_bid,
              "intent": intent,
              "trend_value": trend_value,
              "metrics_source": ads_metrics.get("metrics_source", "heuristic"),
              "seed": seed,
              "type": source_type,
          }
        )

    return pd.DataFrame(enriched_rows).drop_duplicates(subset=["keyword"]).reset_index(drop=True)


def filter_keywords(df: pd.DataFrame, max_kd: float = 18, min_volume: int = 1000) -> pd.DataFrame:
    return (
        df[(df["kd"] <= max_kd) & (df["search_volume"] >= min_volume)]
        .sort_values(["search_volume", "kd"], ascending=[False, True])
        .reset_index(drop=True)
    )


def main() -> None:
    seed_niches = [
        "health",
        "personal finance",
        "technology",
        "home improvement",
        "gardening",
        "cooking",
        "fitness",
        "travel",
        "education",
        "software",
    ]

    print("Starting keyword research...")
    print(f"Seed niches: {', '.join(seed_niches)}")
    if google_ads_available():
        print("Google Ads keyword metrics: enabled")
    else:
        print("Google Ads keyword metrics: unavailable, using heuristic volume/CPC fallback")

    keywords_df = get_related_keywords(seed_niches, max_results_per_seed=PYTRENDS_MAX_RESULTS_PER_SEED)
    if keywords_df.empty:
        print("No keywords found. Check internet connection or try different seeds.")
        return

    enriched_df = enrich_keywords(keywords_df)
    filtered_df = filter_keywords(enriched_df)

    output_dir = Path(__file__).resolve().parent
    candidates_path = output_dir / "research_candidates.csv"
    filtered_path = output_dir / "filtered_keywords.csv"

    enriched_df.to_csv(candidates_path, index=False)
    filtered_df.to_csv(filtered_path, index=False)

    print(f"Found {len(enriched_df)} enriched keyword candidates.")
    print(f"Filtered to {len(filtered_df)} keywords with KD <= 18 and volume >= 1000.")
    print(f"Candidates saved to {candidates_path}")
    print(f"Filtered results saved to {filtered_path}")

    if not filtered_df.empty:
        print("\nTop 20 keywords:")
        print(
            filtered_df[
                ["keyword", "niche", "search_volume", "kd", "cpc", "intent"]
            ]
            .head(20)
            .to_string(index=False)
        )

        print("\nKeywords per niche:")
        niche_counts = filtered_df.groupby("niche").size().sort_values(ascending=False)
        print(niche_counts.to_string())


if __name__ == "__main__":
    main()
