import React, { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, subMonths, subDays, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";

/**
 * MonthlyReport 화면 (통합본)
 * 한 파일에서 3가지 뷰를 상태로 전환합니다.
 *
 *  [1] 월 단위 리포트 보기 (기본)
 *  [2] 최근 30일 리포트 보기 (shadcn/ui Calendar + date-fns)
 *  [3] 분석 결과 (analyzed === true 일 때 아래로 스크롤 이어 노출)
 *
 *  [2] 30일 뷰 동작:
 *      - 달력에서 선택한 날짜를 "끝 날짜" 로 하고,
 *        그 달 전 같은 날 (subMonths(selectedDate, 1)) 을 "시작 날짜" 로 잡습니다.
 *        예) 2026-04-21 선택 → 2026-03-21 ~ 2026-04-21
 *      - 범위 내(=시작 ~ 선택일 전날) 셀은 연회색 배경.
 *      - 선택 셀은 shadcn 의 기본 selected 스타일 (teal) → 다른 배경색.
 *      - 미래 날짜는 disabled.
 *
 * ※ 9:16 프레임 / 하단 Navbar 는 App.jsx 담당.
 * ※ shadcn/ui Calendar: npx shadcn-ui@latest add calendar
 * ※ date-fns: npm i date-fns
 */
export default function MonthlyReport() {
    const [reportMode, setReportMode] = useState("monthly"); // "monthly" | "30days" | "history"
    const [analyzed, setAnalyzed] = useState(false);

    // 진짜 "오늘" (자정 기준). 매 렌더마다 현재 시각을 반영.
    const TODAY = startOfDay(new Date());
    const [selectedDate, setSelectedDate] = useState(TODAY);

    // 발행 이력 (목데이터). 추후 백엔드에서 받아옴.
    const pastReports = [
        {
            id: "m-2026-04",
            type: "monthly",
            label: "4월",
            range: "2026.04.01 ~ 2026.04.30",
        },
        {
            id: "30-2026-04-21",
            type: "30days",
            label: "2026.03.21 ~ 2026.04.21",
            range: "2026.03.21 ~ 2026.04.21",
        },
        {
            id: "m-2026-03",
            type: "monthly",
            label: "3월",
            range: "2026.03.01 ~ 2026.03.31",
        },
        {
            id: "30-2026-03-01",
            type: "30days",
            label: "2026.02.01 ~ 2026.03.01",
            range: "2026.02.01 ~ 2026.03.01",
        },
    ];
    const [selectedReport, setSelectedReport] = useState(null);
    const [isReportDropdownOpen, setIsReportDropdownOpen] = useState(false);

    // 30일 범위 계산 (한 달 전 같은 날 ~ 선택일)
    const rangeEnd = selectedDate;
    const rangeStart = subMonths(rangeEnd, 1);
    const formatted30DayRange = `${format(rangeStart, "yyyy.MM.dd")} ~ ${format(
        rangeEnd,
        "yyyy.MM.dd"
    )}`;

    const handleNotification = () => alert("알림 아이콘 클릭");

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
        setAnalyzed(true); // 과거 리포트는 선택 즉시 결과 화면 노출
    };

    const handleYearDropdown = () => alert("년도 선택 드롭다운 열기");
    const handleMonthDropdown = () => alert("월 선택 드롭다운 열기");

    const handleDateSelect = (date) => {
        if (!date) return;
        setSelectedDate(startOfDay(date));
        setAnalyzed(false);
    };

    const handleAnalyze = () => {
        setAnalyzed(true);
        alert("분석하기");
    };
    const handleReselect = () => {
        setAnalyzed(false);
        alert("다시 선택");
    };

    const handleCategoryFilter = () => alert("카테고리 필터 열기");
    const handleAIInsightClick = (title) => alert(`"${title}" 인사이트 상세`);

    const aiInsights = [
        { title: "늦은 밤 운동", desc: "자주 실패" },
        { title: "아침 루틴", desc: "꾸준함 ↑" },
        { title: "공부 시간", desc: "저녁 집중" },
        { title: "주말 달성", desc: "평일 대비 낮음" },
    ];

    const resultRange =
        reportMode === "history" && selectedReport
            ? selectedReport.range
            : reportMode === "30days"
                ? formatted30DayRange
                : "2026.04.01 ~ 2026.04.30";

    return (
        <>
            {/* 상단 헤더 */}
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">월간 리포트</h1>
                <button
                    onClick={handleNotification}
                    className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm"
                >
                    {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
                    <span className="w-5 h-5 block" />
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
                </button>
            </header>

            {/* 스크롤 영역 */}
            <div className="flex-1 overflow-y-auto px-6 pt-6 pb-4">
                {/* 탭 토글 */}
                <div className="flex flex-col gap-2">
                    <div className="flex gap-2">
                        <button
                            onClick={() => handleTabChange("monthly")}
                            className={`px-4 py-2 rounded-full text-xs whitespace-nowrap ${
                                reportMode === "monthly"
                                    ? "bg-[#A8C8D8] font-bold text-white"
                                    : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"
                            }`}
                        >
                            월 단위 리포트 보기
                        </button>
                        <button
                            onClick={() => handleTabChange("30days")}
                            className={`px-4 py-2 rounded-full text-xs whitespace-nowrap ${
                                reportMode === "30days"
                                    ? "bg-[#A8C8D8] font-bold text-white"
                                    : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"
                            }`}
                        >
                            최근 30일 리포트 보기
                        </button>
                    </div>
                    <button
                        onClick={() => handleTabChange("history")}
                        className={`w-full py-2 rounded-full text-xs ${
                            reportMode === "history"
                                ? "bg-[#A8C8D8] font-bold text-white"
                                : "bg-[#D9DFE4] font-medium text-[#8B9BAA]"
                        }`}
                    >
                        발행했던 리포트 보기
                    </button>
                </div>

                {/* === 월 단위 뷰 === */}
                {reportMode === "monthly" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            분석할{" "}
                            <span className="text-[#E89B9B] font-semibold">년/월</span>을
                            선택하세요
                        </p>

                        <div className="mt-3 flex gap-3">
                            <button
                                onClick={handleYearDropdown}
                                className="flex-1 bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                            >
                                <span>2026년</span>
                                <span className="text-[#8B9BAA] text-xs">▼</span>
                            </button>
                            <button
                                onClick={handleMonthDropdown}
                                className="flex-1 bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                            >
                                <span>4월</span>
                                <span className="text-[#8B9BAA] text-xs">▼</span>
                            </button>
                        </div>

                        <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3 flex items-start gap-2">
                            {/* 아이콘 위치: 전구 (bi-lightbulb) */}
                            <span className="text-[#F4D58A] text-sm">💡</span>
                            <p className="text-xs text-[#3D4D5C]">
                                선택한 달의 1일부터 말일까지의 할 일 달성률을 분석합니다.
                            </p>
                        </div>
                    </>
                )}

                {/* === 발행 이력 뷰 === */}
                {reportMode === "history" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            <span className="text-[#E89B9B] font-semibold">다시 열람</span>
                            하고 싶은 리포트를 선택하세요
                        </p>

                        <div className="mt-3 relative">
                            <button
                                type="button"
                                onClick={() => setIsReportDropdownOpen((v) => !v)}
                                className="w-full bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm shadow-sm"
                            >
                <span
                    className={
                        selectedReport ? "text-[#3D4D5C]" : "text-[#8B9BAA]"
                    }
                >
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
                                                className={`w-full px-4 py-3 text-left text-sm hover:bg-[#EEF2F5] ${
                                                    selectedReport?.id === report.id
                                                        ? "bg-[#EEF2F5] text-[#3D4D5C] font-semibold"
                                                        : "text-[#3D4D5C]"
                                                }`}
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

                {/* === 최근 30일 뷰 === */}
                {reportMode === "30days" && (
                    <>
                        <p className="mt-5 text-xs text-[#3D4D5C]">
                            30일 기준의{" "}
                            <span className="text-[#E89B9B] font-semibold">마지막 날짜</span>
                            를 선택하세요
                        </p>

                        {/* 캘린더 카드 (shadcn/ui Calendar) */}
                        <div className="mt-3 bg-white rounded-2xl p-4 shadow-sm">
                            <Calendar
                                mode="single"
                                selected={selectedDate}
                                onSelect={handleDateSelect}
                                locale={ko}
                                showOutsideDays={false}
                                disabled={{ after: TODAY }}
                                modifiers={{
                                    // 선택일 "바로 전날" 까지만 range 로 표시 → 선택일은 selected 스타일이 단독으로 먹도록
                                    inRange: { from: rangeStart, to: subDays(rangeEnd, 1) },
                                }}
                                modifiersClassNames={{
                                    inRange: "bg-[#D9DFE4] text-[#3D4D5C] rounded-full",
                                }}
                                className="w-full"
                            />
                        </div>

                        {/* 선택된 범위 (yyyy.MM.dd ~ yyyy.MM.dd) */}
                        <div className="mt-4 bg-[#4A5C6E] rounded-xl py-3 flex items-center justify-center">
              <span className="text-white text-sm font-semibold">
                {formatted30DayRange}
              </span>
                        </div>

                        <div className="mt-3 bg-[#DEE4EA] rounded-xl px-4 py-3 flex items-start gap-2">
                            <span className="text-[#F4D58A] text-sm">💡</span>
                            <p className="text-xs text-[#3D4D5C] leading-5">
                                선택한 날로부터 한 달 전까지의 루틴을 분석합니다.
                                <br />예: 2026.04.21 선택 → 2026.03.21 ~ 2026.04.21
                            </p>
                        </div>
                    </>
                )}

                {/* 분석하기 버튼 (history 모드에서는 숨김 — 드롭다운 선택 즉시 결과로 진입) */}
                {reportMode !== "history" && (
                    <button
                        onClick={handleAnalyze}
                        className="mt-6 w-full py-4 rounded-2xl bg-[#B4D0DB] text-white font-bold text-sm"
                    >
                        분석하기
                    </button>
                )}

                {/* === 분석 결과 === */}
                {analyzed && (
                    <>
                        <div className="mt-6 flex items-center justify-between">
                            <h2 className="text-sm font-bold text-[#3D4D5C]">
                                {resultRange}
                            </h2>
                            <button
                                onClick={handleReselect}
                                className="px-3 py-1.5 rounded-full bg-[#4A5C6E] text-[11px] text-white font-medium"
                            >
                                다시 선택
                            </button>
                        </div>

                        <div className="mt-3 grid grid-cols-2 gap-3">
                            <div className="bg-white rounded-2xl p-4 shadow-sm">
                                <p className="text-[11px] text-[#8B9BAA]">이번 달 달성률</p>
                                <p className="mt-2 text-3xl font-bold text-[#A8C8D8]">40%</p>
                            </div>
                            <div className="bg-white rounded-2xl p-4 shadow-sm">
                                <p className="text-[11px] text-[#8B9BAA]">누적 달성률</p>
                                <p className="mt-2 text-3xl font-bold text-[#A8C8D8]">68%</p>
                            </div>
                        </div>

                        <div className="mt-4 bg-white rounded-2xl p-4 shadow-sm">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-bold text-[#3D4D5C]">
                                    카테고리별 달성률
                                </h3>
                                <button
                                    onClick={handleCategoryFilter}
                                    className="px-3 py-1 rounded-full bg-[#EEF2F5] text-[11px] text-[#3D4D5C] flex items-center gap-1"
                                >
                                    <span>전체</span>
                                    <span className="text-[#8B9BAA] text-[10px]">▼</span>
                                </button>
                            </div>

                            <div className="mt-4 flex items-center gap-4">
                                {/* 도넛 차트 (자리) - 실제 차트 라이브러리로 대체 예정
                    아이콘 위치: Recharts PieChart / Chart.js 도넛 차트 */}
                                <div className="relative w-24 h-24 shrink-0">
                                    <div className="absolute inset-0 rounded-full border-[10px] border-[#E4EEF3]" />
                                    <div
                                        className="absolute inset-0 rounded-full border-[10px] border-transparent"
                                        style={{
                                            borderTopColor: "#A8C8D8",
                                            borderRightColor: "#A8C8D8",
                                            transform: "rotate(-45deg)",
                                        }}
                                    />
                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-base font-bold text-[#3D4D5C]">
                      40%
                    </span>
                                        <span className="text-[9px] text-[#8B9BAA]">전체</span>
                                    </div>
                                </div>

                                <div className="flex-1 flex flex-col gap-2 text-xs">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="w-2 h-2 rounded-full bg-[#E89B9B]" />
                                            <span className="text-[#3D4D5C]">공부</span>
                                        </div>
                                        <span className="text-[#8B9BAA]">40%</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="w-2 h-2 rounded-full bg-[#F4D58A]" />
                                            <span className="text-[#3D4D5C]">운동</span>
                                        </div>
                                        <span className="text-[#8B9BAA]">운동</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="w-2 h-2 rounded-full bg-[#A8D5B4]" />
                                            <span className="text-[#3D4D5C]">약속</span>
                                        </div>
                                        <span className="text-[#8B9BAA]">약속</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="w-2 h-2 rounded-full bg-[#A8C8D8]" />
                                            <span className="text-[#3D4D5C]">일상</span>
                                        </div>
                                        <span className="text-[#8B9BAA]">일상</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <h3 className="mt-6 text-sm font-bold text-[#3D4D5C]">AI 분석</h3>
                        <div className="mt-3 grid grid-cols-2 gap-3">
                            {aiInsights.map((item) => (
                                <button
                                    key={item.title}
                                    onClick={() => handleAIInsightClick(item.title)}
                                    className="bg-white rounded-2xl p-3 shadow-sm text-left"
                                >
                  <span className="inline-block px-2 py-0.5 rounded-full bg-[#EEF2F5] text-[10px] text-[#3D4D5C]">
                    {item.title}
                  </span>
                                    <p className="mt-2 text-xs text-[#3D4D5C]">{item.desc}</p>
                                </button>
                            ))}
                        </div>

                        <div className="mt-4 bg-[#DEE4EA] rounded-xl px-4 py-3">
                            <p className="text-xs font-bold text-[#3D4D5C]">분석 리포트</p>
                            <p className="mt-2 text-xs text-[#3D4D5C] leading-5">
                                이번 달 가장 반복적으로 실패한 패턴은
                                <br />
                                늦은 밤 운동 루틴입니다.
                                <br />
                                에너지 저하 시간대와 겹쳐 실패가 집중된 점이 보입니다.
                            </p>
                        </div>
                    </>
                )}
            </div>
        </>
    );
}
