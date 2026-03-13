const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Example of how we might inject Supabase JWT or other auth headers
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    // Attempt to parse standard error payload from FastAPI Backend
    let errorMessage = `API Error: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) errorMessage = errorData.detail;
    } catch (e) {
      // Ignore parsing error, fallback to status text
    }
    throw new Error(errorMessage);
  }

  // Not all endpoints return JSON (e.g., 204 No Content), but standardizing for LeadForge
  return response.json();
}

export const fetchJson = fetchApi;
