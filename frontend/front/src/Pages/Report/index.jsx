import React, { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, subMonths, subDays, startOfDay, getDaysInMonth } from "date-fns";
import { ko } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAuth } from "@/hooks/useAuth";
import { useReport } from "@/hooks/useReport";
import { BsFillBellFill } from "react-icons/bs";

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
    const { isLoading, error, reportData, fetchReport } = useReport();

    const [reportMode, setReportMode] = useState("monthly");
    const [analyzed, setAnalyzed] = useState(false);

    // 30일 모드
    const [selectedDate, setSelectedDate] = useState(TODAY);
    const rangeEnd = selectedDate;
    const rangeStart = subMonths(rangeEnd, 1);
    const formatted30DayRange = `${format(rangeStart, "yyyy.MM.dd")} ~ ${format(rangeEnd, "yyyy.MM.dd")}`;

    // 월 단위 모드
    const [selectedYear, setSelectedYear] = useState(TODAY.getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(TODAY.getMonth() + 1);

    // 발행 이력 (추후 백엔드 연동)
    const pastReports = [
        { id: "m-2026-04", type: "monthly", label: "4월", range: "2026.04.01 ~ 2026.04.30" },
        { id: "30-2026-04-21", type: "30days", label: "2026.03.21 ~ 2026.04.21", range: "2026.03.21 ~ 2026.04.21" },
        { id: "m-2026-03", type: "monthly", label: "3월", range: "2026.03.01 ~ 2026.03.31" },
        { id: "30-2026-03-01", type: "30days", label: "2026.02.01 ~ 2026.03.01", range: "2026.02.01 ~ 2026.03.01" },
    ];
    const [selectedReport, setSelectedReport] = useState(null);
    const [isReportDropdownOpen, setIsReportDropdownOpen] = useState(false);

    const resultRange =
        reportMode === "history" && selectedReport
            ? selectedReport.range
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
        setIsReportDropdownOpen(false);
    };

    const handlePastReportSelect = (report) => {
        setSelectedReport(report);
        setIsReportDropdownOpen(false);
        setAnalyzed(true);
    };

    const handleDateSelect = (date) => {
        if (!date) return;
        setSelectedDate(startOfDay(date));
        setAnalyzed(false);
    };

    const handleReselect = () => setAnalyzed(false);

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

    const stats = reportData?.stats;
    const aiReport = reportData?.aiReport;
    const categoryEntries = stats ? Object.entries(stats.category_stats) : [];

    return (
        <>
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">월간 리포트</h1>
                    <button
                        onClick={() => setIsNotiOpen(true)}
                        className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm"
                    >
                        {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
                        <BsFillBellFill className="text-white" size={20} />
                        {/* 알림 도트 */}
                        <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
                    </button>
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
                            <div className="flex-1 relative">
                                <select
                                    value={selectedYear}
                                    onChange={(e) => { setSelectedYear(Number(e.target.value)); setAnalyzed(false); }}
                                    className="w-full bg-white rounded-xl px-4 py-3 text-sm text-[#3D4D5C] shadow-sm appearance-none cursor-pointer"
                                >
                                    {YEARS.map((y) => <option key={y} value={y}>{y}년</option>)}
                                </select>
                                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8B9BAA] text-xs pointer-events-none">▼</span>
                            </div>
                            <div className="flex-1 relative">
                                <select
                                    value={selectedMonth}
                                    onChange={(e) => { setSelectedMonth(Number(e.target.value)); setAnalyzed(false); }}
                                    className="w-full bg-white rounded-xl px-4 py-3 text-sm text-[#3D4D5C] shadow-sm appearance-none cursor-pointer"
                                >
                                    {MONTHS.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
                                </select>
                                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8B9BAA] text-xs pointer-events-none">▼</span>
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
                                    {selectedReport ? selectedReport.label : "--- 선택하세요 ---"}
                                </span>
                                <span className="text-[#8B9BAA] text-xs">▼</span>
                            </button>
                            {isReportDropdownOpen && (
                                <ul className="absolute z-10 left-0 right-0 mt-1 bg-white rounded-xl shadow-lg overflow-hidden max-h-64 overflow-y-auto">
                                    {pastReports.map((report) => (
                                        <li key={report.id}>
                                            <button
                                                type="button"
                                                onClick={() => handlePastReportSelect(report)}
                                                className={`w-full px-4 py-3 text-left text-sm hover:bg-[#EEF2F5] ${selectedReport?.id === report.id ? "bg-[#EEF2F5] font-semibold" : ""} text-[#3D4D5C]`}
                                            >
                                                {report.label}
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

                        {/* 실제 데이터 */}
                        {!isLoading && reportData && !error && (
                            <>
                                {/* 달성률 카드 */}
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
                                        <div className="relative w-24 h-24 shrink-0">
                                            <div className="absolute inset-0 rounded-full border-[10px] border-[#E4EEF3]" />
                                            <div
                                                className="absolute inset-0 rounded-full border-[10px] border-transparent"
                                                style={{ borderTopColor: "#A8C8D8", borderRightColor: "#A8C8D8", transform: "rotate(-45deg)" }}
                                            />
                                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                                <span className="text-base font-bold text-[#3D4D5C]">{stats.user_success_rate}%</span>
                                                <span className="text-[9px] text-[#8B9BAA]">전체</span>
                                            </div>
                                        </div>
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

                                {/* AI 분석 (클러스터) */}
                                <h3 className="mt-6 text-sm font-bold text-[#3D4D5C]">AI 분석</h3>
                                {aiReport.cluster_summaries.length === 0 ? (
                                    <div className="mt-3 bg-[#EEF2F5] rounded-2xl px-4 py-3">
                                        <p className="text-xs text-[#8B9BAA]">분석할 실패 패턴이 충분하지 않습니다.</p>
                                    </div>
                                ) : (
                                    <div className="mt-3 grid grid-cols-2 gap-3">
                                        {aiReport.cluster_summaries.map((cluster) => (
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
                                )}

                                {/* 분석 리포트 */}
                                <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3">
                                    <p className="text-xs font-bold text-[#3D4D5C]">분석 리포트</p>
                                    <div className="mt-2">
                                        <ReportMarkdown content={aiReport.report || "리포트를 생성하지 못했습니다."} />
                                    </div>
                                </div>
                            </>
                        )}

                        {/* 발행 이력 모드 */}
                        {reportMode === "history" && selectedReport && (
                            <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3">
                                <p className="text-xs font-bold text-[#3D4D5C]">분석 리포트</p>
                                <p className="mt-2 text-xs text-[#3D4D5C] leading-5">
                                    이전에 발행된 리포트입니다. (백엔드 연동 예정)
                                </p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </>
    );
}
