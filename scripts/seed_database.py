#!/usr/bin/env python3
"""
Seed database with sample data for AdSense Automation project.
Safe to run multiple times - uses upsert logic.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

def check_prerequisites():
    """Check if Supabase credentials are available."""
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not anon_key:
        print("❌ Missing Supabase credentials in .env file")
        print("   Run setup-supabase.py first or configure .env manually")
        return False
    
    return True

def seed_keywords(supabase):
    """Seed keywords table with sample data."""
    print("📊 Seeding keywords table...")
    
    sample_keywords = [
        {
            "keyword": "how to save money fast",
            "seed_niche": "personal finance",
            "search_volume": 12100,
            "keyword_difficulty": 8.0,
            "cpc": 2.34,
            "competition": "low",
        },
        {
            "keyword": "best credit cards for travel",
            "seed_niche": "personal finance",
            "search_volume": 9900,
            "keyword_difficulty": 12.0,
            "cpc": 5.67,
            "competition": "medium",
        },
        {
            "keyword": "how to fix a leaky faucet",
            "seed_niche": "home improvement",
            "search_volume": 4400,
            "keyword_difficulty": 3.0,
            "cpc": 1.23,
            "competition": "low",
        },
        {
            "keyword": "benefits of meditation",
            "seed_niche": "health & wellness",
            "search_volume": 40500,
            "keyword_difficulty": 7.0,
            "cpc": 1.23,
            "competition": "low",
        },
        {
            "keyword": "home renovation cost calculator",
            "seed_niche": "home improvement",
            "search_volume": 2900,
            "keyword_difficulty": 4.0,
            "cpc": 1.89,
            "competition": "low",
        },
    ]
    
    inserted_count = 0
    for keyword_data in sample_keywords:
        try:
            # Check if keyword already exists
            existing = supabase.table('keywords')\
                .select('id')\
                .eq('keyword', keyword_data['keyword'])\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                print(f"  ✓ Keyword '{keyword_data['keyword']}' already exists")
                continue
            
            # Insert new keyword
            response = supabase.table('keywords').insert(keyword_data).execute()
            
            if hasattr(response, 'data') and response.data:
                inserted_count += 1
                print(f"  ✓ Added: {keyword_data['keyword']}")
            else:
                print(f"  ⚠️  Failed to insert: {keyword_data['keyword']}")
                
        except Exception as e:
            print(f"  ❌ Error inserting keyword '{keyword_data['keyword']}': {e}")
    
    print(f"  Total keywords in database: {inserted_count} new, {len(sample_keywords)} total available")
    return inserted_count

def seed_articles(supabase):
    """Seed articles table with sample content."""
    print("\n📝 Seeding articles table...")
    
    # First, get some keyword IDs to associate with articles
    try:
        keywords_response = supabase.table('keywords').select('id, keyword').limit(5).execute()
        if not keywords_response.data:
            print("  ⚠️  No keywords found. Run keyword seeding first.")
            return 0
        
        keyword_ids = {k['keyword']: k['id'] for k in keywords_response.data}
    except Exception as e:
        print(f"  ❌ Error fetching keywords: {e}")
        return 0
    
    sample_articles = [
        {
            "title": "How to Save Money Fast: 10 Proven Strategies",
            "slug": "how-to-save-money-fast",
            "excerpt": "Learn practical tips to boost your savings rate and build financial security faster than you thought possible.",
            "content": "This is a sample article about saving money fast. In production, this would be AI-generated content with detailed information, tips, and actionable advice.",
            "keyword_id": keyword_ids.get("how to save money fast"),
            "status": "published",
            "published_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "metadata": {
                "word_count": 850,
                "reading_time": 5,
                "niche": "personal finance",
                "seed_keyword": "how to save money fast",
            }
        },
        {
            "title": "Best Credit Cards for Travel in 2025",
            "slug": "best-credit-cards-for-travel",
            "excerpt": "Compare the top travel credit cards and find the perfect one for your next adventure.",
            "content": "This is a sample article about travel credit cards. In production, this would include detailed comparisons, benefits analysis, and application tips.",
            "keyword_id": keyword_ids.get("best credit cards for travel"),
            "status": "published",
            "published_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "metadata": {
                "word_count": 1200,
                "reading_time": 7,
                "niche": "personal finance",
                "seed_keyword": "best credit cards for travel",
            }
        },
        {
            "title": "How to Fix a Leaky Faucet: DIY Guide for Beginners",
            "slug": "how-to-fix-leaky-faucet",
            "excerpt": "Step-by-step instructions to repair common faucet types and save hundreds on plumber bills.",
            "content": "This is a sample article about fixing leaky faucets. In production, this would include detailed instructions, tool lists, and troubleshooting tips.",
            "keyword_id": keyword_ids.get("how to fix a leaky faucet"),
            "status": "draft",
            "published_at": None,
            "metadata": {
                "word_count": 950,
                "reading_time": 5,
                "niche": "home improvement",
                "seed_keyword": "how to fix a leaky faucet",
            }
        },
    ]
    
    inserted_count = 0
    for article_data in sample_articles:
        try:
            # Check if article already exists
            existing = supabase.table('articles')\
                .select('id')\
                .eq('slug', article_data['slug'])\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                print(f"  ✓ Article '{article_data['slug']}' already exists")
                continue
            
            # Insert new article
            response = supabase.table('articles').insert(article_data).execute()
            
            if hasattr(response, 'data') and response.data:
                inserted_count += 1
                print(f"  ✓ Added: {article_data['title']}")
            else:
                print(f"  ⚠️  Failed to insert: {article_data['title']}")
                
        except Exception as e:
            print(f"  ❌ Error inserting article '{article_data['slug']}': {e}")
    
    print(f"  Total articles seeded: {inserted_count}")
    return inserted_count

def main():
    """Main seeding routine."""
    print("="*60)
    print("Database Seeding Script")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        supabase: Client = create_client(url, anon_key)
        
        print("✅ Connected to Supabase")
        
        # Seed keywords
        keyword_count = seed_keywords(supabase)
        
        # Seed articles
        article_count = seed_articles(supabase)
        
        # Summary
        print("\n" + "="*60)
        print("✅ Seeding Complete!")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"  • Keywords added: {keyword_count}")
        print(f"  • Articles added: {article_count}")
        
        if keyword_count > 0 or article_count > 0:
            print("\n🚀 Next steps:")
            print("1. Run the website locally: cd website && npm run dev")
            print("2. Visit http://localhost:4321 to see your content")
            print("3. Check Supabase dashboard to verify data")
        else:
            print("\n📝 Note: All sample data already exists in database")
        
        print("\n💡 Tip: You can run this script multiple times safely.")
        print("   It will only insert missing data, not create duplicates.")
        
    except ImportError:
        print("❌ supabase-client not installed.")
        print("   Install with: pip install supabase python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()