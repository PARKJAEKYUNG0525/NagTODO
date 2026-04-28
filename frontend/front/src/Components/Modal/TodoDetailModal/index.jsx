import React, { useEffect, useState } from "react";
import ModalLayout from "../ModalLayout";

/**
 * TodoDetailModal
 * - 할 일 카드 클릭 시 열리는 상세/수정 모달.
 * - 제목/메모/카테고리를 그 자리에서 수정하고 저장합니다.
 *
 * props:
 *   - isOpen   : boolean
 *   - onClose  : ()=>void
 *   - todo     : { id, title, memo, category, ... } | null
 *   - onSave   : (updatedTodo)=>void
 *   - onDelete : (id)=>void
 *
 * ※ 추후 "완료/해제", "반복 설정", "알림 설정" 등을 확장하기 위한 기본 틀.
 */
const CATEGORIES = [
  { key: "study",       label: "공부", color: "#E88A8A" },
  { key: "workout",     label: "운동", color: "#F4D58A" },
  { key: "daily",       label: "일상", color: "#A8D5B4" },
  { key: "appointment", label: "약속", color: "#C5A8D8" },
  { key: "work",        label: "업무", color: "#A8B8D8" },
  { key: "etc",         label: "기타", color: "#B8C8D0" },
];

const TodoDetailModal = ({ isOpen, onClose, todo, onSave, onDelete }) => {
  const [title, setTitle] = useState("");
  const [memo, setMemo] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0].key);
  const [isPublic, setIsPublic] = useState(true);

  // 모달이 열릴 때마다 todo 값을 동기화
  useEffect(() => {
    if (!todo) return;
    setTitle(todo.title || "");
    setMemo(todo.memo || "");
    setCategory(todo.category || CATEGORIES[0].key);
    setIsPublic(todo.isPublic ?? true);
  }, [todo]);

  if (!todo) {
    // 보호: todo 가 없는 경우 아무 것도 안 그림
    return null;
  }

  const handleSave = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert("할 일 제목을 입력해 주세요.");
      return;
    }
    onSave?.({
      ...todo,
      title: title.trim(),
      memo: memo.trim(),
      category,
      isPublic,
    });
    onClose?.();
  };

  const handleDelete = () => {
    onDelete?.(todo.id);
    onClose?.();
  };

  return (
      <ModalLayout isOpen={isOpen} onClose={onClose} title="할 일 상세">
        <form onSubmit={handleSave} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1">
            <span className="text-xs text-[#8B9BAA]">제목</span>
            <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-xs text-[#8B9BAA]">메모</span>
            <textarea
                rows={3}
                value={memo}
                onChange={(e) => setMemo(e.target.value)}
                className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8] resize-none"
            />
          </label>

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

          <div className="mt-2 flex gap-2">
            <button
                type="button"
                onClick={handleDelete}
                className="flex-1 py-3 rounded-xl bg-[#FCEAEA] text-[#E89B9B] font-semibold text-sm"
            >
              삭제
            </button>
            <button
                type="submit"
                className="flex-1 py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9]"
            >
              저장하기
            </button>
          </div>
        </form>
      </ModalLayout>
  );
};

export default TodoDetailModal;
