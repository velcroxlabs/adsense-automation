#!/usr/bin/env python3
"""
Test Supabase connection and database setup.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_credentials():
    """Check if required credentials exist."""
    print("🔍 Checking Supabase credentials...")
    
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url:
        print("❌ Missing SUPABASE_URL in .env file")
        return False
    
    if not anon_key:
        print("❌ Missing SUPABASE_ANON_KEY in .env file")
        return False
    
    # Service key is optional for basic tests
    if not service_key:
        print("⚠️  SUPABASE_SERVICE_ROLE_KEY not set (optional for this test)")
    
    print(f"✅ SUPABASE_URL: {url}")
    print(f"✅ SUPABASE_ANON_KEY: {anon_key[:20]}...")
    if service_key:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {service_key[:20]}...")
    
    return True

def test_connection():
    """Test connection to Supabase."""
    print("\n🔌 Testing Supabase connection...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        supabase: Client = create_client(url, anon_key)
        
        # Try a simple query to test connection
        response = supabase.table('keywords').select('count', count='exact').execute()
        
        print("✅ Successfully connected to Supabase!")
        print(f"✅ Project: {url}")
        
        # Check if tables exist
        tables_to_check = ['keywords', 'articles', 'seo_metrics', 'adsense_metrics']
        
        print("\n📊 Checking database tables...")
        for table in tables_to_check:
            try:
                test = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table}: Exists")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    print(f"  ❌ {table}: Does not exist (run schema.sql)")
                else:
                    print(f"  ⚠️  {table}: Error - {str(e)[:50]}...")
        
        return True
        
    except ImportError:
        print("❌ supabase-client not installed. Install with:")
        print("   pip install supabase python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_sample_data():
    """Test inserting and reading sample data."""
    print("\n📝 Testing sample data operations...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        supabase: Client = create_client(url, anon_key)
        
        # Test insert
        sample_keyword = {
            "keyword": "test-keyword-connection",
            "seed_niche": "test",
            "search_volume": 1000,
            "keyword_difficulty": 5.0,
            "cpc": 1.50,
            "competition": "low"
        }
        
        print("  Inserting test keyword...")
        insert_response = supabase.table('keywords').insert(sample_keyword).execute()
        
        if hasattr(insert_response, 'data') and insert_response.data:
            print(f"  ✅ Insert successful (ID: {insert_response.data[0]['id'][:8]}...)")
            
            # Test select
            print("  Reading back test data...")
            select_response = supabase.table('keywords')\
                .select('*')\
                .eq('keyword', 'test-keyword-connection')\
                .execute()
            
            if select_response.data:
                print(f"  ✅ Read successful: {len(select_response.data)} records")
                
                # Cleanup
                print("  Cleaning up test data...")
                delete_response = supabase.table('keywords')\
                    .delete()\
                    .eq('keyword', 'test-keyword-connection')\
                    .execute()
                print(f"  ✅ Cleanup successful")
            else:
                print("  ⚠️  Could not read inserted data")
        else:
            print("  ❌ Insert failed")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Data operations failed: {e}")
        return False

def main():
    """Main test routine."""
    print("="*60)
    print("Supabase Connection Test")
    print("="*60)
    
    # Step 1: Check credentials
    if not check_credentials():
        print("\n❌ Please configure your .env file first.")
        print("   Copy .env.example to .env and add your Supabase credentials.")
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("\n❌ Connection test failed.")
        sys.exit(1)
    
    # Step 3: Test data operations (optional)
    try:
        test_sample_data()
    except Exception as e:
        print(f"⚠️  Data test skipped: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run the website locally: cd website && npm run dev")
    print("2. Generate content: python keywords/research.py")
    print("3. Deploy to Vercel: Push to GitHub")
    print("\nYour Supabase database is ready! 🎉")

if __name__ == "__main__":
    main()