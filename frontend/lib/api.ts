const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function apiUpload(path: string, formData: FormData) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// Auth
export const auth = {
  demoLogin: () => apiFetch('/api/auth/login/demo', { method: 'POST' }),
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    return fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    }).then(r => r.json());
  },
  me: () => apiFetch('/api/auth/me'),
};

// Advisor
export const advisor = {
  personas: () => apiFetch('/api/advisor/personas'),
  start: (persona?: string) => apiFetch('/api/advisor/start', { method: 'POST', body: JSON.stringify({ persona }) }),
  message: (conversation_id: string, message: string) =>
    apiFetch('/api/advisor/message', { method: 'POST', body: JSON.stringify({ conversation_id, message }) }),
  conversation: (id: string) => apiFetch(`/api/advisor/conversation/${id}`),
};

// Recommendations
export const recommendations = {
  generate: (body: Record<string, unknown>) =>
    apiFetch('/api/recommendations/generate', { method: 'POST', body: JSON.stringify(body) }),
};

// Products
export const products = {
  list: () => apiFetch('/api/products/'),
};

// Quotes
export const quotes = {
  create: (body: Record<string, unknown>) =>
    apiFetch('/api/quotes/', { method: 'POST', body: JSON.stringify(body) }),
  get: (id: string) => apiFetch(`/api/quotes/${id}`),
  accept: (id: string) => apiFetch(`/api/quotes/${id}/accept`, { method: 'PATCH' }),
  list: () => apiFetch('/api/quotes/'),
};

// Orders
export const orders = {
  create: (body: Record<string, unknown>) =>
    apiFetch('/api/orders/', { method: 'POST', body: JSON.stringify(body) }),
  get: (id: string) => apiFetch(`/api/orders/${id}`),
  list: () => apiFetch('/api/orders/'),
};

// KYC
export const kyc = {
  consent: (body: Record<string, unknown>) =>
    apiFetch('/api/kyc/consent', { method: 'POST', body: JSON.stringify(body) }),
  upload: (formData: FormData) => apiUpload('/api/kyc/upload', formData),
  verify: (submissionId: string) =>
    apiFetch(`/api/kyc/submissions/${submissionId}/verify`, { method: 'POST' }),
  getSubmission: (id: string) => apiFetch(`/api/kyc/submissions/${id}`),
};

// Analytics & Leads (back-office)
export const leads = {
  list: (params?: Record<string, string>) => apiFetch('/api/leads/?' + new URLSearchParams(params || {}).toString()),
  funnel: () => apiFetch('/api/leads/funnel'),
  segments: () => apiFetch('/api/leads/analytics/segments'),
  sources: () => apiFetch('/api/leads/analytics/sources'),
  dropReasons: () => apiFetch('/api/leads/analytics/drop-reasons'),
  gstin: () => apiFetch('/api/leads/analytics/gstin'),
  highIntent: () => apiFetch('/api/leads/high-intent'),
  abandonedQuotes: () => apiFetch('/api/leads/abandoned-quotes'),
};

export const analytics = {
  overview: () => apiFetch('/api/analytics/overview'),
  bundlePopularity: () => apiFetch('/api/analytics/bundle-popularity'),
  churn: () => apiFetch('/api/analytics/churn-analysis'),
  nps: () => apiFetch('/api/analytics/nps-distribution'),
};
