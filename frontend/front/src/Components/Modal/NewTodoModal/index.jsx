import React, { useState } from "react";
import ModalLayout from "../ModalLayout";

/**
 * NewTodoModal
 * - 새 할 일 추가 모달
 * - ModalLayout 안에 폼만 얹은 구조.
 * - 저장 시 onSubmit({ title, memo, category }) 로 부모에게 넘깁니다.
 *
 * props:
 *   - isOpen    : boolean
 *   - onClose   : ()=>void
 *   - onSubmit  : (todo)=>void
 *
 * ※ 카테고리는 일단 하드코딩. 추후 props 로 주입 예정.
 */
const CATEGORIES = [
  { key: "study", label: "공부", color: "#E88A8A" },
  { key: "workout", label: "운동", color: "#F4D58A" },
  { key: "daily", label: "일상", color: "#A8D5B4" },
];

const NewTodoModal = ({ isOpen, onClose, onSubmit }) => {
  const [title, setTitle] = useState("");
  const [memo, setMemo] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0].key);
  const [isPublic, setIsPublic] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert("할 일 제목을 입력해 주세요.");
      return;
    }
    onSubmit?.({
      title: title.trim(),
      memo: memo.trim(),
      category,
      isPublic,
    });
    setTitle("");
    setMemo("");
    setCategory(CATEGORIES[0].key);
    setIsPublic(true);
    onClose?.();
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
                        className={`flex items-center gap-2 px-3 py-2 rounded-full text-xs font-medium transition ${
                            active
                                ? "bg-[#3D4D5C] text-white"
                                : "bg-[#F5F8FA] text-[#8B9BAA]"
                        }`}
                    >
                  <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: cat.color }}
                  />
                      {cat.label}
                    </button>
                );
              })}
            </div>
          </div>

          {/* 친구에게 공개 토글 */}
          <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-[#3D4D5C]">
            친구에게 공개
          </span>
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
              disabled={!title.trim()}
          >
            저장하기
          </button>
        </form>
      </ModalLayout>
  );
};

export default NewTodoModal;
