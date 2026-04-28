import React, { useState } from "react";
import { format } from "date-fns";
import ModalLayout from "../ModalLayout";
import { useAuth } from "../../../hooks/useAuth";
import { useInterference } from "../../../hooks/useInterference";
import api from "../../../utils/api";

/**
 * NewTodoModal
 * - 새 할 일 추가 모달
 * - 저장 시 백엔드 POST /todos/ 호출 → AI 간섭 팝업 트리거
 *
 * props:
 *   - isOpen        : boolean
 *   - onClose       : ()=>void
 *   - onSubmit      : (todo)=>void  — 부모의 목록 갱신용 콜백 (선택)
 *   - selectedDate  : Date          — 캘린더에서 선택한 날짜 (기본값: 오늘)
 */
const CATEGORIES = [
    { key: "study",       label: "공부" },
    { key: "workout",     label: "운동" },
    { key: "daily",       label: "일상" },
    { key: "appointment", label: "약속" },
    { key: "work",        label: "업무" },
    { key: "etc",         label: "기타" },
];

const NewTodoModal = ({ isOpen, onClose, onSubmit, selectedDate = new Date() }) => {
    const { user } = useAuth();
    const { showLoading, showFeedback } = useInterference();

    const [title, setTitle] = useState("");
    const [memo, setMemo] = useState("");
    const [category, setCategory] = useState(CATEGORIES[0].key);
    const [isPublic, setIsPublic] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title.trim()) return;

        // 모달 즉시 닫고 로딩 팝업 표시
        const snapshot = { title: title.trim(), memo: memo.trim(), category, isPublic };
        setTitle("");
        setMemo("");
        setCategory(CATEGORIES[0].key);
        setIsPublic(true);
        onClose?.();
        showLoading();
        setSubmitting(true);

        try {
            const res = await api.post("/todos/", {
                title: snapshot.title,
                detail: snapshot.memo,
                category_id: snapshot.category,
                visibility: snapshot.isPublic ? "친구공개" : "비공개",
                user_id: user.user_id,
                created_at: format(selectedDate, "yyyy-MM-dd'T'HH:mm:ss"),
            });

            const feedback = res.data.interference?.feedback ?? "할 수 있어! 이번엔 꼭 해내길 바라!";
            showFeedback(feedback);
            onSubmit?.(snapshot);
        } catch (err) {
            const detail = err.response?.data?.detail;
            showFeedback(detail ?? "todo 저장에 실패했어요. 다시 시도해 주세요.");
        } finally {
            setSubmitting(false);
        }
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
                    <div className="flex gap-2">
                        {CATEGORIES.map((cat) => {
                            const active = category === cat.key;
                            return (
                                <button
                                    key={cat.key}
                                    type="button"
                                    onClick={() => setCategory(cat.key)}
                                    className={`px-3 py-2 rounded-full text-xs font-medium transition ${
                                        active
                                            ? "bg-[#3D4D5C] text-white"
                                            : "bg-[#F5F8FA] text-[#8B9BAA]"
                                    }`}
                                >
                                    {cat.label}
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
