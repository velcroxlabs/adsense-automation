-- Database schema for AdSense Automation Project
-- Designed for PostgreSQL (Supabase)

-- Keywords table: stores researched keywords with metrics
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword TEXT NOT NULL,
    seed_niche TEXT,
    search_volume INTEGER,
    keyword_difficulty DECIMAL(5,2),
    cpc DECIMAL(10,2),
    competition TEXT, -- 'low', 'medium', 'high'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(keyword)
);

-- Articles table: generated content
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,
    featured_image TEXT,
    keyword_id UUID REFERENCES keywords(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'draft', -- 'draft', 'published', 'scheduled'
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb -- SEO meta, word count, etc.
);

-- SEO metrics table: track rankings and performance
CREATE TABLE seo_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    keyword_id UUID REFERENCES keywords(id) ON DELETE CASCADE,
    google_position INTEGER,
    impressions INTEGER,
    clicks INTEGER,
    ctr DECIMAL(5,2),
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, keyword_id, date)
);

-- AdSense metrics table: revenue tracking
CREATE TABLE adsense_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    page_views INTEGER,
    ad_impressions INTEGER,
    ad_clicks INTEGER,
    revenue DECIMAL(10,2),
    rpm DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, date)
);

-- Content generation logs: track LLM usage and costs
CREATE TABLE generation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    model TEXT,
    cost DECIMAL(10,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_keywords_niche ON keywords(seed_niche);
CREATE INDEX idx_keywords_difficulty ON keywords(keyword_difficulty);
CREATE INDEX idx_keywords_volume ON keywords(search_volume);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_published ON articles(published_at);
CREATE INDEX idx_seo_metrics_date ON seo_metrics(date);
CREATE INDEX idx_adsense_metrics_date ON adsense_metrics(date);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
