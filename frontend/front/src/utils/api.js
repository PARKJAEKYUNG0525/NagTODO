import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
    headers: {
        "ngrok-skip-browser-warning": "true",
    },
});

export const buildFileUrl = (filePath) => filePath;

export default api;