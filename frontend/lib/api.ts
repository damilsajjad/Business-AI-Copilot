import { createClient } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Make an authenticated request to the backend API.
 *
 * Automatically attaches the Supabase JWT token as a Bearer token.
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options.headers as Record<string, string>),
  };

  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  } else if (typeof window !== "undefined" && sessionStorage.getItem("guest_mode") === "true") {
    headers["Authorization"] = `Bearer demo-token`;
  }

  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
}

/**
 * Typed API helper that parses JSON responses.
 */
export async function apiJson<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await apiFetch(path, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: response.statusText,
    }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}
