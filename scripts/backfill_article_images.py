#!/usr/bin/env python3
"""
Backfill article images for existing rows in Supabase.

Assigns a deterministic featured image per article based on niche + slug and
mirrors it into metadata.image for compatibility.
"""

import os
import sys
import json
from typing import Any, Dict
from urllib import parse, request

from article_images import assign_images_for_keys
from env_utils import load_project_env

load_project_env()


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def derive_niche(article: Dict[str, Any]) -> str:
    metadata = article.get("metadata") or {}
    niche = metadata.get("niche")
    if isinstance(niche, str) and niche.strip():
        return niche.strip()
    return "personal finance"


def main() -> None:
    try:
        from supabase import create_client, Client
    except ImportError:
        create_client = None

    url = get_env("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if create_client:
        supabase: "Client" = create_client(url, anon_key)
        response = (
            supabase.table("articles")
            .select("id, slug, featured_image, metadata")
            .order("created_at", desc=False)
            .execute()
        )
        rows = response.data or []
        updater = lambda article_id, payload: (
            supabase.table("articles").update(payload).eq("id", article_id).execute()
        )
    else:
        if not service_role_key:
            raise RuntimeError(
                "supabase-client is not installed and SUPABASE_SERVICE_ROLE_KEY is missing."
            )

        rows = fetch_articles_via_rest(url, service_role_key)
        updater = lambda article_id, payload: update_article_via_rest(
            url, service_role_key, article_id, payload
        )

    if not rows:
        print("No articles found.")
        return

    rows_by_niche: Dict[str, list[Dict[str, Any]]] = {}
    for row in rows:
        rows_by_niche.setdefault(derive_niche(row), []).append(row)

    updated = 0

    for niche, niche_rows in rows_by_niche.items():
        image_map = assign_images_for_keys(
            niche,
            [(row.get("slug") or row.get("id")) for row in niche_rows],
        )

        for row in niche_rows:
            metadata = row.get("metadata") or {}
            slug = row.get("slug") or row.get("id")
            image = image_map[slug]

            next_metadata = dict(metadata)
            next_metadata["image"] = image

            updater(
                row["id"],
                {
                    "featured_image": image,
                    "metadata": next_metadata,
                },
            )

            updated += 1
            print(f"Updated {row['slug']} -> {image}")

    print(f"Done. Updated: {updated}.")


def fetch_articles_via_rest(url: str, service_role_key: str) -> list[Dict[str, Any]]:
    query = parse.urlencode(
        {
            "select": "id,slug,featured_image,metadata",
            "order": "created_at.asc",
        }
    )
    req = request.Request(
        f"{url}/rest/v1/articles?{query}",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
        },
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def update_article_via_rest(
    url: str,
    service_role_key: str,
    article_id: str,
    payload: Dict[str, Any],
) -> None:
    req = request.Request(
        f"{url}/rest/v1/articles?id=eq.{parse.quote(article_id, safe='')}",
        data=json.dumps(payload).encode("utf-8"),
        method="PATCH",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    with request.urlopen(req):
        return


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
