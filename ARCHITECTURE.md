# Architecture - AdSense Automation System

## Overview
Zero-Human-Touch automated content generation and monetization system for niche websites.

## System Components

### 1. Content Pipeline
```
Keyword Research → Data Scraping → LLM Generation → Quality Review → Auto-Publishing
```

### 2. Technology Stack
```
Frontend: Astro (SSG) + Tailwind CSS
Backend: Supabase (PostgreSQL) + Node.js/Python microservices
Deployment: Vercel + GitHub Actions CI/CD
Automation: Python scripts + Make + Cron jobs
AI/ML: OpenAI GPT-4 + Anthropic Claude APIs
```

## Data Flow

### A. Keyword Research Phase
1. **Input**: Seed niches (Personal Finance, Home Improvement, Health & Wellness)
2. **Process**: Google Trends API → Keyword filtering (KD≤10, SV≥1000)
3. **Output**: Filtered keywords stored in `keywords` table

### B. Content Generation Phase
1. **Input**: Filtered keywords + Scraped reference data
2. **Process**: LLM API calls with specialized prompts
3. **Quality Control**: Automated checks (originality, readability, accuracy)
4. **Output**: Articles stored in `articles` table

### C. Publishing Phase
1. **Input**: Quality-approved articles
2. **Process**: Automatic build trigger → Vercel deployment
3. **SEO**: Auto-indexing via Search Console API
4. **Output**: Live website with new content

### D. Monitoring Phase
1. **Tracking**: Google Analytics 4 + Search Console metrics
2. **Monetization**: AdSense revenue tracking
3. **Optimization**: A/B testing + Performance analysis
4. **Alerting**: Anomaly detection + Automated reports

## Database Schema

### Core Tables
- **keywords**: Researched keywords with metrics (volume, difficulty, CPC)
- **articles**: Generated content with metadata (status, published_at, SEO data)
- **seo_metrics**: Search rankings and performance over time
- **adsense_metrics**: Revenue, RPM, CTR tracking
- **generation_logs**: LLM usage and costs

### Relationships
```
keywords (1) → (many) articles
articles (1) → (many) seo_metrics
articles (1) → (many) adsense_metrics
```

## Automation Workflows

### Daily Workflow (GitHub Actions)
1. **2:00 AM UTC**: Trigger content update pipeline
2. **Content Generation**: 5-10 new articles based on keyword research
3. **Build & Deploy**: Automatic Vercel deployment
4. **Indexing**: Submit new URLs to Google Search Console
5. **Reporting**: Send daily performance summary

### Weekly Workflow
1. **Keyword Research Refresh**: New keyword discovery
2. **Content Optimization**: Update underperforming articles
3. **Performance Review**: Analyze RPM, CTR, traffic trends
4. **System Maintenance**: Cleanup logs, backup database

## Security & Compliance

### Data Security
- Environment variables for all secrets
- Supabase Row Level Security (RLS)
- HTTPS everywhere (Vercel automatic SSL)
- Regular security updates via Dependabot

### Content Compliance
- AI-generated content disclosure
- Medical/financial disclaimer implementation
- AdSense policy compliance checks
- Copyright/plagiarism detection

### Privacy
- No personal data collection (GDPR-friendly)
- Anonymous analytics
- Cookie consent implementation
- Privacy policy page

## Scalability Considerations

### Horizontal Scaling
- Multi-niche expansion (add new niches easily)
- Multi-language support (internationalization)
- Multi-region deployment (CDN optimization)

### Performance Optimization
- Static site generation (Astro)
- Image optimization (Sharp/Cloudinary)
- Database indexing for frequent queries
- Caching strategy (Vercel Edge Network)

### Cost Management
- LLM token usage optimization
- API call batching
- Free tier utilization (Supabase, Vercel)
- Monitoring and alerting on cost overruns

## Monitoring & Alerting

### Key Metrics
- **Traffic**: Sessions, pageviews, bounce rate
- **SEO**: Rankings, impressions, clicks
- **Monetization**: RPM, CTR, revenue
- **System**: Uptime, build success, error rate

### Alert Channels
- Discord notifications for critical issues
- Email alerts for revenue anomalies
- Dashboard for real-time monitoring
- Weekly summary reports

## Development Workflow

### Local Development
```bash
cd website
npm install
npm run dev  # Local Astro development server
```

### Testing
- Unit tests for utility functions
- Integration tests for API endpoints
- End-to-end tests for critical user journeys

### Deployment
1. Push to `main` branch triggers GitHub Actions
2. Automated tests run
3. Build Astro site
4. Deploy to Vercel
5. Run post-deployment checks

## Future Enhancements

### Phase 2 (Content Pipeline)
- Advanced LLM fine-tuning
- Multimedia content generation (images, videos)
- Social media auto-posting
- Email newsletter automation

### Phase 3 (Monetization Expansion)
- Affiliate marketing integration
- Sponsored content marketplace
- Premium subscription tier
- E-commerce integration

### Phase 4 (Platform Features)
- User accounts and personalization
- Community features (comments, forums)
- Mobile app development
- API for third-party developers

## Troubleshooting Guide

### Common Issues
1. **Build failures**: Check Astro/Tailwind compatibility
2. **API rate limits**: Implement retry logic with exponential backoff
3. **Database connection**: Verify Supabase credentials and network
4. **Content quality**: Adjust LLM prompts and review thresholds

### Recovery Procedures
- Database backup and restore process
- Content regeneration for failed articles
- Rollback to previous deployment
- Emergency shutdown procedures

---

**Last Updated**: 2026-03-03  
**Version**: 1.0  
**Status**: Phase 1 (Infrastructure) in progress