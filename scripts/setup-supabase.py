#!/usr/bin/env python3
"""
Supabase setup script for AdSense Automation project.
This script helps set up a Supabase project and database schema.
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

def print_step(step, message):
    print(f"\n[{step}] {message}")
    print("-" * 50)

def check_prerequisites():
    """Check if required tools are installed."""
    print_step(1, "Checking prerequisites")
    
    required_tools = {
        'node': 'Node.js (for Supabase CLI)',
        'npm': 'npm package manager',
    }
    
    missing_tools = []
    for tool, description in required_tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✓ {description} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"✗ {description} is NOT installed")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\nMissing tools: {', '.join(missing_tools)}")
        print("Please install them before continuing.")
        return False
    
    return True

def install_supabase_cli():
    """Install Supabase CLI if not already installed."""
    print_step(2, "Installing Supabase CLI")
    
    try:
        # Check if supabase CLI is already installed
        result = subprocess.run(['supabase', '--version'], capture_output=True)
        if result.returncode == 0:
            print("✓ Supabase CLI is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("Installing Supabase CLI via npm...")
    try:
        subprocess.run(['npm', 'install', '-g', 'supabase'], check=True)
        print("✓ Supabase CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install Supabase CLI: {e}")
        return False

def create_supabase_project():
    """Guide user through creating a Supabase project."""
    print_step(3, "Creating Supabase Project")
    
    print("\nTo create a Supabase project:")
    print("1. Go to https://supabase.com and sign up/login")
    print("2. Click 'New Project'")
    print("3. Fill in project details:")
    print("   - Name: adsense-automation")
    print("   - Database Password: Choose a strong password")
    print("   - Region: Choose closest to your audience")
    print("   - Pricing: Start with Free tier")
    print("\n4. Wait for project to be created (2-3 minutes)")
    
    input("\nPress Enter when you have created the project...")
    
    print("\n5. Get your project credentials:")
    print("   - Go to Project Settings > API")
    print("   - Copy the following:")
    print("     * Project URL")
    print("     * anon/public key")
    print("     * service_role key (keep this secret!)")
    
    return get_project_credentials()

def get_project_credentials():
    """Get project credentials from user."""
    print("\n" + "="*50)
    print("Please enter your Supabase project credentials:")
    print("="*50)
    
    credentials = {}
    credentials['SUPABASE_URL'] = input("\nProject URL: ").strip()
    credentials['SUPABASE_ANON_KEY'] = input("Anon/Public Key: ").strip()
    credentials['SUPABASE_SERVICE_ROLE_KEY'] = input("Service Role Key: ").strip()
    
    # Validate URL format
    if not credentials['SUPABASE_URL'].startswith('https://'):
        print("⚠️  URL should start with https://")
    
    # Save to .env file
    save_credentials(credentials)
    
    return credentials

def save_credentials(credentials):
    """Save credentials to .env file."""
    print_step(4, "Saving credentials to .env file")
    
    env_content = f"""# Supabase Configuration
SUPABASE_URL={credentials['SUPABASE_URL']}
SUPABASE_ANON_KEY={credentials['SUPABASE_ANON_KEY']}
SUPABASE_SERVICE_ROLE_KEY={credentials['SUPABASE_SERVICE_ROLE_KEY']}

# Website Configuration
SITE_URL=https://your-domain.com
SITE_NAME=AdSense Automation

# OpenAI/LLM Configuration
OPENAI_API_KEY=your-openai-key-here

# Google APIs
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json
"""
    
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✓ Credentials saved to {env_path}")
        print("\n⚠️  IMPORTANT: Add .env to .gitignore if not already!")
        print("   Do NOT commit this file to version control.")
    except Exception as e:
        print(f"✗ Failed to save .env file: {e}")
        return False
    
    return True

def run_database_schema():
    """Run the database schema SQL."""
    print_step(5, "Setting up database schema")
    
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        print(f"✗ Schema file not found: {schema_path}")
        return False
    
    print(f"Database schema file: {schema_path}")
    print("\nTo execute the schema:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Click 'New query'")
    print("4. Copy and paste the contents of database/schema.sql")
    print("5. Click 'Run' or press Ctrl+Enter")
    print("\nAlternatively, you can use the Supabase CLI:")
    print("  supabase db push")
    
    # Show preview of schema
    try:
        with open(schema_path, 'r') as f:
            schema_content = f.read()
            table_count = schema_content.count('CREATE TABLE')
            print(f"\nSchema contains {table_count} tables")
    except Exception as e:
        print(f"✗ Error reading schema: {e}")
    
    return True

def test_connection(credentials):
    """Test connection to Supabase."""
    print_step(6, "Testing connection to Supabase")
    
    if not credentials:
        print("✗ No credentials provided for testing")
        return False
    
    # Simple test using the REST API
    test_url = f"{credentials['SUPABASE_URL']}/rest/v1/"
    
    try:
        req = urllib.request.Request(test_url)
        req.add_header('apikey', credentials['SUPABASE_ANON_KEY'])
        req.add_header('Authorization', f'Bearer {credentials['SUPABASE_ANON_KEY']}')
        
        response = urllib.request.urlopen(req)
        if response.status == 200:
            print("✓ Successfully connected to Supabase")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✓ Connected (404 expected for root endpoint)")
            return True
        else:
            print(f"✗ HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
    
    return False

def main():
    """Main setup routine."""
    print("="*60)
    print("Supabase Setup for AdSense Automation Project")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Install Supabase CLI
    if not install_supabase_cli():
        print("\nYou can continue without CLI, but manual setup required.")
        choice = input("Continue without CLI? (y/n): ").lower()
        if choice != 'y':
            sys.exit(1)
    
    # Create project and get credentials
    credentials = create_supabase_project()
    
    # Run database schema
    run_database_schema()
    
    # Test connection
    if credentials:
        test_connection(credentials)
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Execute the database schema in Supabase SQL Editor")
    print("2. Update the .env file with your actual SITE_URL")
    print("3. Run 'npm run build' in the website directory")
    print("4. Configure GitHub Secrets with your Vercel tokens")
    print("5. Push to GitHub to trigger first deployment")
    print("\nFor questions, check the documentation or ask for help!")

if __name__ == '__main__':
    main()