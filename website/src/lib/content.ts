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

const FALLBACK_IMAGES: Record<CategorySlug, string> = {
  "personal-finance":
    "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200",
  "home-improvement":
    "https://images.unsplash.com/photo-1493666438817-866a91353ca9?auto=format&fit=crop&q=80&w=1200",
  "health-wellness":
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&q=80&w=1200",
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
      FALLBACK_IMAGES[categorySlug],
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
