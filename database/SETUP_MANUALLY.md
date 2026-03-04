# Manual Supabase Setup Guide

## Step 1: Create Supabase Account & Project

1. **Go to [supabase.com](https://supabase.com)** and sign up/login
2. Click **"New Project"**
3. Fill in project details:
   - **Name**: `adsense-automation`
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to your audience (e.g., `North Virginia`)
   - **Pricing Plan**: **Free** tier (perfect for starting)
4. Click **"Create new project"**
5. Wait 2-3 minutes for project to be created

## Step 2: Get Project Credentials

1. Go to **Project Settings** (gear icon in left sidebar)
2. Click **"API"** in the settings menu
3. Copy these three values:

```
Project URL: https://xxxxxxxxxxxx.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ Important:**
- **Project URL**: Your unique Supabase endpoint
- **anon key**: Public key for client-side usage
- **service_role key**: **KEEP SECRET!** Only for server-side/scripts

## Step 3: Execute Database Schema

1. Go to **SQL Editor** in left sidebar
2. Click **"New query"**
3. Copy the entire contents of `database/schema.sql`:
   ```bash
   cat ~/.openclaw/workspace/adsense-automation/database/schema.sql
   ```
4. Paste into SQL Editor
5. Click **"Run"** or press `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

**Expected Output:**
- All tables created successfully
- No errors (might see warnings about existing tables if re-running)

## Step 4: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cd ~/.openclaw/workspace/adsense-automation
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   nano .env
   ```

3. Update these lines:
   ```
   SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

## Step 5: Test Connection

Run the test script:
```bash
cd ~/.openclaw/workspace/adsense-automation
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
anon_key = os.getenv('SUPABASE_ANON_KEY')

if url and anon_key:
    print(f'✅ URL: {url}')
    print(f'✅ Anon key: {anon_key[:20]}...')
    print('Credentials loaded successfully!')
else:
    print('❌ Missing credentials in .env file')
"
```

## Step 6: Test Database Connection (Optional)

Create a test script `test_supabase.py`:
```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    
    # Test connection by fetching something
    response = supabase.table('keywords').select('*').limit(1).execute()
    
    if hasattr(response, 'data'):
        print(f"✅ Connected to Supabase!")
        print(f"✅ Project: {url}")
        print(f"✅ Tables accessible: Yes")
    else:
        print(f"⚠️  Connected but could not fetch data")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Troubleshooting

### Common Issues:

1. **"Invalid API key" error**
   - Verify you copied the correct key (anon vs service_role)
   - Check for extra spaces or newlines in .env file

2. **"Table does not exist" error**
   - Make sure you executed the schema SQL
   - Check table names are lowercase in your code

3. **Connection timeout**
   - Check internet connection
   - Verify Project URL is correct
   - Ensure Supabase project is active (not paused)

4. **Permission errors**
   - Use `anon` key for client-side operations
   - Use `service_role` key for administrative scripts
   - Check Row Level Security (RLS) if you enabled it

## Next Steps After Setup

1. **Test the website locally:**
   ```bash
   cd website
   npm run dev
   ```
   Open `http://localhost:4321`

2. **Generate sample data:**
   ```bash
   # Run keyword research
   python keywords/research.py
   ```

3. **Deploy to Vercel:**
   - Push to GitHub
   - Connect Vercel to your repository
   - Add environment variables in Vercel dashboard

## Security Notes

- **NEVER commit `.env` file to Git**
- Add `.env` to `.gitignore` if not already
- **service_role key** has full database access - keep it secret!
- Use environment variables in production (Vercel, GitHub Secrets)

## Support

- Supabase Docs: https://supabase.com/docs
- Project Issues: Check GitHub repository
- Discord Community: https://discord.gg/clawd

---

**Last Updated:** 2026-03-04  
**Status:** Ready for setup