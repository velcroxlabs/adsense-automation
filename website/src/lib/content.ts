import { getSupabaseServerClient } from "./supabase";

export const CATEGORY_SLUGS = [
  "personal-finance",
  "home-improvement",
  "health-wellness",
] as const;

export type CategorySlug = (typeof CATEGORY_SLUGS)[number];

type KeywordRelation =
  | {
      seed_niche?: string | null;
    }
  | {
      seed_niche?: string | null;
    }[]
  | null;

type ArticleRow = {
  title: string;
  excerpt: string | null;
  slug: string;
  content: string | null;
  published_at: string | null;
  featured_image: string | null;
  metadata: Record<string, unknown> | null;
  keywords: KeywordRelation;
};

const ARTICLE_SELECT_WITH_FEATURED_IMAGE =
  "title,excerpt,slug,content,published_at,featured_image,metadata,keywords(seed_niche)";
const ARTICLE_SELECT_LEGACY =
  "title,excerpt,slug,content,published_at,metadata,keywords(seed_niche)";

export type WebsiteArticle = {
  title: string;
  excerpt: string;
  slug: string;
  content: string;
  publishedAt: string | null;
  dateLabel: string;
  readTimeLabel: string;
  author: string;
  image: string;
  niche: string;
  categorySlug: CategorySlug;
  wordCount: number;
};

const FALLBACK_IMAGE_POOLS: Record<CategorySlug, string[]> = {
  "personal-finance": [
    "https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1554260570-e9689a3418b8?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1565514020179-026b92b84bb6?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?auto=format&fit=crop&q=80&w=1600",
  ],
  "home-improvement": [
    "https://images.unsplash.com/photo-1493666438817-866a91353ca9?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1502005097973-6a7082348e28?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&q=80&w=1600&crop=entropy",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1460317442991-0ec209397118?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1464890100898-a385f744067f?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1480074568708-e7b720bb3f09?auto=format&fit=crop&q=80&w=1600",
  ],
  "health-wellness": [
    "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1514996937319-344454492b37?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1494390248081-4e521a5940db?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&q=80&w=1600",
    "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&q=80&w=1600",
  ],
};

const pickFallbackImage = (categorySlug: CategorySlug, slug: string): string => {
  const pool = FALLBACK_IMAGE_POOLS[categorySlug];
  const seed = `${categorySlug}:${slug}`;
  let hash = 0;

  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }

  return pool[hash % pool.length];
};

const asObject = (value: unknown): Record<string, unknown> =>
  typeof value === "object" && value !== null ? (value as Record<string, unknown>) : {};

const asString = (value: unknown): string | null =>
  typeof value === "string" && value.trim().length > 0 ? value.trim() : null;

const asPositiveInt = (value: unknown): number | null =>
  typeof value === "number" && Number.isFinite(value) && value > 0
    ? Math.round(value)
    : null;

const getSeedNiche = (keywords: KeywordRelation): string => {
  if (Array.isArray(keywords) && keywords.length > 0) {
    return asString(keywords[0]?.seed_niche) ?? "personal finance";
  }

  if (keywords && typeof keywords === "object" && !Array.isArray(keywords)) {
    return asString(keywords.seed_niche) ?? "personal finance";
  }

  return "personal finance";
};

export const nicheToCategorySlug = (niche: string): CategorySlug => {
  const normalized = niche.toLowerCase();

  if (normalized.includes("home")) {
    return "home-improvement";
  }

  if (normalized.includes("health") || normalized.includes("wellness")) {
    return "health-wellness";
  }

  return "personal-finance";
};

