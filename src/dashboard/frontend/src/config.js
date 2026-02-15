/**
 * API base URL. In production (e.g. Render), set VITE_API_URL to your backend URL.
 * Example: https://your-backend.onrender.com
 */
const API_BASE =
  (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "") +
  "/api";

export { API_BASE };
