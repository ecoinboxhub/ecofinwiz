import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8105/api/v1";

const client = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken && error.config?.url !== "/auth/refresh") {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken });
          localStorage.setItem("access_token", data.access_token);
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return client(error.config);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
