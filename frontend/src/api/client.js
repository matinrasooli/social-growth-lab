const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("sgl_token");
}

export function setToken(token) {
  if (token) localStorage.setItem("sgl_token", token);
  else localStorage.removeItem("sgl_token");
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";

  const resp = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await resp.json();
  } catch {
    data = null;
  }

  if (!resp.ok) {
    const error = new Error(
      (data && data.detail && (data.detail.message || data.detail)) || `Request failed (${resp.status})`
    );
    error.status = resp.status;
    error.detail = data ? data.detail : null;
    throw error;
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  postForm: (path, formData) => request(path, { method: "POST", body: formData, isForm: true }),
};

export { API_BASE };
