import React, { useState, useEffect } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, subMonths, subDays, startOfDay, getDaysInMonth } from "date-fns";
import { ko } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import NotificationModal from "../../Components/Modal/NotificationModal";
import remarkGfm from "remark-gfm";
import { useAuth } from "@/hooks/useAuth";
import { useReport } from "@/hooks/useReport";
import api from "@/utils/api.js";
import { useImg } from "@/hooks/useImg";
import { BsFillBellFill } from "react-icons/bs";
import { useNotification } from "@/hooks/useNotification";

const CATEGORY_COLORS = ["#E89B9B", "#F4D58A", "#A8D5B4", "#A8C8D8", "#C5A8D8", "#D8A8C5", "#D4B896"];
const YEARS = [2024, 2025, 2026];
const MONTHS = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"];

const getCategoryColor = (idx) => CATEGORY_COLORS[idx % CATEGORY_COLORS.length];

function ReportMarkdown({ content }) {
    return (
        <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
                h1: ({ children }) => <h1 className="mt-4 text-base font-bold text-[#3D4D5C] first:mt-0">{children}</h1>,
                h2: ({ children }) => <h2 className="mt-4 text-sm font-bold text-[#3D4D5C] first:mt-0">{children}</h2>,
                h3: ({ children }) => <h3 className="mt-3 text-xs font-bold text-[#3D4D5C] first:mt-0">{children}</h3>,
                p: ({ children }) => <p className="mt-2 text-xs text-[#3D4D5C] leading-5 first:mt-0">{children}</p>,
                ul: ({ children }) => <ul className="mt-2 list-disc pl-5 text-xs text-[#3D4D5C] first:mt-0">{children}</ul>,
                ol: ({ children }) => <ol className="mt-2 list-decimal pl-5 text-xs text-[#3D4D5C] first:mt-0">{children}</ol>,
                li: ({ children }) => <li className="mt-1 leading-5">{children}</li>,
                strong: ({ children }) => <strong className="font-bold text-[#2C3946]">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
                blockquote: ({ children }) => (
                    <blockquote className="mt-3 border-l-4 border-[#A8C8D8] pl-3 text-xs text-[#4A5C6E]">
                        {children}
                    </blockquote>
                ),
                code: ({ children }) => (
                    <code className="rounded bg-white px-1 py-0.5 text-[11px] text-[#3D4D5C]">{children}</code>
                ),
            }}
        >
            {content}
        </ReactMarkdown>
    );
}

