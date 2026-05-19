const BASE_URL = "http://localhost:8000";

async function request(
  endpoint,
  { method = "GET", body = null, auth = true } = {},
) {
  const headers = {};

  if (body) {
    headers["Content-Type"] = "application/json";
  }

  if (auth) {
    const token = localStorage.getItem("token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Произошла ошибка");
  }

  return data;
}

const api = {
  get: (endpoint) => request(endpoint),
  post: (endpoint, body) => request(endpoint, { method: "POST", body }),
  patch: (endpoint, body) => request(endpoint, { method: "PATCH", body }),
  delete: (endpoint) => request(endpoint, { method: "DELETE" }),

  login: (body) =>
    request("/auth/login", { method: "POST", body, auth: false }),
  register: (body) =>
    request("/auth/register", { method: "POST", body, auth: false }),
};

export default api;
