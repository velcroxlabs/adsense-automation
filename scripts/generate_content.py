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

# Try to import requests for Unsplash API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Requests library not installed. Install with: pip install requests")

def get_unsplash_image(keyword: str, niche: str) -> Optional[str]:
    """Get a relevant image from Unsplash for the article.
    Uses Unsplash Source API (public, no API key required).
    Returns image URL or None if not available.
    """
    if not REQUESTS_AVAILABLE:
        print("  ⚠️  Requests library not available for Unsplash images")
        return get_fallback_image(niche)
    
    try:
        # Build search query - combine keyword and niche for better results
        query = f"{keyword} {niche}".replace(" ", "%20")
        
        # Unsplash Source API (public, no API key, limited to 50 requests per hour)
        url = f"https://source.unsplash.com/featured/1200x800/?{query}"
        
        # Get the actual image URL (following redirects)
        response = requests.get(url, allow_redirects=True, timeout=10)
        
        if response.status_code == 200:
            image_url = response.url
            print(f"  📸 Found Unsplash image: {image_url[:80]}...")
            return image_url
        else:
            print(f"  ⚠️  Unsplash API error: {response.status_code}, using LoremFlickr")
            return get_fallback_image(niche)
            
    except Exception as e:
        print(f"  ⚠️  Unsplash image error: {e}, using LoremFlickr")
        return get_fallback_image(niche)

def get_fallback_image(niche: str) -> str:
    """Get a fallback image URL based on niche category.
    Uses LoremFlickr for keyword-based images (no API key needed).
    """
    # Map niches to Flickr tags for better relevance
    niche_tags = {
        "personal finance": "money,finance,business,currency",
        "home improvement": "home,renovation,tools,diy,construction",
        "health & wellness": "health,fitness,wellness,exercise,yoga",
        "health and wellness": "health,fitness,wellness,exercise,yoga",
        "general": "nature,landscape,abstract"
    }
    
    # Get tags for niche (default to general)
    tags = niche_tags.get(niche.lower(), "nature")
    
    # Use LoremFlickr - free, keyword-based, no API key
    # Format: https://loremflickr.com/1200/800/{tags}
    fallback_url = f"https://loremflickr.com/1200/800/{tags}"
    
    print(f"  📸 Using LoremFlickr image with tags: {tags}")
    return fallback_url

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
        
        # Create prompt based on intent and niche with SPICY AND VIRAL tone
        if intent == 'commercial':
            prompt = f"""Write a SPICY, VIRAL, and highly engaging article about '{keyword}' for a {niche} website.
            The article should be a provocative review and buying guide that creates buzz and gets shared.
            Include:
            1. CATCHY introduction that hooks readers immediately
            2. CONTROVERSIAL takes or surprising revelations about {keyword}
            3. Top 3-5 options ranked with BOLD opinions (not afraid to criticize)
            4. Comparison table with 🔥 HOT takes
            5. Buying considerations that challenge conventional wisdom
            6. Conclusion with STRONG, shareable recommendations
            7. FAQ section with provocative Q&A
            
            Write in a SPICY, VIRAL tone: Use emojis, bold statements, cliffhangers, and emotional triggers.
            Make it CONTROVERSIAL but informative. Target 1000-1200 words.
            IMPORTANT: This should be content people WANT to share on social media!"""
        elif intent == 'transactional':
            prompt = f"""Write a SPICY, VIRAL article about '{keyword}' for a {niche} website.
            The article should help readers compare options with HOT takes that challenge the status quo.
            Include:
            1. PROVOCATIVE introduction that questions common assumptions
            2. Key factors to consider with UNCONVENTIONAL advice
            3. Price ranges with SHOCKING value revelations
            4. Where to buy with INSIDER tips (online/offline)
            5. Tips for getting the best deal that most people don't know
            6. Conclusion with ACTIONABLE, shareable advice
            7. FAQ section with provocative questions
            
            Write in a BOLD, VIRAL tone: Use urgency, scarcity language, and emotional triggers.
            Make readers feel like they're getting SECRET information. Target 800-1000 words.
            This should be content that gets PEOPLE TALKING!"""
        else:  # informational
            prompt = f"""Write a SPICY, VIRAL guide about '{keyword}' for a {niche} website.
            The article should educate readers with PROVOCATIVE information that challenges norms.
            Include:
            1. HOOK introduction that surprises readers
            2. Key concepts explained with CONTROVERSIAL angles
            3. Step-by-step guide with UNCONVENTIONAL methods
            4. Common mistakes with SHOCKING consequences
            5. Best practices that DEFY traditional advice
            6. Advanced considerations that will BLOW readers' minds
            7. Conclusion with MEMORABLE, shareable takeaways
            8. FAQ section with provocative questions
            
            Write in an AUTHORITATIVE but REBELLIOUS tone: Challenge established wisdom.
            Use bold claims, surprising facts, and emotional storytelling.
            Target 1200-1500 words. This should be content people CAN'T HELP BUT SHARE!"""
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Using gpt-4o as closest available to gpt-5
            messages=[
                {"role": "system", "content": "You are a CONTROVERSIAL content creator writing SPICY, VIRAL articles designed to get maximum engagement and social shares. Use bold language, emotional triggers, surprising facts, and provocative opinions. Write in engaging English with proper markdown formatting, emojis, and attention-grabbing elements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,  # Higher temperature for more creativity
            max_tokens=3500
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
    
    # Create title variations based on keyword intent (SPICY AND VIRAL VERSION)
    intent = keyword_data.get('intent', 'informational')
    
    if intent == 'commercial':
        title = f"🔥 {keyword.upper()} - The SHOCKING Truth Nobody Tells You! 🚨"
    elif intent == 'transactional':
        title = f"💥 {keyword.title()} - These SECRETS Will Save You Thousands! 💰"
    else:  # informational
        title = f"🤯 {keyword.title()} - The EXPLOSIVE Guide They Don't Want You to Read! 📖"
    
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
    
    # Create excerpt (SPICY AND VIRAL VERSION)
    excerpt = f"🚨 WARNING: What you know about {keyword} is WRONG! Discover the shocking truth that will blow your mind. This explosive guide reveals secrets nobody wants you to know! 🔥"
    
    # Get Unsplash image for article
    featured_image = get_unsplash_image(keyword, niche)
    
    # Create article structure
    article = {
        'id': str(uuid.uuid4()),
        'title': title,
        'slug': slug,
        'excerpt': excerpt,
        'content': content,
        'featured_image': featured_image,
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
    # Use absolute path to keywords file
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    keywords_csv = os.path.join(project_root, "keywords", "final_batch.csv")
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
    
    # Check if running interactively
    import sys
    if not sys.stdin.isatty():
        # Non-interactive mode, auto-select option 1
        choice = "1"
        print(f"\n  (Auto-selected option {choice} for non-interactive execution)")
    else:
        # Interactive mode, ask for input
        try:
            choice = input("\nSelect option (1-4): ").strip()
        except EOFError:
            choice = "1"  # Default to save to Supabase if running non-interactively
            print(f"  (Auto-selected option {choice} for non-interactive execution)")
    
    # Process each keyword
    print(f"\n🔧 Processing {len(keywords)} keywords...")
    
    saved_count = 0
    for i, keyword_data in enumerate(keywords, 1):  # Process all keywords in batch
        keyword = keyword_data.get('keyword', 'Unknown')
        print(f"\n[{i}/{len(keywords)}] Generating: {keyword}")
        
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
        print(f"  • Processed: {len(keywords)} keywords")
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