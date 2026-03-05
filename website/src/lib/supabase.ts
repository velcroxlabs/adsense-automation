import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let cachedClient: SupabaseClient | null | undefined;

const getEnv = (key: string): string | undefined => {
  const fromAstro = import.meta.env[key];
  if (typeof fromAstro === "string" && fromAstro.length > 0) {
    return fromAstro;
  }

  const fromProcess = process.env[key];
  if (typeof fromProcess === "string" && fromProcess.length > 0) {
    return fromProcess;
  }

  return undefined;
};

export const getSupabaseServerClient = (): SupabaseClient | null => {
  if (cachedClient !== undefined) {
    return cachedClient;
  }

  const url = getEnv("SUPABASE_URL");
  const anonKey = getEnv("SUPABASE_ANON_KEY");

  if (!url || !anonKey) {
    cachedClient = null;
    return cachedClient;
  }

  cachedClient = createClient(url, anonKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });

  return cachedClient;
};
