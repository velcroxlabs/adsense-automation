# Quick Start Guide - AdSense Automation

## 🚀 Project Status (DEPLOYMENT IN PROGRESS)
- **Phase 0**: ✅ 85% complete (Research & Planning)
- **Phase 1**: ✅ 99% complete (Base Infrastructure - DEPLOYING)
- **Deployment**: ✅ Vercel project created and configured
- **Database**: ✅ Schema executed, connection verified
- **Website**: ✅ Builds successfully (6 pages + sitemap)
- **GitHub**: ✅ Repository created and pushed (velcroxlabs/adsense-automation)
- **CI/CD**: ✅ GitHub Actions + Vercel auto-deploy configured
- **Environment**: ✅ Supabase variables configured in Vercel
- **URL**: ⚡ **https://adsense-automation-muwg1qkba-velcroxlabs-projects.vercel.app**

## Prerequisites
```bash
# 1. Python environment
cd ~/.openclaw/workspace/adsense-automation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # If exists, or:
pip install supabase python-dotenv pytrends pandas

# 2. Node.js for website
cd website
npm install
```

## Setup Checklist

### 1. Domain (Choose one)
- [ ] Decide on domain name (`.com` preferred, `.net/.org` backup)
- [ ] Register at Namecheap/GoDaddy (~$10-15/year)
- [ ] Configure DNS for Vercel

### 2. Supabase Database
```bash
# Option A: Use guided script
python scripts/setup-supabase.py

# Option B: Manual setup
# Follow database/SETUP_MANUALLY.md
```

### 3. Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env  # Add Supabase, Vercel, API keys
```

### 4. Test Everything
```bash
# Test Supabase connection
python scripts/test_supabase.py

# Test website build
cd website
npm run build

# Test locally
npm run dev  # http://localhost:4321
```

## Deployment

### 1. GitHub Setup
```bash
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/your-username/adsense-automation.git
git push -u origin main
```

### 2. Vercel Deployment
1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Add environment variables in Vercel dashboard
4. Deploy automatically

### 3. Domain Configuration (Vercel)
1. In Vercel dashboard: Settings → Domains
2. Add your purchased domain
3. Configure DNS as instructed

## Content Generation

### Initial Content Batch
```bash
# Generate keywords
python keywords/research.py

# Generate articles (requires LLM API keys)
# python scripts/generate_content.py  # Coming soon
```

### Automation Schedule
- **Daily**: 5-10 new articles (2:00 AM UTC)
- **Weekly**: Keyword research refresh
- **Monthly**: Performance review & optimization

## Monitoring

### Dashboard URLs
- **Website**: `https://your-domain.com`
- **Stats**: `https://your-domain.com/stats`
- **Vercel**: `https://vercel.com/your-project`
- **Supabase**: `https://app.supabase.com/project/your-project`

### Key Metrics to Watch
- **Traffic**: >1,000 sessions/month (goal)
- **RPM**: $10-20 (AdSense revenue per 1000 pageviews)
- **Indexing**: 70%+ articles indexed by Google
- **Uptime**: >99% (Vercel automatically)

## Common Commands

### Development
```bash
# Local development
cd website && npm run dev

# Build for production
cd website && npm run build

# Lint code
cd website && npm run lint
```

### Database
```bash
# Test connection
python scripts/test_supabase.py

# Reset database (careful!)
# Run schema.sql again in Supabase SQL Editor
```

### Git Workflow
```bash
# Add all changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

## Troubleshooting

### Website Won't Build
```bash
cd website
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Supabase Connection Fails
1. Check `.env` file credentials
2. Verify Supabase project is active
3. Test with `python scripts/test_supabase.py`
4. Check network/firewall settings

### No Traffic
1. Wait 1-2 weeks for Google indexing
2. Submit sitemap to Google Search Console
3. Check robots.txt isn't blocking crawlers
4. Verify content quality and uniqueness

## Next Phases

### Phase 2 (Content Pipeline)
- Advanced LLM integration
- Multimedia content generation
- Social media automation

### Phase 3 (Monetization Expansion)
- Affiliate marketing
- Sponsored content
- Premium subscriptions

### Phase 4 (Platform Features)
- User accounts
- Community features
- Mobile app

## Support & Resources
- **Project Docs**: Check `ARCHITECTURE.md`, `plan.md`
- **Supabase**: https://supabase.com/docs
- **Astro**: https://docs.astro.build
- **Vercel**: https://vercel.com/docs
- **Discord**: https://discord.gg/clawd

---

**Last Updated**: 2026-03-04  
**Status**: Ready for production setup  
**Maintainer**: Jarvis (OpenClaw Assistant)