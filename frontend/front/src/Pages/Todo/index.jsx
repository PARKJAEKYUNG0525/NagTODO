import React, { useState, useEffect, useCallback } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay, isBefore } from "date-fns";
import { ko } from "date-fns/locale";
import NewTodoModal from "../../Components/Modal/NewTodoModal";
import NotificationModal from "../../Components/Modal/NotificationModal";
import TodoDetailModal from "../../Components/Modal/TodoDetailModal";
import { useAuth } from "../../hooks/useAuth";
import useTodo from "@/hooks/useTodo.jsx";
import useCategory from "@/hooks/useCategory.jsx";
import useImg from "@/hooks/useImg.jsx";

import { BsFillBellFill } from "react-icons/bs";

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

// 달성률에 따른 도트 색
const RATE_COLOR = {
    HIGH:  "#A8D5B4", // 100% — 초록
    MID:   "#F4D58A", // 50%~99% — 노랑
    LOW:   "#E89B9B", // 50% 미만 — 빨강
};

// 상태별 라디오 색 (카드용)
const STATUS_COLOR = {
    PENDING:   "#A8C8D8", // 연한 청회색 — 빈 원
    COMPLETED: "#A8D5B4", // 초록 — 완료 점
    FAILED:    "#E89B9B", // 빨강 — ✕
};

// 할 일 상태 (DB값: 시작전/진행중/완료, FAILED는 표시 전용)
const STATUS = {
    PENDING:     "시작전",
    IN_PROGRESS: "진행중",
    COMPLETED:   "완료",
    FAILED:      "실패", // 표시 전용 — DB에 저장되지 않음
};

