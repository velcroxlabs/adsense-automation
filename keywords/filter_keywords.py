#!/usr/bin/env python3
"""
Filter researched keywords into a final batch ready for content generation.

Input:
- keywords/research_candidates.csv

Output:
- keywords/final_batch.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "keyword",
    "niche",
    "search_volume",
    "kd",
    "cpc",
    "competition",
    "intent",
]


def main() -> None:
    keywords_dir = Path(__file__).resolve().parent
    input_path = keywords_dir / "research_candidates.csv"
    output_path = keywords_dir / "final_batch.csv"

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        print("Run keywords/research.py first.")
        return

    df = pd.read_csv(input_path)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        print(f"Missing required columns: {', '.join(missing_columns)}")
        return

    filtered = df[(df["kd"] <= 18) & (df["search_volume"] >= 1000)].copy()
    filtered = filtered.sort_values(
        ["search_volume", "kd", "cpc"],
        ascending=[False, True, False],
    )

    final_batch = filtered[REQUIRED_COLUMNS].reset_index(drop=True)

    print(f"Total researched keywords: {len(df)}")
    print(f"Filtered keywords: {len(final_batch)}")

    if final_batch.empty:
        print("No keywords passed the filters.")
        return

    print("\nTop filtered keywords:")
    print(final_batch.head(20).to_string(index=False))

    final_batch.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
