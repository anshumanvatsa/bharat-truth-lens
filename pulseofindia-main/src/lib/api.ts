// ── Shared API utility for all backend calls ─────────────────────────────────
// Reads VITE_API_URL from env — falls back to localhost for dev

const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const API_BASE = BASE;

// ── Backend wake-up helper ────────────────────────────────────────────────────
// Render free tier sleeps after 15min inactivity. Wake it up before user submits.
let _wakeupPromise: Promise<boolean> | null = null;

export async function wakeBackend(): Promise<boolean> {
  if (_wakeupPromise) return _wakeupPromise;
  _wakeupPromise = (async () => {
    try {
      const r = await fetch(`${BASE}/health`, { signal: AbortSignal.timeout(70000) });
      return r.ok;
    } catch {
      return false;
    } finally {
      // Reset after 5 minutes so next visit re-checks
      setTimeout(() => { _wakeupPromise = null; }, 5 * 60 * 1000);
    }
  })();
  return _wakeupPromise;
}

// ── Auth token helpers ────────────────────────────────────────────────────────

export function getToken(): string | null {
  try {
    const raw = localStorage.getItem("pulse_user");
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.access_token ?? null;
  } catch {
    return null;
  }
}

export function saveUser(data: { access_token: string; token_type: string }) {
  localStorage.setItem("pulse_user", JSON.stringify(data));
}

export function clearUser() {
  localStorage.removeItem("pulse_user");
  localStorage.removeItem("pulse_profile");
}

export function saveProfile(profile: Record<string, unknown>) {
  localStorage.setItem("pulse_profile", JSON.stringify(profile));
}

export function getProfile(): Record<string, unknown> | null {
  try {
    const raw = localStorage.getItem("pulse_profile");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function isLoggedIn(): boolean {
  return Boolean(getToken());
}

// ── Authenticated fetch helper ────────────────────────────────────────────────

export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  return fetch(`${BASE}${path}`, { ...options, headers });
}

// ── Auth API ──────────────────────────────────────────────────────────────────

export async function apiSignup(payload: {
  full_name: string;
  email: string;
  password: string;
  age_group: string;
  state: string;
}) {
  const res = await apiFetch("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Signup failed");
  return data;
}

export async function apiLogin(email: string, password: string) {
  const form = new FormData();
  form.append("username", email);
  form.append("password", password);

  // OAuth2PasswordRequestForm requires form-encoded body — no Content-Type header
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers,
    body: form,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Login failed");
  return data;
}

export async function apiGetMe() {
  const res = await apiFetch("/auth/me");
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

// ── Voting API ────────────────────────────────────────────────────────────────

export async function apiGetCandidates() {
  const res = await fetch(`${BASE}/vote/pm/candidates`);
  return res.json();
}

export async function apiGetMyVote() {
  const res = await apiFetch("/vote/pm/my-vote");
  if (!res.ok) return { has_voted: false, candidate_id: null };
  return res.json();
}

export async function apiCastVote(candidate_id: string) {
  const res = await apiFetch("/vote/pm", {
    method: "POST",
    body: JSON.stringify({ candidate_id }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Vote failed");
  return data;
}

export async function apiGetResults() {
  const res = await fetch(`${BASE}/vote/pm/results`);
  return res.json();
}

export async function apiGetStates() {
  const res = await fetch(`${BASE}/vote/states`);
  return res.json();
}
