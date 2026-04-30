import React, { useState, useEffect, useCallback } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay, isBefore } from "date-fns";
import { ko } from "date-fns/locale";
import NotificationBell from "../../Components/Notification";

import useTodo from "@/hooks/useTodo.jsx";
import useCategory from "@/hooks/useCategory.jsx";
import { useFriend } from "../../hooks/useFriend";
import { useAuth } from "../../hooks/useAuth";
import api from "../../utils/api";
import { showSuccessAlert } from "@/utils/alertUtils.js";
import { IoChevronBack } from "react-icons/io5";

// 상태 상수
const STATUS = {
    PENDING:     "시작전",
    IN_PROGRESS: "진행중",
    COMPLETED:   "완료",
    FAILED:      "실패",
};

const STATUS_COLOR = {
    PENDING:   "#A8C8D8",
    COMPLETED: "#A8D5B4",
    FAILED:    "#E89B9B",
};

export default function FriendDetail() {
    const { userId: friendUserId } = useParams();            // URL에서 친구 userId 추출
    const { state } = useLocation();                         // navigate state에서 friendName 추출
    const navigate = useNavigate();

    const friendName = state?.friendName ?? "친구";          // 이름 없으면 기본값

    const { getAllTodos } = useTodo();
    const { getCategory } = useCategory();
    const { fetchFriends } = useFriend();
    const { user: currentUser } = useAuth();

    const TODAY = startOfDay(new Date());

    const [selectedDate, setSelectedDate] = useState(TODAY);
    const [todos, setTodos] = useState([]);
    const [categories, setCategories] = useState([]);

    // 친구 todo 불러오기 (friendUserId를 파라미터로 전달)
    const loadTodos = useCallback(async () => {
        const data = await getAllTodos(Number(friendUserId));
        if (data) setTodos(data);
    }, [getAllTodos, friendUserId]);

    useEffect(() => {
        loadTodos();
    }, [loadTodos]);

    // 카테고리 불러오기
    const loadCategory = useCallback(async () => {
        const data = await getCategory();
        if (data) setCategories(data);
    }, [getCategory]);

    useEffect(() => {
        loadCategory();
    }, [loadCategory]);

    // 선택 날짜의 할 일 필터링
    const currentTodos = todos.filter((t) =>
        isSameDay(startOfDay(new Date(t.created_at)), selectedDate)
    );

    const categoryMap = Object.fromEntries(
        categories.map((c) => [c.category_id, c])
    );

    const isToday = isSameDay(selectedDate, TODAY);
    const formattedSelected = format(selectedDate, "M월 d일", { locale: ko });

    // 달력 도트용 날짜 계산
    const { highDays, midDays, lowDays } = (() => {
        const byDay = new Map();
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

    // 과거 날짜 + 미완료 → 실패로 표시
    const getDisplayStatus = (todo) => {
        const todoDay = startOfDay(new Date(todo.created_at));
        const isPast = isBefore(todoDay, TODAY);
        if (isPast && todo.todo_status !== STATUS.COMPLETED) return STATUS.FAILED;
        return todo.todo_status;
    };

    return (
        <>
            {/* 헤더: 뒤로가기 + 친구 이름 + 벨 */}
            <header className="px-6 pt-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => navigate(-1)}
                        className="w-10 h-10 flex items-center justify-center rounded-full bg-white shadow-sm cursor-pointer"
                        aria-label="뒤로가기"
                    >
                        <IoChevronBack className="w-5 h-5 text-[#3D4D5C]" />
                    </button>
                    <h1 className="text-2xl font-bold text-[#3D4D5C]">{friendName}</h1>
                </div>
                <NotificationBell />
            </header>

            {/* 스크롤 영역 */}
            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                {/* 캘린더 */}
                <div className="bg-white rounded-2xl p-4 shadow-sm">
                    <Calendar
                        mode="single"
                        selected={selectedDate}
                        onSelect={(date) => {
                            if (!date) return;
                            setSelectedDate(startOfDay(date));
                        }}
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
                            {friendName}의 할 일
                        </h2>
                        <p className="text-xs text-[#8B9BAA] mt-1">
                            {formattedSelected} · {currentTodos.length}개
                        </p>
                    </div>
                </div>

                {/* 할 일 카드 리스트 (읽기 전용) */}
                <div className="mt-3 flex flex-col gap-3">
                    {currentTodos.length === 0 ? (
                        <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                            등록된 할 일이 없어요.
                        </div>
                    ) : (
                        currentTodos.map((todo) => {
                            const category = categoryMap[todo.category_id];
                            const displayStatus = getDisplayStatus(todo);

                            const radioBorder =
                                displayStatus === STATUS.COMPLETED ? STATUS_COLOR.COMPLETED :
                                displayStatus === STATUS.FAILED    ? STATUS_COLOR.FAILED :
                                STATUS_COLOR.PENDING;

                            return (
                                <div
                                    key={todo.todo_id}
                                    className="w-full bg-white rounded-2xl p-4 shadow-sm"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start gap-3 flex-1">
                                            {/* 상태 표시 (읽기 전용 — 클릭 불가) */}
                                            <div
                                                className="w-6 h-6 rounded-full shrink-0 mt-0.5 flex items-center justify-center border-2"
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
                                            </div>

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
        </>
    );
}