export default function Todo() {
    // ====== 상수/상태 ======
    const TODAY = startOfDay(new Date());

    const { getAllTodos } = useTodo();
    const { getCategory} = useCategory();
    const { currentBg, setCurrentBg, getUserBg } = useImg();

    const [selectedDate, setSelectedDate] = useState(TODAY);
    const [isDeleteMode, setIsDeleteMode] = useState(false);
    const [selectedTodoIds, setSelectedTodoIds] = useState([]);
    const [todos, setTodos] = useState([]);
    const [categories, setCategories] = useState([]);

    // 모달 상태
    const [isNotiOpen, setIsNotiOpen] = useState(false);
    const [isNewOpen, setIsNewOpen] = useState(false);
    const [detailTodo, setDetailTodo] = useState(null);

    // db에서 배경화면 불러오기
    useEffect(() => { getUserBg(); }, []);

    // db에서 todo 불러오기
    const loadTodos = useCallback(async () => {
        const db_todo = await getAllTodos();
        if (db_todo) setTodos(db_todo);
    }, [getAllTodos]);

    useEffect(() => {
        loadTodos();
    }, [loadTodos]);

    // db에서 category 불러오기
    const loadCategory = useCallback(async () => {
        const db_category = await getCategory();
        if (db_category) setCategories(db_category);
    }, [getCategory]);

    useEffect(() => {
        loadCategory();
    }, [loadCategory]);

    const currentTodos = todos.filter((t) =>
        isSameDay(startOfDay(new Date(t.created_at)), selectedDate)
    );
    const categoryMap = Object.fromEntries(
        categories.map((c) => [c.category_id, c])
    );

    const isToday = isSameDay(selectedDate, TODAY);
    const formattedSelected = format(selectedDate, "M월 d일", { locale: ko });

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
        setSelectedTodoIds(currentTodos.map((t) => t.todo_id));
    };
    const handleDeleteSelected = async () => {
        if (selectedTodoIds.length === 0) return;
        await Promise.all(selectedTodoIds.map((id) => deleteTodo(id)));
        setSelectedTodoIds([]);
        setIsDeleteMode(false);
        loadTodos();
    };

    const handleTodoClick = (todo) => {
        if (isDeleteMode) {
            setSelectedTodoIds((prev) =>
                prev.includes(todo.todo_id)
                    ? prev.filter((id) => id !== todo.todo_id)
                    : [...prev, todo.todo_id]
            );
        } else {
            setDetailTodo(todo);
        }
    };

    // 과거 날짜 + 미완료 → 화면에서 실패로 표시 (DB 값은 그대로)
    const getDisplayStatus = (todo) => {
        const todoDay = startOfDay(new Date(todo.created_at));
        const isPast = isBefore(todoDay, TODAY);
        if (isPast && todo.todo_status !== STATUS.COMPLETED) return STATUS.FAILED;
        return todo.todo_status;
    };

    // 클릭 시: 완료 ↔ 시작전 토글
    const getNextStatus = (todo_status) => {
        return todo_status === STATUS.COMPLETED ? STATUS.PENDING : STATUS.COMPLETED;
    };

    const handleToggleStatus = async (todo) => {
        const prevStatus = todo.todo_status;
        const nextStatus = getNextStatus(prevStatus);

        // 낙관적 업데이트 — 서버 응답 전에 UI를 먼저 갱신한다
        setTodos((prev) =>
            prev.map((t) =>
                t.todo_id === todo.todo_id ? { ...t, todo_status: nextStatus } : t
            )
        );
        const result = await updateTodo(todo.todo_id, { todo_status: nextStatus });
        if (!result) {
            // 요청 실패 시 이전 상태로 롤백
            setTodos((prev) =>
                prev.map((t) =>
                    t.todo_id === todo.todo_id ? { ...t, todo_status: prevStatus } : t
                )
            );
        }
    };

    // 같은 날의 todo 들끼리 묶어 달성률 계산 → 색 그룹별 날짜 배열
    const { highDays, midDays, lowDays } = (() => {
        const byDay = new Map(); // key: yyyy-MM-dd, value: Todo[]
        todos.forEach((t) => {
            const day = startOfDay(new Date(t.created_at));
            const key = format(day, "yyyy-MM-dd");
            if (!byDay.has(key)) byDay.set(key, { day, list: [] });
            byDay.get(key).list.push(t);
        });

        const high = [], mid = [], low = [];
        byDay.forEach(({ day, list }) => {
            const total = list.length;
            if (total === 0) return;
            const done = list.filter((t) => t.todo_status === STATUS.COMPLETED).length;
            const rate = done / total;
            if (rate >= 1) high.push(day);
            else if (rate >= 0.5) mid.push(day);
            else low.push(day);
        });
        return { highDays: high, midDays: mid, lowDays: low };
    })();

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
            {/* 상단 헤더 */}
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">
                    {format(selectedDate, "M월", { locale: ko })}
                </h1>
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

            {/* 스크롤 영역 */}
            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                {/* 캘린더 카드 (shadcn/ui Calendar) */}
                <div className="bg-white rounded-2xl p-4 shadow-sm">
                    <div className="flex items-center justify-end px-1 mb-1">
                        <button
                            onClick={handleToday}
                            className="text-xs text-[#87B4C4] font-medium"
                        >
                        </button>
                    </div>
                    <Calendar
                        mode="single"
                        selected={selectedDate}
                        onSelect={handleDateSelect}
                        locale={ko}
                        showOutsideDays
                        modifiers={{
                            high: highDays,
                            mid:  midDays,
                            low:  lowDays,
                        }}
                        modifiersClassNames={{
                            high: "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#A8D5B4]",
                            mid:  "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#F4D58A]",
                            low:  "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#E89B9B]",
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
                            const isChecked = selectedTodoIds.includes(todo.todo_id);
                            const category = categoryMap[todo.category_id];
                            const displayStatus = getDisplayStatus(todo);

                            // 상태에 따른 라디오 색
                            const radioBorder =
                                displayStatus === STATUS.COMPLETED ? STATUS_COLOR.COMPLETED :
                                    displayStatus === STATUS.FAILED    ? STATUS_COLOR.FAILED :
                                        STATUS_COLOR.PENDING;
                            return (
                                <div
                                    key={todo.todo_id}
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => handleTodoClick(todo)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter" || e.key === " ") {
                                            e.preventDefault();
                                            handleTodoClick(todo);
                                        }
                                    }}
                                    className={`w-full bg-white rounded-2xl p-4 shadow-sm text-left cursor-pointer ${
                                        isDeleteMode && isChecked ? "ring-2 ring-[#A8C8D8]" : ""
                                    }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start gap-3 flex-1">
                                            {/* 라디오 토글 (3-상태) */}
                                            <button
                                                type="button"
                                                aria-label={
                                                    displayStatus === STATUS.COMPLETED
                                                        ? "완료 해제"
                                                        : displayStatus === STATUS.FAILED
                                                            ? "다시 완료로 변경"
                                                            : "완료 표시"
                                                }
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleToggleStatus(todo);
                                                }}
                                                className="w-6 h-6 rounded-full shrink-0 mt-0.5 flex items-center justify-center border-2 transition"
                                                style={{ borderColor: radioBorder }}
                                            >
                                                {displayStatus === STATUS.COMPLETED && (
                                                    <span
                                                        className="w-2.5 h-2.5 rounded-full"
                                                        style={{ backgroundColor: STATUS_COLOR.COMPLETED }}
                                                    />
                                                )}
                                                {displayStatus === STATUS.FAILED && (
                                                    <span className="text-[#E89B9B] text-[11px] font-bold leading-none">
                                                        ✕
                                                    </span>
                                                )}
                                            </button>

                                            <div className="flex-1">
                                                <p className="text-sm font-bold text-[#3D4D5C]">
                                                    {todo.title}
                                                </p>
                                                {todo.detail && (
                                                    <p className="text-xs text-[#8B9BAA] mt-1">
                                                        {todo.detail}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        <span className="text-[11px] text-[#87B4C4] bg-[#E4EEF3] px-2 py-0.5 rounded-full shrink-0">
                                            {category?.name ?? todo.category_id}
                                        </span>
                                    </div>
                                </div>
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
                notifications={[]}
            />
            <NewTodoModal
                isOpen={isNewOpen}
                onClose={() => setIsNewOpen(false)}
                onSubmit={() => {
                    setIsNewOpen(false);
                    loadTodos();
                }}
                selectedDate={selectedDate}
            />
            <TodoDetailModal
                isOpen={!!detailTodo}
                onClose={() => setDetailTodo(null)}
                todo={detailTodo}
                onSave={async (updated) => {
                    const result = await updateTodo(updated.todo_id, {
                        title:       updated.title,
                        detail:      updated.detail,
                        category_id: updated.category_id,
                        todo_status: updated.todo_status,
                        visibility:  updated.visibility,
                    });
                    if (result) {
                        setDetailTodo(null);
                        loadTodos();
                    }
                }}
                onDelete={async (id) => {
                    await deleteTodo(id);
                    setDetailTodo(null);
                    loadTodos();
                }}
            />
        </div>
    );
}
