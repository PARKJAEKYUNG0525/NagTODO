import React, { useEffect, useState } from "react";
import { format } from "date-fns";
import ModalLayout from "../ModalLayout";
import { useAuth } from "../../../hooks/useAuth";
import { useInterference } from "../../../hooks/useInterference";
import { useTodo } from "../../../hooks/useTodo";
import useCategory from "../../../hooks/useCategory";

/**
 * NewTodoModal
 * - 새 할 일 추가 모달
 * - 저장 시 useTodo.createTodo() 호출 → AI 간섭 팝업 트리거
 *
 * props:
 *   - isOpen        : boolean
 *   - onClose       : ()=>void
 *   - onSubmit      : (todo)=>void  — 부모의 목록 갱신용 콜백 (선택)
 *   - selectedDate  : Date          — 캘린더에서 선택한 날짜 (기본값: 오늘)
 */

const NewTodoModal = ({ isOpen, onClose, onSubmit, selectedDate = new Date() }) => {
    const { user } = useAuth();
    const { showFeedback } = useInterference();
    const { createTodo } = useTodo();
    const { getCategory } = useCategory();

    const [categories, setCategories] = useState([]);
    const [title, setTitle] = useState("");
    const [memo, setMemo] = useState("");
    const [category, setCategory] = useState("");
    const [isPublic, setIsPublic] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    // 카테고리 목록을 서버에서 불러온다
    useEffect(() => {
        getCategory().then((data) => {
            if (data && data.length > 0) {
                setCategories(data);
                setCategory(data[0].category_id);
            }
        });
    }, [getCategory]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!title.trim() || submitting) return;

        const snapshot = { title: title.trim(), memo: memo.trim(), category, isPublic };

        // 모달 즉시 닫고 사용자가 다른 작업 가능하도록 함
        setTitle("");
        setMemo("");
        setCategory(categories[0]?.category_id ?? "");
        setIsPublic(true);
        onClose?.();
        setSubmitting(true);

        // AI 잔소리 생성은 백그라운드에서 처리 — 완료되면 팝업으로 알림
        // createTodo 내부에서 에러를 흡수하고 null을 반환하므로 .catch 불필요
        createTodo({
            title: snapshot.title,
            detail: snapshot.memo,
            category_id: snapshot.category,
            visibility: snapshot.isPublic ? "친구공개" : "비공개",
            user_id: user.user_id,
            created_at: format(selectedDate, "yyyy-MM-dd'T'HH:mm:ss"),
        }).then((data) => {
            if (data) {
                showFeedback(snapshot.title, data.interference);
                onSubmit?.(snapshot);
            }
        }).finally(() => {
            setSubmitting(false);
        });
    };

    return (
        <ModalLayout isOpen={isOpen} onClose={onClose} title="새 할 일 추가">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                {/* 제목 */}
                <label className="flex flex-col gap-1">
                    <span className="text-xs text-[#8B9BAA]">제목</span>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="예: React 복습하기"
                        className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
                    />
                </label>

                {/* 메모 */}
                <label className="flex flex-col gap-1">
                    <span className="text-xs text-[#8B9BAA]">메모</span>
                    <textarea
                        rows={3}
                        value={memo}
                        onChange={(e) => setMemo(e.target.value)}
                        placeholder="간단한 메모 (선택)"
                        className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8] resize-none"
                    />
                </label>

                {/* 카테고리 */}
                <div className="flex flex-col gap-2">
                    <span className="text-xs text-[#8B9BAA]">카테고리</span>
                    <div className="flex gap-2 flex-wrap">
                        {categories.map((cat) => {
                            const active = category === cat.category_id;
                            return (
                                <button
                                    key={cat.category_id}
                                    type="button"
                                    onClick={() => setCategory(cat.category_id)}
                                    className={`px-3 py-2 rounded-full text-xs font-medium transition ${
                                        active
                                            ? "bg-[#3D4D5C] text-white"
                                            : "bg-[#F5F8FA] text-[#8B9BAA]"
                                    }`}
                                >
                                    {cat.name}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* 친구에게 공개 토글 */}
                <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-[#3D4D5C]">친구에게 공개</span>
                    <button
                        type="button"
                        role="switch"
                        aria-checked={isPublic}
                        onClick={() => setIsPublic((v) => !v)}
                        className={`relative w-12 h-7 rounded-full transition-colors ${
                            isPublic ? "bg-[#A8C8D8]" : "bg-[#D9DFE4]"
                        }`}
                    >
                        <span
                            className={`absolute top-0.5 left-0.5 w-6 h-6 rounded-full bg-white shadow transition-transform ${
                                isPublic ? "translate-x-5" : "translate-x-0"
                            }`}
                        />
                    </button>
                </div>

                {/* 제출 */}
                <button
                    type="submit"
                    className="mt-2 w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9] disabled:opacity-60"
                    disabled={!title.trim() || submitting}
                >
                    저장하기
                </button>
            </form>
        </ModalLayout>
    );
};

export default NewTodoModal;
