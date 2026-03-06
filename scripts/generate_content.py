#!/usr/bin/env python3
"""
Content generation script for AdSense Automation.
Generates article structures from keywords and saves to Supabase or Markdown files.
"""

import os
import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv
load_dotenv()

# Try to import OpenAI for LLM content generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not installed. Install with: pip install openai")

def load_keywords(csv_path: str) -> List[Dict[str, Any]]:
    """Load keywords from CSV file."""
    keywords = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords.append(row)
        
        print(f"✅ Loaded {len(keywords)} keywords from {csv_path}")
        return keywords
    
    except FileNotFoundError:
        print(f"❌ Keywords file not found: {csv_path}")
        return []
    except Exception as e:
        print(f"❌ Error loading keywords: {e}")
        return []

def create_slug(keyword: str) -> str:
    """Convert keyword to URL-friendly slug."""
    # Simple slug creation - in production, use a proper slug library
    slug = keyword.lower().strip()
    slug = slug.replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    slug = '-'.join(filter(None, slug.split('-')))  # Remove empty segments
    return slug[:100]  # Limit length

def generate_content_with_openai(keyword: str, niche: str, intent: str) -> str:
    """Generate article content using OpenAI API."""
    if not OPENAI_AVAILABLE:
        return None
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ⚠️  OPENAI_API_KEY not found in .env")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Create prompt based on intent and niche
        if intent == 'commercial':
            prompt = f"""Write a comprehensive, SEO-optimized article about '{keyword}' for a {niche} website.
            The article should be a review and buying guide that helps readers make informed decisions.
            Include:
            1. Introduction explaining the importance of {keyword}
            2. Key features to look for
            3. Top 3-5 options with pros and cons
            4. Comparison table
            5. Buying considerations
            6. Conclusion with recommendations
            7. FAQ section
            
            Write in a professional, helpful tone. Target 1000-1200 words."""
        elif intent == 'transactional':
            prompt = f"""Write a detailed, SEO-optimized article about '{keyword}' for a {niche} website.
            The article should help readers compare options and make purchasing decisions.
            Include:
            1. Introduction to {keyword} and its importance
            2. Key factors to consider when choosing
            3. Price ranges and value considerations
            4. Where to buy (online/offline options)
            5. Tips for getting the best deal
            6. Conclusion with actionable advice
            7. FAQ section
            
            Write in a practical, informative tone. Target 800-1000 words."""
        else:  # informational
            prompt = f"""Write a comprehensive, SEO-optimized guide about '{keyword}' for a {niche} website.
            The article should educate readers with complete information.
            Include:
            1. Introduction explaining what {keyword} is
            2. Key concepts and terminology
            3. Step-by-step guide or detailed explanation
            4. Common mistakes to avoid
            5. Best practices and tips
            6. Advanced considerations (if applicable)
            7. Conclusion summarizing key points
            8. FAQ section
            
            Write in an authoritative yet accessible tone. Target 1200-1500 words."""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional content writer creating SEO-optimized articles for a blog. Write in clear, engaging English with proper markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content
        print(f"  ✅ Generated content with OpenAI ({len(content)} characters)")
        return content
    
    except Exception as e:
        print(f"  ❌ OpenAI API error: {e}")
        return None

