#!/usr/bin/env python3
"""
Content generation script for AdSense Automation.
Generates article structures from keywords and saves to Supabase or Markdown files.
"""

import csv
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from article_images import choose_featured_image
from env_utils import load_project_env

load_project_env()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not installed. Install with: pip install openai")


DEFAULT_KEYWORD_SOURCES = [
    "keywords/final_batch.csv",
    "keywords/filtered_keywords.csv",
    "keywords/research_candidates.csv",
]


def first_present_value(row: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_keyword_row(row: Dict[str, Any]) -> Dict[str, Any]:
    keyword = str(first_present_value(row, "keyword", default="")).strip()
    niche = str(first_present_value(row, "niche", "seed", default="General")).strip() or "General"
    intent = str(first_present_value(row, "intent", default="informational")).strip().lower() or "informational"
    search_volume = to_int(first_present_value(row, "search_volume", "estimated_volume", default=0))
    kd = to_float(first_present_value(row, "kd", "estimated_kd", "keyword_difficulty", default=0))
    cpc = to_float(first_present_value(row, "cpc", default=0))
    competition = str(first_present_value(row, "competition", default="low")).strip().lower() or "low"

    return {
        "keyword": keyword,
        "niche": niche,
        "intent": intent,
        "search_volume": search_volume,
        "kd": kd,
        "cpc": cpc,
        "competition": competition,
    }


def load_keywords(csv_path: str) -> List[Dict[str, Any]]:
    """Load and normalize keywords from a CSV file."""
    keywords: List[Dict[str, Any]] = []

    try:
        with open(csv_path, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                normalized = normalize_keyword_row(row)
                if normalized["keyword"]:
                    keywords.append(normalized)

        print(f"Loaded {len(keywords)} keywords from {csv_path}")
        return keywords
    except FileNotFoundError:
        print(f"Keywords file not found: {csv_path}")
        return []
    except Exception as exc:
        print(f"Error loading keywords: {exc}")
        return []


def resolve_keywords_csv(project_root: Path) -> Optional[Path]:
    for relative_path in DEFAULT_KEYWORD_SOURCES:
        candidate = project_root / relative_path
        if candidate.exists():
            return candidate
    return None


def create_slug(keyword: str) -> str:
    """Convert keyword to URL-friendly slug."""
    slug = keyword.lower().strip()
    slug = slug.replace(" ", "-")
    slug = "".join(character for character in slug if character.isalnum() or character == "-")
    slug = "-".join(filter(None, slug.split("-")))
    return slug[:100]


def generate_content_with_openai(keyword: str, niche: str, intent: str) -> Optional[str]:
    """Generate high-end, premium article content using OpenAI API."""
    if not OPENAI_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  OPENAI_API_KEY not found in .env")
        return None

    try:
        client = OpenAI(api_key=api_key)

        # Style Guide for Premium UX
        style_guide = """
        - Always Start with a hooks to engage the audience in the article
        - NO fluff. NO 'In today's digital world' or 'It is important to note'.
        - Use "Sentence Case" for headings.
        - Use <blockquote> for key insights.
        - Use bolding for technical terms, never for whole sentences.
        - If a list has more than 4 items, use a structured table or sub-headings.
        """

        # Intent-specific logic
        if intent == "commercial":
            structure = f"""
            1. Quick Summary Table (Feature | Verdict | Rating)
            2. The 'Why This Matters' Hook (Short & Punchy)
            3. Detailed Analysis of '{keyword}'
            4. The Competition (Trade-offs)
            5. Final Recommendation
            """
        elif intent == "transactional":
            structure = f"""
            1. Instant Value Check (Is it worth the price?)
            2. Where to Buy & Best Deals
            3. Avoiding Common Scams/Overpricing
            4. Warranty & Long-term Value
            """
        else: # Informational
            structure = f"""
            1. Executive Summary (Key Takeaways)
            2. The Core Concept (Explained like a pro)
            3. Step-by-Step Implementation Framework
            4. Expert-level Pitfalls to Avoid
            """

        prompt = f"""
        Write a premium article for a '{niche}' website about '{keyword}'.
        
        Required Structure:
        {structure}

        Style Requirements:
        {style_guide}

        Tone: Authoritative, Minimalist, and Sophisticated. 
        Target: {1200 if intent == 'informational' else 1000} words.
        Format: Clean Markdown only.
        """

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior editorial director for a premium tech and lifestyle magazine. "
                        "You value brevity, data-driven insights, and clean information architecture. "
                        "You never use AI clichés or 'journey' metaphors."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7, # Lowered slightly for more consistent, professional output
            max_tokens=3500,
        )

        content = response.choices[0].message.content
        print(f"  Generated premium content ({len(content)} characters)")
        return content
    except Exception as exc:
        print(f"  OpenAI API error: {exc}")
        return None

def generate_article_structure(keyword_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate article structure from keyword data."""
    keyword = keyword_data.get("keyword", "")
    niche = keyword_data.get("niche", "General")
    intent = keyword_data.get("intent", "informational")

    if intent == "commercial":
        title = f"{keyword.title()} - Reviews and Buying Guide"
    elif intent == "transactional":
        title = f"{keyword.title()} - Compare Options and Prices"
    else:
        title = f"{keyword.title()} - Complete Guide"

    slug = create_slug(keyword)
    featured_image = choose_featured_image(niche, slug)

    ai_content = generate_content_with_openai(keyword, niche, intent)

    if ai_content:
        content = ai_content
        word_count = len(ai_content.split())
        requires_llm = False
        print(f"  AI-generated content ({word_count} words)")
    else:
        word_count = 800
        content = f"<!-- PLACEHOLDER CONTENT FOR: {keyword} -->\n\n"
        content += f"This article will be automatically generated about {keyword}. "
        content += "The final content will include detailed information, tips, and practical advice.\n\n"
        content += "**Expected sections:**\n"
        content += f"1. Introduction to {keyword}\n"
        content += "2. Key concepts and terminology\n"
        content += "3. Step-by-step guide\n"
        content += "4. Common mistakes to avoid\n"
        content += "5. Best practices and tips\n"
        content += "6. Frequently asked questions\n\n"
        content += "*Note: This is a placeholder. The final article will be generated by AI and will be unique, informative, and SEO-oriented.*"
        requires_llm = True
        print("  Using placeholder content (AI generation not available)")

    excerpt = f"Learn everything about {keyword}. This comprehensive guide covers the most important decisions, tradeoffs, and tactics."

    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": content,
        "featured_image": featured_image,
        "keyword_id": None,
        "status": "draft",
        "published_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "word_count": word_count,
            "reading_time": round(word_count / 200),
            "niche": niche,
            "seed_keyword": keyword,
            "search_volume": int(keyword_data.get("search_volume", 0)),
            "keyword_difficulty": float(keyword_data.get("kd", 0)),
            "cpc": float(keyword_data.get("cpc", 0)),
            "competition": keyword_data.get("competition", "low"),
            "intent": intent,
            "image": featured_image,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "requires_llm": requires_llm,
            "ai_generated": ai_content is not None,
        },
    }


def save_to_markdown(article: Dict[str, Any], output_dir: str) -> bool:
    """Save article as Markdown file."""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(output_dir, f"{article['slug']}.md")

        md_content = f"""---
title: \"{article['title']}\"
slug: \"{article['slug']}\"
excerpt: \"{article['excerpt']}\"
date: {datetime.now(timezone.utc).date().isoformat()}
niche: \"{article['metadata']['niche']}\"
status: \"{article['status']}\"
word_count: {article['metadata']['word_count']}
reading_time: {article['metadata']['reading_time']}
seed_keyword: \"{article['metadata']['seed_keyword']}\"
search_volume: {article['metadata']['search_volume']}
keyword_difficulty: {article['metadata']['keyword_difficulty']}
cpc: {article['metadata']['cpc']}
competition: \"{article['metadata']['competition']}\"
intent: \"{article['metadata']['intent']}\"
featured_image: \"{article['featured_image']}\"
---

{article['content']}
"""

        with open(filepath, "w", encoding="utf-8") as handle:
            handle.write(md_content)

        print(f"  Saved to: {filepath}")
        return True
    except Exception as exc:
        print(f"  Error saving Markdown: {exc}")
        return False


def save_to_supabase(article: Dict[str, Any]) -> bool:
    """Save article to Supabase database."""
    try:
        from supabase import Client, create_client

        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not anon_key:
            print("  Supabase credentials not found in .env")
            return False

        supabase: Client = create_client(url, anon_key)
        article_data = {key: value for key, value in article.items() if value is not None}
        response = supabase.table("articles").insert(article_data).execute()

        if hasattr(response, "data") and response.data:
            print(f"  Saved to Supabase (ID: {response.data[0]['id'][:8]}...)")
            return True

        print(f"  Supabase insert failed: {response}")
        return False
    except ImportError:
        print("  supabase-client not installed")
        return False
    except Exception as exc:
        print(f"  Supabase error: {exc}")
        return False


def main() -> None:
    """Main content generation routine."""
    print("=" * 60)
    print("Content Generation Script")
    print("=" * 60)

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    keywords_csv = resolve_keywords_csv(project_root)
    output_dir = "content/articles"

    if keywords_csv is None:
        print("No keyword CSV found.")
        print("Expected one of:")
        for relative_path in DEFAULT_KEYWORD_SOURCES:
            print(f"  - {relative_path}")
        print("Run keywords/research.py and keywords/filter_keywords.py first.")
        return

    keywords = load_keywords(str(keywords_csv))
    if not keywords:
        print("No keywords to process")
        return

    print("\nProcessing method:")
    print("1. Save to Supabase database (requires setup)")
    print("2. Save as Markdown files")
    print("3. Both")
    print("4. Preview only (no save)")

    if not sys.stdin.isatty():
        choice = "4"
        print(f"\n  Auto-selected option {choice} for non-interactive execution")
    else:
        try:
            choice = input("\nSelect option (1-4): ").strip()
        except EOFError:
            choice = "4"
            print(f"  Auto-selected option {choice} for non-interactive execution")

    print(f"\nProcessing {len(keywords)} keywords...")

    saved_count = 0
    for index, keyword_data in enumerate(keywords, 1):
        keyword = keyword_data.get("keyword", "Unknown")
        print(f"\n[{index}/{len(keywords)}] Generating: {keyword}")

        article = generate_article_structure(keyword_data)

        if choice == "1":
            if save_to_supabase(article):
                saved_count += 1
        elif choice == "2":
            if save_to_markdown(article, output_dir):
                saved_count += 1
        elif choice == "3":
            supabase_success = save_to_supabase(article)
            markdown_success = save_to_markdown(article, output_dir)
            if supabase_success or markdown_success:
                saved_count += 1
        else:
            print(f"  Preview for: {article['title']}")
            print(f"  Slug: {article['slug']}")
            print(f"  Niche: {article['metadata']['niche']}")
            print(f"  Volume: {article['metadata']['search_volume']}")
            print(f"  Intent: {article['metadata']['intent']}")
            print(f"  Image: {article['featured_image']}")

    print("\n" + "=" * 60)
    print("Content Generation Complete")
    print("=" * 60)

    if choice in ["1", "2", "3"]:
        print("\nResults:")
        print(f"  Processed: {len(keywords)} keywords")
        print(f"  Saved: {saved_count} articles")

        if choice in ["2", "3"]:
            print(f"  Markdown files: {output_dir}/")
        if choice in ["1", "3"]:
            print("  Database: Supabase")

    print("\nNext steps:")
    print("1. Review generated articles in database or files")
    print("2. Publish articles by changing status to 'published'")
    print("3. Deploy website to see articles live")


if __name__ == "__main__":
    main()