export default function MonthlyReport() {
    const TODAY = startOfDay(new Date());
    const { user } = useAuth();
    const { isLoading, error, reportData, savedReports, fetchReport, fetchSavedReports } = useReport();
    const { notifications } = useNotification();

    const { currentBg, getUserBg } = useImg();
    useEffect(() => { getUserBg(); }, []);

    const [reportMode, setReportMode] = useState("monthly");
    const [analyzed, setAnalyzed] = useState(false);
    const [isNotiOpen, setIsNotiOpen] = useState(false);

    // 30일 모드
    const [selectedDate, setSelectedDate] = useState(TODAY);
    const rangeEnd = selectedDate;
    const rangeStart = subMonths(rangeEnd, 1);
    const formatted30DayRange = `${format(rangeStart, "yyyy.MM.dd")} ~ ${format(rangeEnd, "yyyy.MM.dd")}`;

    // 월 단위 모드
    const [selectedYear, setSelectedYear] = useState(TODAY.getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(TODAY.getMonth() + 1);

    // 월 단위 드롭다운
    const [isYearDropdownOpen, setIsYearDropdownOpen] = useState(false);
    const [isMonthDropdownOpen, setIsMonthDropdownOpen] = useState(false);

    // 발행 이력 모드
    const [selectedReport, setSelectedReport] = useState(null);
    const [selectedReportDetail, setSelectedReportDetail] = useState(null);
    const [isReportDropdownOpen, setIsReportDropdownOpen] = useState(false);

    const handleNotification = () => setIsNotiOpen(true);

    // 발행 이력 탭 진입 시 저장된 리포트 로드
    useEffect(() => {
        if (reportMode === "history" && user) {
            fetchSavedReports(user.user_id);
        }
    }, [reportMode, user]);

    const formatDateRange = (start, end) =>
        `${(start || "").replace(/-/g, ".")} ~ ${(end || "").replace(/-/g, ".")}`;

    const resultRange =
        reportMode === "history" && selectedReport
            ? formatDateRange(selectedReport.month_start, selectedReport.month_end)
            : reportMode === "30days"
                ? formatted30DayRange
                : (() => {
                    const days = getDaysInMonth(new Date(selectedYear, selectedMonth - 1));
                    const mm = String(selectedMonth).padStart(2, "0");
                    return `${selectedYear}.${mm}.01 ~ ${selectedYear}.${mm}.${String(days).padStart(2, "0")}`;
                })();

    const handleTabChange = (mode) => {
        if (mode === reportMode) return;
        setReportMode(mode);
        setAnalyzed(false);
        setSelectedReport(null);
        setSelectedReportDetail(null);
        setIsReportDropdownOpen(false);
        setIsYearDropdownOpen(false);
        setIsMonthDropdownOpen(false);
    };

    const handlePastReportSelect = (report) => {
        setSelectedReport(report);
        setIsReportDropdownOpen(false);
        setAnalyzed(true);
        try {
            setSelectedReportDetail(JSON.parse(report.detail));
        } catch {
            setSelectedReportDetail(null);
        }
    };

    const handleDateSelect = (date) => {
        if (!date) return;
        setSelectedDate(startOfDay(date));
        setAnalyzed(false);
    };

    const handleReselect = () => {
        setAnalyzed(false);
        setSelectedReport(null);
        setSelectedReportDetail(null);
    };

    const handleAnalyze = async () => {
        if (!user) return;
        setAnalyzed(true);

        if (reportMode === "30days") {
            await fetchReport({
                userId: user.user_id,
                monthStart: format(rangeStart, "yyyy-MM-dd"),
                monthEnd: format(rangeEnd, "yyyy-MM-dd"),
            });
        } else if (reportMode === "monthly") {
            const daysInMonth = getDaysInMonth(new Date(selectedYear, selectedMonth - 1));
            await fetchReport({
                userId: user.user_id,
                year: selectedYear,
                month: selectedMonth,
                monthStart: format(new Date(selectedYear, selectedMonth - 1, 1), "yyyy-MM-dd"),
                monthEnd: format(new Date(selectedYear, selectedMonth - 1, daysInMonth), "yyyy-MM-dd"),
            });
        }
    };

    // 공용 UI: 상단 벨 버튼
    const NotificationBell = () => (
        <button
            onClick={handleNotification}
            className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
        >
            <BsFillBellFill className="w-5 h-5 text-white" />

            {notifications.length > 0 && (
                <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
            )}
        </button>
    );

    return (
        <div className="flex-1 flex flex-col bg-[#F4F7FA] bg-cover bg-center"
             style={
                 currentBg
                     ? {
                         backgroundImage: `linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url(${api.defaults.baseURL}${currentBg.file_url})`,
                     }
                     : undefined
             }
        >
            {/* 상단 헤더 (알림 벨) */}
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">월간 리포트</h1>
                <NotificationBell />
            </header>

            <div className="flex-1 overflow-y-auto px-6 pt-6 pb-4">
                {/* 탭 토글 */}
                <div className="flex flex-col gap-2">
                    <div className="flex gap-2">
                        <button
                            onClick={() => handleTabChange("monthly")}
                            className={`px-4 py-2 rounded-full text-xs whitespace-nowrap ${reportMode === "monthly" ? "bg-[#A8C8D8] font-bold text-white" : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"}`}
                        >
                            월 단위 리포트 보기
                        </button>
                        <button
                            onClick={() => handleTabChange("30days")}
                            className={`px-4 py-2 rounded-full text-xs whitespace-nowrap ${reportMode === "30days" ? "bg-[#A8C8D8] font-bold text-white" : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"}`}
                        >
                            최근 30일 리포트 보기
                        </button>
                    </div>
                    <button
                        onClick={() => handleTabChange("history")}
                        className={`w-full py-2 rounded-full text-xs ${reportMode === "history" ? "bg-[#A8C8D8] font-bold text-white" : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"}`}
                    >
                        발행했던 리포트 보기
                    </button>
                </div>

                {/* 월 단위 뷰 */}
                {reportMode === "monthly" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            분석할 <span className="text-[#E89B9B] font-semibold">년/월</span>을 선택하세요
                        </p>
                        <div className="mt-3 flex gap-3">
                            {/* 연도 커스텀 드롭다운 */}
                            <div className="flex-1 relative">
                                <button
                                    type="button"
                                    onClick={() => { setIsYearDropdownOpen((v) => !v); setIsMonthDropdownOpen(false); }}
                                    className="w-full bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                                >
                                    <span>{selectedYear}년</span>
                                    <span className="text-[#8B9BAA] text-xs">▼</span>
                                </button>
                                {isYearDropdownOpen && (
                                    <ul className="absolute z-20 left-0 right-0 mt-1 bg-white rounded-xl shadow-lg overflow-hidden">
                                        {YEARS.map((y) => (
                                            <li key={y}>
                                                <button
                                                    type="button"
                                                    onClick={() => { setSelectedYear(y); setAnalyzed(false); setIsYearDropdownOpen(false); }}
                                                    className={`w-full px-4 py-3 text-left text-sm hover:bg-[#EEF2F5] text-[#3D4D5C] ${selectedYear === y ? "bg-[#EEF2F5] font-semibold" : ""}`}
                                                >
                                                    {y}년
                                                </button>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            {/* 월 커스텀 드롭다운 */}
                            <div className="flex-1 relative">
                                <button
                                    type="button"
                                    onClick={() => { setIsMonthDropdownOpen((v) => !v); setIsYearDropdownOpen(false); }}
                                    className="w-full bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                                >
                                    <span>{selectedMonth}월</span>
                                    <span className="text-[#8B9BAA] text-xs">▼</span>
                                </button>
                                {isMonthDropdownOpen && (
                                    <ul className="absolute z-20 left-0 right-0 mt-1 bg-white rounded-xl shadow-lg overflow-hidden max-h-48 overflow-y-auto">
                                        {MONTHS.map((m, i) => (
                                            <li key={i + 1}>
                                                <button
                                                    type="button"
                                                    onClick={() => { setSelectedMonth(i + 1); setAnalyzed(false); setIsMonthDropdownOpen(false); }}
                                                    className={`w-full px-4 py-3 text-left text-sm hover:bg-[#EEF2F5] text-[#3D4D5C] ${selectedMonth === i + 1 ? "bg-[#EEF2F5] font-semibold" : ""}`}
                                                >
                                                    {m}
                                                </button>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                        <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3 flex items-start gap-2">
                            <span className="text-[#F4D58A] text-sm">💡</span>
                            <p className="text-xs text-[#3D4D5C]">선택한 달의 1일부터 말일까지의 할 일 달성률을 분석합니다.</p>
                        </div>
                    </>
                )}

                {/* 발행 이력 뷰 */}
                {reportMode === "history" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            <span className="text-[#E89B9B] font-semibold">다시 열람</span>하고 싶은 리포트를 선택하세요
                        </p>
                        <div className="mt-3 relative">
                            <button
                                type="button"
                                onClick={() => setIsReportDropdownOpen((v) => !v)}
                                className="w-full bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm shadow-sm"
                            >
                                <span className={selectedReport ? "text-[#3D4D5C]" : "text-[#8B9BAA]"}>
                                    {selectedReport
                                        ? formatDateRange(selectedReport.month_start, selectedReport.month_end)
                                        : savedReports.length === 0 ? "저장된 리포트가 없습니다" : "--- 선택하세요 ---"}
                                </span>
                                <span className="text-[#8B9BAA] text-xs">▼</span>
                            </button>
                            {isReportDropdownOpen && savedReports.length > 0 && (
                                <ul className="absolute z-10 left-0 right-0 mt-1 bg-white rounded-xl shadow-lg overflow-hidden max-h-64 overflow-y-auto">
                                    {savedReports.map((report) => (
                                        <li key={report.report_id}>
                                            <button
                                                type="button"
                                                onClick={() => handlePastReportSelect(report)}
                                                className={`w-full px-4 py-3 text-left text-sm hover:bg-[#EEF2F5] ${selectedReport?.report_id === report.report_id ? "bg-[#EEF2F5] font-semibold" : ""} text-[#3D4D5C]`}
                                            >
                                                {formatDateRange(report.month_start, report.month_end)}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </>
                )}

                {/* 최근 30일 뷰 */}
                {reportMode === "30days" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            30일 기준의 <span className="text-[#E89B9B] font-semibold">마지막 날짜</span>를 선택하세요
                        </p>
                        <div className="mt-3 bg-white rounded-2xl p-4 shadow-sm">
                            <Calendar
                                mode="single"
                                selected={selectedDate}
                                onSelect={handleDateSelect}
                                locale={ko}
                                showOutsideDays={false}
                                disabled={{ after: TODAY }}
                                modifiers={{ inRange: { from: rangeStart, to: subDays(rangeEnd, 1) } }}
                                modifiersClassNames={{ inRange: "bg-[#D9DFE4] text-[#3D4D5C] rounded-full" }}
                                className="w-full"
                            />
                        </div>
                        <div className="mt-4 bg-[#4A5C6E] rounded-xl py-3 flex items-center justify-center">
                            <span className="text-white text-sm font-semibold">{formatted30DayRange}</span>
                        </div>
                        <div className="mt-3 bg-[#DEE4EA] rounded-xl px-4 py-3 flex items-start gap-2">
                            <span className="text-[#F4D58A] text-sm">💡</span>
                            <p className="text-xs text-[#3D4D5C] leading-5">
                                선택한 날로부터 한 달 전까지의 루틴을 분석합니다.<br />
                                예: 2026.04.21 선택 → 2026.03.21 ~ 2026.04.21
                            </p>
                        </div>
                    </>
                )}

                {/* 분석하기 버튼 */}
                {reportMode !== "history" && (
                    <button
                        onClick={handleAnalyze}
                        disabled={isLoading}
                        className="mt-6 w-full py-4 rounded-2xl bg-[#B4D0DB] text-white font-bold text-sm disabled:opacity-60"
                    >
                        {isLoading ? "분석 중..." : "분석하기"}
                    </button>
                )}

                {/* 분석 결과 */}
                {analyzed && (
                    <>
                        <div className="mt-6 flex items-center justify-between">
                            <h2 className="text-sm font-bold text-[#3D4D5C]">{resultRange}</h2>
                            <button
                                onClick={handleReselect}
                                className="px-3 py-1.5 rounded-full bg-[#4A5C6E] text-[11px] text-white font-medium"
                            >
                                다시 선택
                            </button>
                        </div>

                        {/* 로딩 */}
                        {isLoading && (
                            <div className="mt-8 flex flex-col items-center gap-3 py-8">
                                <div className="animate-spin rounded-full h-10 w-10 border-4 border-[#A8C8D8] border-t-transparent" />
                                <p className="text-xs text-[#8B9BAA]">AI 리포트를 생성하는 중입니다…</p>
                                <p className="text-[10px] text-[#8B9BAA]">최대 1~2분 소요될 수 있습니다</p>
                            </div>
                        )}

                        {/* 에러 */}
                        {!isLoading && error && (
                            <div className="mt-4 bg-[#FDECEA] rounded-xl px-4 py-3">
                                <p className="text-xs text-[#E89B9B] font-medium">리포트 생성 실패</p>
                                <p className="mt-1 text-xs text-[#E89B9B]">{error}</p>
                            </div>
                        )}

                        {/* 신규 생성 결과 */}
                        {!isLoading && reportData && !error && reportMode !== "history" && (
                            <ReportContent
                                stats={reportData.stats}
                                clusters={reportData.aiReport.cluster_summaries}
                                reportText={reportData.aiReport.report}
                            />
                        )}

                        {/* 발행 이력 모드 - 저장된 리포트 표시 */}
                        {reportMode === "history" && selectedReport && selectedReportDetail && (
                            <ReportContent
                                stats={selectedReportDetail.stats}
                                clusters={selectedReportDetail.cluster_summaries}
                                reportText={selectedReportDetail.report}
                            />
                        )}
                        {reportMode === "history" && selectedReport && !selectedReportDetail && (
                            <div className="mt-4 bg-[#FDECEA] rounded-xl px-4 py-3">
                                <p className="text-xs text-[#E89B9B]">리포트 데이터를 불러올 수 없습니다.</p>
                            </div>
                        )}
                    </>
                )}
            </div>
            <NotificationModal
                isOpen={isNotiOpen}
                onClose={() => setIsNotiOpen(false)}
                notifications={notifications}
            />
        </div>
    );
}

function ReportContent({ stats, clusters, reportText }) {
    const categoryEntries = stats ? Object.entries(stats.category_stats || {}) : [];

    return (
        <>
            {/* 달성률 카드 */}
            {stats && (
                <>
                    <div className="mt-3 grid grid-cols-2 gap-3">
                        <div className="bg-white rounded-2xl p-4 shadow-sm">
                            <p className="text-[11px] text-[#8B9BAA]">내 달성률</p>
                            <p className="mt-2 text-3xl font-bold text-[#A8C8D8]">{stats.user_success_rate}%</p>
                        </div>
                        <div className="bg-white rounded-2xl p-4 shadow-sm">
                            <p className="text-[11px] text-[#8B9BAA]">전체 사용자 달성률</p>
                            <p className="mt-2 text-3xl font-bold text-[#A8C8D8]">{stats.all_users_success_rate}%</p>
                        </div>
                    </div>

                    {/* 카테고리별 달성률 */}
                    <div className="mt-4 bg-white rounded-2xl p-4 shadow-sm">
                        <h3 className="text-sm font-bold text-[#3D4D5C]">카테고리별 달성률</h3>
                        <div className="mt-4 flex items-center gap-4">
                            <DonutChart categoryEntries={categoryEntries} overallRate={stats.user_success_rate} />
                            <div className="flex-1 flex flex-col gap-2 text-xs">
                                {categoryEntries.length === 0 ? (
                                    <p className="text-[#8B9BAA]">카테고리 데이터 없음</p>
                                ) : (
                                    categoryEntries.map(([name, data], idx) => (
                                        <div key={name} className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: getCategoryColor(idx) }} />
                                                <span className="text-[#3D4D5C]">{name}</span>
                                            </div>
                                            <span className="text-[#8B9BAA]">{data.rate}%</span>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* AI 분석 (클러스터) */}
            <h3 className="mt-6 text-sm font-bold text-[#3D4D5C]">AI 분석</h3>
            <ClusterGrid clusters={clusters} />

            {/* 분석 리포트 */}
            <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3">
                <p className="text-xs font-bold text-[#3D4D5C]">분석 리포트</p>
                <div className="mt-2">
                    <ReportMarkdown content={reportText || "리포트 내용이 없습니다."} />
                </div>
            </div>
        </>
    );
}

function DonutChart({ categoryEntries, overallRate }) {
    const [tooltip, setTooltip] = useState(null);

    const SIZE = 128;
    const CX = SIZE / 2;
    const CY = SIZE / 2;
    const R_OUTER = 60;
    const R_INNER = 38;

    const totalRate = categoryEntries.reduce((sum, [, data]) => sum + (data.rate || 0), 0);

    if (categoryEntries.length === 0 || totalRate === 0) {
        return (
            <div className="relative w-32 h-32 shrink-0 rounded-full bg-[#E4EEF3] flex items-center justify-center">
                <div className="w-[60%] h-[60%] rounded-full bg-white flex flex-col items-center justify-center">
                    <span className="text-base font-bold text-[#3D4D5C]">{overallRate}%</span>
                    <span className="text-[9px] text-[#8B9BAA]">전체</span>
                </div>
            </div>
        );
    }

    const polar = (r, deg) => {
        const rad = (deg - 90) * (Math.PI / 180);
        return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
    };

    const arcPath = (startDeg, endDeg) => {
        const s = polar(R_OUTER, startDeg);
        const e = polar(R_OUTER, endDeg);
        const si = polar(R_INNER, endDeg);
        const ei = polar(R_INNER, startDeg);
        const large = endDeg - startDeg > 180 ? 1 : 0;
        return `M${s.x},${s.y} A${R_OUTER},${R_OUTER} 0 ${large} 1 ${e.x},${e.y} L${si.x},${si.y} A${R_INNER},${R_INNER} 0 ${large} 0 ${ei.x},${ei.y} Z`;
    };

    let cumDeg = 0;
    const segments = categoryEntries
        .map(([name, data], idx) => {
            const deg = (data.rate / totalRate) * 360;
            if (deg === 0) return null;
            const seg = { name, rate: data.rate, idx, startDeg: cumDeg, endDeg: cumDeg + deg };
            cumDeg += deg;
            return seg;
        })
        .filter(Boolean);

    return (
        <div className="relative w-32 h-32 shrink-0">
            <svg width={SIZE} height={SIZE}>
                {segments.map(({ name, rate, idx, startDeg, endDeg }) => (
                    <path
                        key={name}
                        d={arcPath(startDeg, endDeg)}
                        fill={getCategoryColor(idx)}
                        onMouseEnter={() => setTooltip({ name, rate })}
                        onMouseLeave={() => setTooltip(null)}
                        className="cursor-pointer"
                    />
                ))}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-base font-bold text-[#3D4D5C]">{overallRate}%</span>
                <span className="text-[9px] text-[#8B9BAA]">전체</span>
            </div>
            {tooltip && (
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-[#3D4D5C] text-white text-[10px] px-2 py-1 rounded-lg whitespace-nowrap z-10 pointer-events-none">
                    {tooltip.name} {tooltip.rate}%
                </div>
            )}
        </div>
    );
}

function ClusterGrid({ clusters }) {
    if (!clusters || clusters.length === 0) {
        return (
            <div className="mt-3 bg-[#EEF2F5] rounded-2xl px-4 py-3">
                <p className="text-xs text-[#8B9BAA]">분석할 실패 패턴이 충분하지 않습니다.</p>
            </div>
        );
    }
    return (
        <div className="mt-3 grid grid-cols-2 gap-3">
            {clusters.map((cluster) => (
                <div key={cluster.cluster_id} className="bg-white rounded-2xl p-3 shadow-sm">
                    <span className="inline-block px-2 py-0.5 rounded-full bg-[#EEF2F5] text-[10px] text-[#3D4D5C]">
                        {cluster.dominant_category}
                    </span>
                    <p className="mt-2 text-xs text-[#3D4D5C] font-medium">{cluster.size}개 실패 task</p>
                    {cluster.sample_texts[0] && (
                        <p className="mt-1 text-[10px] text-[#8B9BAA] line-clamp-2">{cluster.sample_texts[0]}</p>
                    )}
                </div>
            ))}
        </div>
    );
}
