import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: process.env.SITE_URL || 'https://example.com',
  trailingSlash: 'ignore',
  build: {
    format: 'directory'
  },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      serialize: (item) => {
        // Prioritize important pages
        if (item.url === '/') {
          return { ...item, priority: 1.0, changefreq: 'daily' };
        }
        return item;
      }
    }),
    tailwind()
  ],
  vite: {
    ssr: {
      noExternal: ['@supabase/supabase-js']
    }
  }
});