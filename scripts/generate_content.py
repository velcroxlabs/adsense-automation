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


def load_keywords(csv_path: str) -> List[Dict[str, Any]]:
    """Load keywords from a CSV file."""
    keywords: List[Dict[str, Any]] = []

    try:
        with open(csv_path, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                keywords.append(row)

        print(f"Loaded {len(keywords)} keywords from {csv_path}")
        return keywords
    except FileNotFoundError:
        print(f"Keywords file not found: {csv_path}")
        return []
    except Exception as exc:
        print(f"Error loading keywords: {exc}")
        return []


def create_slug(keyword: str) -> str:
    """Convert keyword to URL-friendly slug."""
    slug = keyword.lower().strip()
    slug = slug.replace(" ", "-")
    slug = "".join(character for character in slug if character.isalnum() or character == "-")
    slug = "-".join(filter(None, slug.split("-")))
    return slug[:100]


def generate_content_with_openai(keyword: str, niche: str, intent: str) -> Optional[str]:
    """Generate article content using OpenAI API."""
    if not OPENAI_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  OPENAI_API_KEY not found in .env")
        return None

    try:
        client = OpenAI(api_key=api_key)

        if intent == "commercial":
            prompt = f"""Write a high-engagement article about '{keyword}' for a {niche} website.
            The article should be a sharp review and buying guide that stays credible and useful.
            Include:
            1. A strong introduction that hooks the reader immediately
            2. Unexpected or non-obvious observations about {keyword}
            3. Top 3-5 options ranked with clear opinions and tradeoffs
            4. A comparison table
            5. Buying considerations that challenge weak conventional advice
            6. A conclusion with concrete recommendations
            7. An FAQ section

            Write in a bold but professional tone. Target 1000-1200 words."""
        elif intent == "transactional":
            prompt = f"""Write a compelling article about '{keyword}' for a {niche} website.
            The article should help readers compare options and make a decision.
            Include:
            1. A direct introduction that questions common assumptions
            2. Key decision factors with practical advice
            3. Price ranges and value considerations
            4. Where to buy with realistic tips
            5. How to avoid overpaying
            6. A conclusion with actionable advice
            7. An FAQ section

            Write in a confident, high-clarity tone. Target 800-1000 words."""
        else:
            prompt = f"""Write an engaging guide about '{keyword}' for a {niche} website.
            The article should educate readers with useful, differentiated insight.
            Include:
            1. A surprising introduction
            2. Key concepts explained clearly
            3. A step-by-step guide or detailed framework
            4. Common mistakes and their consequences
            5. Best practices
            6. Advanced considerations
            7. A conclusion with memorable takeaways
            8. An FAQ section

            Write in an authoritative but readable tone. Target 1200-1500 words."""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional content writer creating SEO-oriented articles with strong hooks, clear structure, and readable markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.75,
            max_tokens=3500,
        )

        content = response.choices[0].message.content
        print(f"  Generated content with OpenAI ({len(content)} characters)")
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

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    keywords_csv = os.path.join(project_root, "keywords", "final_batch.csv")
    output_dir = "content/articles"

    keywords = load_keywords(keywords_csv)
    if not keywords:
        print("No keywords to process")
        return

    print("\nProcessing method:")
    print("1. Save to Supabase database (requires setup)")
    print("2. Save as Markdown files")
    print("3. Both")
    print("4. Preview only (no save)")

    if not sys.stdin.isatty():
        choice = "1"
        print(f"\n  Auto-selected option {choice} for non-interactive execution")
    else:
        try:
            choice = input("\nSelect option (1-4): ").strip()
        except EOFError:
            choice = "1"
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