def generate_article_structure(keyword_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate article structure from keyword data."""
    keyword = keyword_data.get('keyword', '')
    niche = keyword_data.get('niche', 'General')
    
    # Create title variations based on keyword intent
    intent = keyword_data.get('intent', 'informational')
    
    if intent == 'commercial':
        title = f"Best {keyword} - Reviews & Buying Guide"
    elif intent == 'transactional':
        title = f"{keyword.title()} - Compare Options & Prices"
    else:  # informational
        title = f"{keyword.title()} - Complete Guide"
    
    slug = create_slug(keyword)
    
    # Try to generate content with OpenAI
    ai_content = generate_content_with_openai(keyword, niche, intent)
    
    if ai_content:
        content = ai_content
        word_count = len(ai_content.split())
        requires_llm = False
        print(f"  ✅ AI-generated content ({word_count} words)")
    else:
        # Generate placeholder content structure
        word_count = 800  # Target word count
        content = f"<!-- PLACEHOLDER CONTENT FOR: {keyword} -->\n\n"
        content += f"This article will be automatically generated about {keyword}. "
        content += f"The final content will include detailed information, tips, and practical advice.\n\n"
        content += f"**Expected sections:**\n"
        content += f"1. Introduction to {keyword}\n"
        content += f"2. Key concepts and terminology\n"
        content += f"3. Step-by-step guide\n"
        content += f"4. Common mistakes to avoid\n"
        content += f"5. Best practices and tips\n"
        content += f"6. Frequently asked questions\n\n"
        content += f"*Note: This is a placeholder. The final article will be generated by AI "
        content += f"and will be 100% unique, informative, and SEO-optimized.*"
        requires_llm = True
        print(f"  ⚠️  Using placeholder content (AI generation not available)")
    
    # Create excerpt
    excerpt = f"Learn everything about {keyword}. This comprehensive guide covers all aspects you need to know."
    
    # Create article structure
    article = {
        'id': str(uuid.uuid4()),
        'title': title,
        'slug': slug,
        'excerpt': excerpt,
        'content': content,
        'keyword_id': None,  # Will be set when keyword is inserted to DB
        'status': 'draft',
        'published_at': None,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'metadata': {
            'word_count': word_count,
            'reading_time': round(word_count / 200),  # 200 words per minute
            'niche': niche,
            'seed_keyword': keyword,
            'search_volume': int(keyword_data.get('search_volume', 0)),
            'keyword_difficulty': float(keyword_data.get('kd', 0)),
            'cpc': float(keyword_data.get('cpc', 0)),
            'competition': keyword_data.get('competition', 'low'),
            'intent': intent,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'requires_llm': requires_llm,
            'ai_generated': ai_content is not None
        }
    }
    
    return article

def save_to_markdown(article: Dict[str, Any], output_dir: str):
    """Save article as Markdown file."""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"{article['slug']}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Create Markdown content
        md_content = f"""---
title: "{article['title']}"
slug: "{article['slug']}"
excerpt: "{article['excerpt']}"
date: {datetime.now(timezone.utc).date().isoformat()}
niche: "{article['metadata']['niche']}"
status: "{article['status']}"
word_count: {article['metadata']['word_count']}
reading_time: {article['metadata']['reading_time']}
seed_keyword: "{article['metadata']['seed_keyword']}"
search_volume: {article['metadata']['search_volume']}
keyword_difficulty: {article['metadata']['keyword_difficulty']}
cpc: {article['metadata']['cpc']}
competition: "{article['metadata']['competition']}"
intent: "{article['metadata']['intent']}"
---

{article['content']}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  📄 Saved to: {filepath}")
        return True
    
    except Exception as e:
        print(f"  ❌ Error saving Markdown: {e}")
        return False

def save_to_supabase(article: Dict[str, Any]) -> bool:
    """Save article to Supabase database."""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not anon_key:
            print("  ⚠️  Supabase credentials not found in .env")
            return False
        
        supabase: Client = create_client(url, anon_key)
        
        # Prepare article for insertion (remove None values)
        article_data = {k: v for k, v in article.items() if v is not None}
        
        # Insert into database
        response = supabase.table('articles').insert(article_data).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"  ✅ Saved to Supabase (ID: {response.data[0]['id'][:8]}...)")
            return True
        else:
            print(f"  ❌ Supabase insert failed: {response}")
            return False
    
    except ImportError:
        print("  ⚠️  supabase-client not installed")
        return False
    except Exception as e:
        print(f"  ❌ Supabase error: {e}")
        return False

def main():
    """Main content generation routine."""
    print("="*60)
    print("Content Generation Script")
    print("="*60)
    
    # Configuration
    keywords_csv = "keywords/sample_keywords.csv"
    output_dir = "content/articles"
    
    # Load keywords
    keywords = load_keywords(keywords_csv)
    if not keywords:
        print("❌ No keywords to process")
        return
    
    # Ask user for processing method
    print("\n📝 Processing method:")
    print("1. Save to Supabase database (requires setup)")
    print("2. Save as Markdown files")
    print("3. Both")
    print("4. Preview only (no save)")
    
    try:
        choice = input("\nSelect option (1-4): ").strip()
    except EOFError:
        choice = "4"  # Default to preview if running non-interactively
    
    # Process each keyword
    print(f"\n🔧 Processing {len(keywords)} keywords...")
    
    saved_count = 0
    for i, keyword_data in enumerate(keywords[:10], 1):  # Limit to 10 for demo
        keyword = keyword_data.get('keyword', 'Unknown')
        print(f"\n[{i}/{len(keywords[:10])}] Generating: {keyword}")
        
        # Generate article structure
        article = generate_article_structure(keyword_data)
        
        # Process based on choice
        if choice == "1":  # Supabase only
            if save_to_supabase(article):
                saved_count += 1
        
        elif choice == "2":  # Markdown only
            if save_to_markdown(article, output_dir):
                saved_count += 1
        
        elif choice == "3":  # Both
            supabase_success = save_to_supabase(article)
            markdown_success = save_to_markdown(article, output_dir)
            if supabase_success or markdown_success:
                saved_count += 1
        
        else:  # Preview only
            print(f"  📝 Preview for: {article['title']}")
            print(f"  🔗 Slug: {article['slug']}")
            print(f"  📊 Niche: {article['metadata']['niche']}")
            print(f"  📈 Volume: {article['metadata']['search_volume']}")
            print(f"  🎯 Intent: {article['metadata']['intent']}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ Content Generation Complete!")
    print("="*60)
    
    if choice in ["1", "2", "3"]:
        print(f"\n📊 Results:")
        print(f"  • Processed: {len(keywords[:10])} keywords")
        print(f"  • Saved: {saved_count} articles")
        
        if choice in ["2", "3"]:
            print(f"  • Markdown files: {output_dir}/")
        
        if choice in ["1", "3"]:
            print(f"  • Database: Supabase")
    
    print("\n🚀 Next steps:")
    print("1. For LLM content generation: OpenAI API key detected in .env")
    print("2. Review generated articles in database or files")
    print("3. Publish articles by changing status to 'published'")
    print("4. Deploy website to see articles live")

if __name__ == "__main__":
    main()