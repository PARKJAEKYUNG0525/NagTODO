import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
    headers: {
        "ngrok-skip-browser-warning": "true",
    },
});

// 정적 파일은 frontend public/에서 같은 origin으로 서빙되므로 상대 경로 그대로 사용
export const buildFileUrl = (filePath) => filePath;

export default api;