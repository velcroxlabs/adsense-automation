#!/usr/bin/env python3
"""
Shared article image assignment helpers.

Uses curated per-niche pools and deterministic hashing so articles in the same
category do not all collapse to a single fallback image.
"""

from __future__ import annotations

import hashlib
from typing import Dict, Iterable, List


IMAGE_POOLS: Dict[str, List[str]] = {
    "personal-finance": [
        "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1554260570-e9689a3418b8?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1565514020179-026b92b84bb6?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?auto=format&fit=crop&q=80&w=1600",
    ],
    "home-improvement": [
        "https://images.unsplash.com/photo-1493666438817-866a91353ca9?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1502005097973-6a7082348e28?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&q=80&w=1600&crop=entropy",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1460317442991-0ec209397118?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1464890100898-a385f744067f?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1480074568708-e7b720bb3f09?auto=format&fit=crop&q=80&w=1600",
    ],
    "health-wellness": [
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1514996937319-344454492b37?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1494390248081-4e521a5940db?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&q=80&w=1600",
        "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&q=80&w=1600",
    ],
}


def niche_to_category_slug(niche: str) -> str:
    normalized = (niche or "").strip().lower()

    if "home" in normalized:
        return "home-improvement"
    if "health" in normalized or "wellness" in normalized:
        return "health-wellness"
    return "personal-finance"


def choose_featured_image(niche: str, unique_key: str) -> str:
    category_slug = niche_to_category_slug(niche)
    pool = IMAGE_POOLS[category_slug]
    digest = hashlib.sha256((unique_key or niche or category_slug).encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(pool)
    return pool[index]


def assign_images_for_keys(niche: str, keys: Iterable[str]) -> Dict[str, str]:
    category_slug = niche_to_category_slug(niche)
    pool = IMAGE_POOLS[category_slug]
    sorted_keys = sorted(set(keys))

    if len(sorted_keys) > len(pool):
        raise ValueError(
            f"Not enough curated images for {category_slug}: {len(sorted_keys)} keys, {len(pool)} images."
        )

    return {
        key: pool[index]
        for index, key in enumerate(sorted_keys)
    }
