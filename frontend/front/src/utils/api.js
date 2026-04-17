import axios from "axios";

// axios : http 요청 쉽게 보낼 수 있는 라이브러리
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    // 쿠키 자동 전송
    withCredentials: true,
});

export default api;