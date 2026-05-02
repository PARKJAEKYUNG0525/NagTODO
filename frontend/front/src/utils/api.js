import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
    headers: {
        "ngrok-skip-browser-warning": "true",
    },
});

// ngrok 환경에서 <img>, <audio> 등 브라우저 직접 로드 요청에 헤더를 붙일 수 없으므로
// 쿼리 파라미터로 ngrok 경고 페이지를 우회
export const buildFileUrl = (filePath) => {
    const base = api.defaults.baseURL || '';
    const url = `${base}${filePath}`;
    return base.includes('ngrok') ? `${url}?ngrok-skip-browser-warning=true` : url;
};

export default api;