import { useState } from "react";
import axios from "axios";
import api from "../utils/api";

const aiApi = axios.create({
    baseURL: import.meta.env.VITE_AI_URL || "http://localhost:8081",
    timeout: 120_000, // Ollama LLM 생성 시간 고려
});

export function useReport() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [reportData, setReportData] = useState(null);

    const fetchReport = async ({ userId, monthStart, monthEnd, year, month }) => {
        setIsLoading(true);
        setError(null);
        setReportData(null);

        const aiBody =
            year != null
                ? { user_id: String(userId), year, month }
                : { user_id: String(userId), month_start: monthStart, month_end: monthEnd };

        try {
            const [statsRes, aiRes] = await Promise.all([
                api.get("/todos/stats", {
                    params: { user_id: userId, month_start: monthStart, month_end: monthEnd },
                }),
                aiApi.post("/ai/report/monthly", aiBody),
            ]);
            setReportData({ stats: statsRes.data, aiReport: aiRes.data });
        } catch (e) {
            setError(e.response?.data?.detail || "리포트 생성에 실패했습니다");
        } finally {
            setIsLoading(false);
        }
    };

    return { isLoading, error, reportData, fetchReport };
}
