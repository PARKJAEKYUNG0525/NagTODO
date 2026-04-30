import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
    headers: {
        "ngrok-skip-browser-warning": "true",
    },
});

// 쿠키는 HttpOnly이므로 withCredentials로 자동 전송됨 (별도 인터셉터 불필요)

export default api;