const mapRowToWebsiteArticle = (row: ArticleRow): WebsiteArticle => {
  const niche = getSeedNiche(row.keywords);
  const categorySlug = nicheToCategorySlug(niche);
  const metadata = asObject(row.metadata);

  const content =
    asString(row.content) ??
    "This article content is being prepared. Please check back for the full edition.";

  const wordCount =
    asPositiveInt(metadata.word_count) ??
    Math.max(400, Math.ceil(content.split(/\s+/).length));
  const readTimeMinutes = Math.max(3, Math.ceil(wordCount / 200));

  return {
    title: row.title,
    excerpt: asString(row.excerpt) ?? "No excerpt is available for this article yet.",
    slug: row.slug,
    content,
    publishedAt: row.published_at,
    dateLabel: row.published_at
      ? new Date(row.published_at)
          .toLocaleDateString("en-US", { month: "long", year: "numeric" })
          .toUpperCase()
      : "RECENT EDITION",
    readTimeLabel: `${readTimeMinutes} min read`,
    author: asString(metadata.author) ?? "Editorial Staff",
    image:
      asString(row.featured_image) ??
      asString(metadata.image) ??
      pickFallbackImage(categorySlug, row.slug),
    niche,
    categorySlug,
    wordCount,
  };
};

export const getPublishedArticles = async (limit = 50): Promise<WebsiteArticle[]> => {
  const supabase = getSupabaseServerClient();
  if (!supabase) {
    console.warn("[content] Supabase client unavailable. Check SUPABASE_URL and SUPABASE_ANON_KEY.");
    return [];
  }

  let { data, error } = await supabase
    .from("articles")
    .select(ARTICLE_SELECT_WITH_FEATURED_IMAGE)
    .eq("status", "published")
    .order("published_at", { ascending: false })
    .limit(limit);

  if (error?.message?.includes("featured_image does not exist")) {
    ({ data, error } = await supabase
      .from("articles")
      .select(ARTICLE_SELECT_LEGACY)
      .eq("status", "published")
      .order("published_at", { ascending: false })
      .limit(limit));
  }

  if (error || !data) {
    console.warn("[content] Failed to fetch published articles.", error?.message ?? "No data returned.");
    return [];
  }

  console.info(`[content] Loaded ${data.length} published article(s) from Supabase.`);
  return (data as ArticleRow[]).map(mapRowToWebsiteArticle);
};

export const getPublishedArticleSlugs = async (): Promise<string[]> => {
  const supabase = getSupabaseServerClient();
  if (!supabase) {
    console.warn("[content] Supabase client unavailable while loading article slugs.");
    return [];
  }

  const { data, error } = await supabase
    .from("articles")
    .select("slug")
    .eq("status", "published")
    .order("published_at", { ascending: false });

  if (error || !data) {
    console.warn("[content] Failed to fetch article slugs.", error?.message ?? "No data returned.");
    return [];
  }

  const slugs = data
    .map((entry) => (typeof entry.slug === "string" ? entry.slug : null))
    .filter((value): value is string => value !== null);

  console.info(`[content] Loaded ${slugs.length} published article slug(s) from Supabase.`);
  return slugs;
};

export const getPublishedArticleBySlug = async (
  slug: string,
): Promise<WebsiteArticle | null> => {
  const supabase = getSupabaseServerClient();
  if (!supabase) {
    console.warn(`[content] Supabase client unavailable while loading article slug "${slug}".`);
    return null;
  }

  let { data, error } = await supabase
    .from("articles")
    .select(ARTICLE_SELECT_WITH_FEATURED_IMAGE)
    .eq("status", "published")
    .eq("slug", slug)
    .maybeSingle();

  if (error?.message?.includes("featured_image does not exist")) {
    ({ data, error } = await supabase
      .from("articles")
      .select(ARTICLE_SELECT_LEGACY)
      .eq("status", "published")
      .eq("slug", slug)
      .maybeSingle());
  }

  if (error || !data) {
    console.warn(
      `[content] Failed to fetch article "${slug}".`,
      error?.message ?? "No published row returned.",
    );
    return null;
  }

  console.info(`[content] Loaded article "${slug}" from Supabase.`);
  return mapRowToWebsiteArticle(data as ArticleRow);
};

export const getPublishedArticlesByCategory = async (
  categorySlug: CategorySlug,
  limit = 12,
): Promise<WebsiteArticle[]> => {
  const allArticles = await getPublishedArticles(100);

  return allArticles
    .filter((article) => article.categorySlug === categorySlug)
    .slice(0, limit);
};
