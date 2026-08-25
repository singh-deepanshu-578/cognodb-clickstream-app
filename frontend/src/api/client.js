import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.error) {
      return Promise.reject(new Error(error.response.data.error));
    }
    if (error.code === "ECONNABORTED") {
      return Promise.reject(new Error("Request timed out. Please try again."));
    }
    return Promise.reject(
      new Error("Could not reach the server. Is the backend running?"),
    );
  },
);

export default client;
