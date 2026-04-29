import { useState } from "react";
import axios from "axios";
import api from "../utils/api";

const aiApi = axios.create({
    baseURL: import.meta.env.VITE_AI_URL || "http://localhost:8000",
    timeout: 120_000,
});

export function useReport() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [reportData, setReportData] = useState(null);
    const [savedReports, setSavedReports] = useState([]);

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
            const data = { stats: statsRes.data, aiReport: aiRes.data };
            setReportData(data);

            // 생성된 리포트를 백엔드에 저장 (실패해도 결과 표시는 유지)
            await _saveReport({ userId, monthStart, monthEnd, aiReport: aiRes.data });

            return data;
        } catch (e) {
            setError(e.response?.data?.detail || "리포트 생성에 실패했습니다");
        } finally {
            setIsLoading(false);
        }
    };

    const _saveReport = async ({ userId, monthStart, monthEnd, aiReport }) => {
        try {
            await api.post("/reports/", {
                title: `월간 리포트 ${monthStart} ~ ${monthEnd}`,
                date: new Date().toISOString(),
                detail: JSON.stringify({
                    report: aiReport.report,
                    cluster_summaries: aiReport.cluster_summaries,
                    category_stats: aiReport.category_stats,
                }),
                user_id: userId,
                month_start: monthStart,
                month_end: monthEnd,
            });
        } catch (e) {
            console.warn("리포트 저장 실패:", e);
        }
    };

    const fetchSavedReports = async (userId) => {
        try {
            const res = await api.get("/reports/", { params: { user_id: userId } });
            setSavedReports(res.data);
        } catch (e) {
            console.warn("저장된 리포트 조회 실패:", e);
        }
    };

    return { isLoading, error, reportData, savedReports, fetchReport, fetchSavedReports };
}
