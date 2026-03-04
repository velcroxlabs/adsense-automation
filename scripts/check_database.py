#!/usr/bin/env python3
"""
Check database schema and tables for AdSense Automation project.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    """Check database tables and schema."""
    print("="*60)
    print("Database Status Check")
    print("="*60)
    
    # Check credentials
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not anon_key:
        print("❌ Missing Supabase credentials in .env file")
        print("   Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set")
        sys.exit(1)
    
    print(f"✅ Supabase URL: {url}")
    print(f"✅ Anon key: {anon_key[:20]}...")
    
    try:
        from supabase import create_client, Client
        
        supabase: Client = create_client(url, anon_key)
        print("✅ Connected to Supabase")
        
        # List of expected tables
        expected_tables = [
            'keywords',
            'articles', 
            'seo_metrics',
            'adsense_metrics',
            'generation_logs'
        ]
        
        print("\n📊 Checking database tables...")
        print("-"*40)
        
        existing_tables = []
        missing_tables = []
        
        for table in expected_tables:
            try:
                # Try to query the table
                response = supabase.table(table).select('count', count='exact').limit(1).execute()
                
                # If we get here, table exists
                existing_tables.append(table)
                
                # Try to get row count
                count_response = supabase.table(table).select('*', count='exact').limit(1).execute()
                count = getattr(count_response, 'count', 0) or 0
                
                print(f"  ✅ {table}: Exists ({count} rows)")
                
            except Exception as e:
                error_msg = str(e)
                if "relation" in error_msg and "does not exist" in error_msg:
                    missing_tables.append(table)
                    print(f"  ❌ {table}: Does not exist")
                else:
                    print(f"  ⚠️  {table}: Error - {error_msg[:50]}...")
        
        # Summary
        print("\n" + "="*60)
        print("📋 Summary")
        print("="*60)
        
        if missing_tables:
            print(f"\n❌ Missing tables ({len(missing_tables)}/{len(expected_tables)}):")
            for table in missing_tables:
                print(f"  • {table}")
            
            print(f"\n🔧 Action required:")
            print(f"   1. Go to Supabase SQL Editor")
            print(f"   2. Copy contents of database/schema.sql")
            print(f"   3. Execute the SQL to create missing tables")
            print(f"\n   File: database/schema.sql")
            
        else:
            print(f"\n✅ All tables exist ({len(existing_tables)}/{len(expected_tables)})")
            
            # Check for sample data
            print(f"\n📝 Checking for sample data...")
            
            # Check keywords
            keywords_response = supabase.table('keywords').select('*', count='exact').limit(5).execute()
            keyword_count = getattr(keywords_response, 'count', 0) or 0
            
            # Check articles
            articles_response = supabase.table('articles').select('*', count='exact').limit(5).execute()
            article_count = getattr(articles_response, 'count', 0) or 0
            
            print(f"  • Keywords: {keyword_count} rows")
            print(f"  • Articles: {article_count} rows")
            
            if keyword_count == 0 and article_count == 0:
                print(f"\n💡 Tip: Run seed script to add sample data:")
                print(f"   python scripts/seed_database.py")
        
        # Test connection with actual query
        print(f"\n🔌 Testing data operations...")
        try:
            # Try to insert and delete a test record
            test_data = {
                "keyword": "database-test-connection",
                "seed_niche": "test",
                "search_volume": 1,
                "keyword_difficulty": 1.0,
                "cpc": 0.01,
                "competition": "low"
            }
            
            insert_response = supabase.table('keywords').insert(test_data).execute()
            
            if hasattr(insert_response, 'data') and insert_response.data:
                test_id = insert_response.data[0]['id']
                
                # Clean up
                delete_response = supabase.table('keywords').delete().eq('id', test_id).execute()
                
                print(f"  ✅ Data operations working correctly")
            else:
                print(f"  ⚠️  Could not insert test data")
                
        except Exception as e:
            print(f"  ⚠️  Data operation test failed: {str(e)[:50]}...")
        
        print("\n" + "="*60)
        print("✅ Check complete")
        print("="*60)
        
    except ImportError:
        print("❌ supabase-client not installed")
        print("   Install with: pip install supabase python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()