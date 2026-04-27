import React, { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";
import NewTodoModal from "../../Components/Modal/NewTodoModal";
import NotificationModal from "../../Components/Modal/NotificationModal";
import TodoDetailModal from "../../Components/Modal/TodoDetailModal";

/**
 * TodoMain 화면 (통합본)
 * 상태에 따라 세 가지 뷰를 하나의 파일에서 렌더합니다.
 *
 *  [1] 기본 뷰 (오늘 · 보기 모드)
 *      - 헤더 우측: "할 일 삭제" 텍스트 버튼
 *      - 우하단 플로팅 + 버튼 표시
 *  [2] 삭제 선택 모드 (오늘 · 선택 모드)
 *      - "할 일 삭제" 클릭 → isDeleteMode = true
 *      - 헤더 우측: "전체 선택 | 선택한 할 일 삭제 | 취소"
 *      - 플로팅 + 버튼 숨김
 *  [3] 지난 날짜 뷰 (달력에서 오늘(2026-04-21)이 아닌 날짜 선택 시)
 *      - 타이틀 / 서브타이틀이 date-fns format 으로 동적 생성
 *
 * ※ 9:16 프레임 / 하단 Navbar 는 App.jsx 가 담당. 여기서는 내부 콘텐츠만.
 * ※ shadcn/ui Calendar: npx shadcn-ui@latest add calendar
 * ※ date-fns: npm i date-fns
 */
export default function Todo() {
    // ====== 상수/상태 ======
    // 오늘 날짜
    const TODAY = startOfDay(new Date());

    const [selectedDate, setSelectedDate] = useState(TODAY);
    const [isDeleteMode, setIsDeleteMode] = useState(false);
    const [selectedTodoIds, setSelectedTodoIds] = useState([]);

    // 모달 상태
    const [isNotiOpen, setIsNotiOpen] = useState(false);
    const [isNewOpen, setIsNewOpen] = useState(false);
    const [detailTodo, setDetailTodo] = useState(null);

    // 날짜별 할 일 임시데이터 (isSameDay로 비교)
    const todosByDate = [
        {
            date: new Date(2026, 3, 21),
            todos: [
                {
                    id: 1,
                    title: "React 복습하기",
                    memo: "useContext, customHook",
                    category: "공부",
                    dotColor: "#D9DFE4",
                    dotLetter: "",
                },
                {
                    id: 2,
                    title: "FastAPI 복습하기",
                    memo: "DB 연동 연습하기",
                    category: "공부",
                    dotColor: "#E89B9B",
                    dotLetter: "V",
                },
            ],
        },
        {
            date: new Date(2026, 3, 15),
            todos: [
                {
                    id: 3,
                    title: "아침 러닝 30분",
                    memo: "",
                    category: "운동",
                    dotColor: "#E89B9B",
                    dotLetter: "",
                },
            ],
        },
    ];

    const currentTodos =
        todosByDate.find((entry) => isSameDay(entry.date, selectedDate))?.todos || [];
    const isToday = isSameDay(selectedDate, TODAY);
    const formattedSelected = format(selectedDate, "M월 d일", { locale: ko });

    const notifications = [
        {
            id: 1,
            title: "오늘의 할 일 알림",
            body: "'React 복습하기' 가 아직 미완료 상태예요.",
            time: "5분 전",
            read: false,
        },
        {
            id: 2,
            title: "연속 3일째 목표 달성!",
            body: "운동 카테고리를 3일 연속으로 완료했어요. 대단해요 👏",
            time: "2시간 전",
            read: true,
        },
    ];

    // ====== 핸들러 ======
    const handleToday = () => {
        setSelectedDate(TODAY);
        setIsDeleteMode(false);
        setSelectedTodoIds([]);
    };

    const handleDateSelect = (date) => {
        if (!date) return;
        setSelectedDate(startOfDay(date));
        setIsDeleteMode(false);
        setSelectedTodoIds([]);
    };

    const handleEnterDeleteMode = () => {
        setIsDeleteMode(true);
    };
    const handleCancelDeleteMode = () => {
        setIsDeleteMode(false);
        setSelectedTodoIds([]);
    };
    const handleSelectAll = () => {
        setSelectedTodoIds(currentTodos.map((t) => t.id));
    };
    const handleDeleteSelected = () =>
        alert(`선택한 ${selectedTodoIds.length}개의 할 일 삭제`);

    const handleTodoClick = (todo) => {
        if (isDeleteMode) {
            setSelectedTodoIds((prev) =>
                prev.includes(todo.id)
                    ? prev.filter((id) => id !== todo.id)
                    : [...prev, todo.id]
            );
        } else {
            setDetailTodo(todo);
        }
    };

    // ====== 카테고리별 도트 표시용 날짜 (shadcn/ui Calendar modifiers) ======
    const studyDays = [
        new Date(2026, 3, 3),
        new Date(2026, 3, 7),
        new Date(2026, 3, 12),
        new Date(2026, 3, 25),
        new Date(2026, 3, 28),
    ];
    const workoutDays = [new Date(2026, 3, 9), new Date(2026, 3, 21)];
    const dailyDays = [new Date(2026, 3, 5), new Date(2026, 3, 14)];

    return (
        <>
            {/* 상단 헤더 */}
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">
                    {format(selectedDate, "M월", {locale: ko})}
                </h1>
                <button
                    className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm"
                    onClick={() => setIsNotiOpen(true)}
                >
                    {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
                    <span className="w-5 h-5 block" />
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
                </button>
            </header>

            {/* 스크롤 영역 */}
            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                {/* 캘린더 카드 (shadcn/ui Calendar) */}
                <div className="bg-white rounded-2xl p-4 shadow-sm">
                    <div className="flex items-center justify-end px-1 mb-1">
                        <button
                            onClick={handleToday}
                            className="text-xs text-[#87B4C4] font-medium"
                        >
                            오늘
                        </button>
                    </div>
                    <Calendar
                        mode="single"
                        selected={selectedDate}
                        onSelect={handleDateSelect}
                        locale={ko}
                        showOutsideDays
                        modifiers={{
                            study: studyDays,
                            workout: workoutDays,
                            daily: dailyDays,
                        }}
                        modifiersClassNames={{
                            study:
                                "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#E88A8A]",
                            workout:
                                "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#F4D58A]",
                            daily:
                                "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#A8D5B4]",
                        }}
                        className="w-full"
                    />
                </div>

                {/* 할 일 섹션 헤더 */}
                <div className="mt-6 flex items-end justify-between">
                    <div>
                        <h2 className="text-base font-bold text-[#3D4D5C]">
                            {isToday ? "오늘의 할 일" : `${formattedSelected}의 할 일`}
                        </h2>
                        <p className="text-xs text-[#8B9BAA] mt-1">
                            {formattedSelected} · {currentTodos.length}개
                        </p>
                    </div>

                    {isDeleteMode ? (
                        <div className="flex items-center gap-3 text-xs">
                            <button onClick={handleSelectAll} className="text-[#8B9BAA]">
                                전체 선택
                            </button>
                            <button
                                onClick={handleDeleteSelected}
                                className="text-[#3D4D5C] font-semibold"
                            >
                                선택한 할 일 삭제
                            </button>
                            <button
                                onClick={handleCancelDeleteMode}
                                className="text-[#8B9BAA]"
                            >
                                취소
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={handleEnterDeleteMode}
                            className="text-xs text-[#8B9BAA]"
                        >
                            할 일 삭제
                        </button>
                    )}
                </div>

                {/* 할 일 카드 리스트 */}
                <div className="mt-3 flex flex-col gap-3">
                    {currentTodos.length === 0 ? (
                        <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                            등록된 할 일이 없어요.
                        </div>
                    ) : (
                        currentTodos.map((todo) => {
                            const isChecked = selectedTodoIds.includes(todo.id);
                            return (
                                <button
                                    key={todo.id}
                                    onClick={() => handleTodoClick(todo)}
                                    className={`
                    w-full bg-white rounded-2xl p-4 shadow-sm text-left
                    ${isDeleteMode && isChecked ? "ring-2 ring-[#A8C8D8]" : ""}
                  `}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start gap-3 flex-1">
                                            <div
                                                className="w-6 h-6 rounded-full shrink-0 mt-0.5 flex items-center justify-center"
                                                style={{ backgroundColor: todo.dotColor }}
                                            >
                                                {/* 아이콘 위치: 카테고리/완료 상태 아이콘
                            예: 공부 bi-book, 운동 bi-activity, 완료 bi-check */}
                                                {todo.dotLetter && (
                                                    <span className="text-white text-xs font-bold">
                            {todo.dotLetter}
                          </span>
                                                )}
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-sm font-bold text-[#3D4D5C]">
                                                    {todo.title}
                                                </p>
                                                {todo.memo && (
                                                    <p className="text-xs text-[#8B9BAA] mt-1">
                                                        {todo.memo}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        <span className="text-[11px] text-[#87B4C4] bg-[#E4EEF3] px-2 py-0.5 rounded-full shrink-0">
                      {todo.category}
                    </span>
                                    </div>
                                </button>
                            );
                        })
                    )}
                </div>
            </div>

            {/* 플로팅 + 버튼 (삭제 모드에서는 숨김) */}
            {!isDeleteMode && (
                <button
                    onClick={() => setIsNewOpen(true)}
                    className="absolute right-6 bottom-28 w-12 h-12 rounded-full bg-[#A8C8D8] flex items-center justify-center shadow-lg"
                    aria-label="새 할 일 추가"
                >
                    {/* 아이콘 위치: 플러스 (bi-plus-lg) */}
                    <span className="text-white text-2xl leading-none">+</span>
                </button>
            )}

            {/* ─── 모달들 ─── */}
            <NotificationModal
                isOpen={isNotiOpen}
                onClose={() => setIsNotiOpen(false)}
                notifications={notifications}
                onItemClick={(n) => alert(`"${n.title}" 상세 보기`)}
            />
            <NewTodoModal
                isOpen={isNewOpen}
                onClose={() => setIsNewOpen(false)}
                onSubmit={() => setIsNewOpen(false)}
            />
            <TodoDetailModal
                isOpen={!!detailTodo}
                onClose={() => setDetailTodo(null)}
                todo={detailTodo}
                onSave={(updated) => alert(`"${updated.title}" 저장`)}
                onDelete={(id) => alert(`id=${id} 삭제`)}
            />
        </>
    );
}
