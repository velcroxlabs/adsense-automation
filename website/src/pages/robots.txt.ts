import type { APIRoute } from 'astro';

const getRobotsTxt = (sitemapURL: string) => `User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Crawl-delay: 10

Sitemap: ${sitemapURL}

# Host: https://your-domain.com

User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Anthropic-ai
Disallow: /

User-agent: Claude-Web
Disallow: /

# AdsBot for Google AdSense
User-agent: AdsBot-Google
Allow: /
Disallow: /admin/
`;

export const GET: APIRoute = ({ site }) => {
  const sitemapURL = new URL('sitemap-index.xml', site);
  return new Response(getRobotsTxt(sitemapURL.href), {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};