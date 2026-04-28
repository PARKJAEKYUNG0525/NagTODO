import React, { useEffect, useState } from "react";
import ModalLayout from "../ModalLayout";
import { showSuccessAlert, showWarningAlert } from "../utils/alertUtiles.js";

/**
 * TodoDetailModal
 * - 할 일 카드 클릭 시 열리는 상세/수정 모달.
 * - 제목/메모/카테고리/진행상태를 그 자리에서 수정하고 저장합니다.
 *
 * props:
 *   - isOpen   : boolean
 *   - onClose  : ()=>void
 *   - todo     : { id, title, memo, category, todo_status, ... } | null
 *   - onSave   : (updatedTodo)=>void
 *   - onDelete : (id)=>void
 */
const CATEGORIES = [
  { key: "study",       label: "공부" },
  { key: "workout",     label: "운동" },
  { key: "daily",       label: "일상" },
  { key: "appointment", label: "약속" },
  { key: "work",        label: "업무" },
  { key: "etc",         label: "기타" },
];

const TodoDetailModal = ({ isOpen, onClose, todo, onSave, onDelete }) => {
  const [title, setTitle] = useState("");
  const [memo, setMemo] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0].key);
  const [isPublic, setIsPublic] = useState(true);

  useEffect(() => {
    if (!todo) return;
    setTitle(todo.title || "");
    setMemo(todo.detail || "");
    setCategory(todo.category_id || CATEGORIES[0].key);
    setIsPublic(todo.visibility === "친구공개");
  }, [todo]);

  if (!todo) return null;

  const handleSave = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert("할 일 제목을 입력해 주세요.");
      return;
    }
    onSave?.({
      ...todo,
      title: title.trim(),
      detail: memo.trim(),
      category_id: category,
      visibility: isPublic ? "친구공개" : "비공개",
    });
    onClose?.();
  };

  const handleDelete = () => {
    onDelete?.(todo.todo_id);
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

        {/* 카테고리 */}
        <div className="flex flex-col gap-2">
          <span className="text-xs text-[#8B9BAA]">카테고리</span>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => {
              const active = category === cat.key;
              return (
                <button
                  key={cat.key}
                  type="button"
                  onClick={() => setCategory(cat.key)}
                  className={`px-3 py-2 rounded-full text-xs font-medium transition ${
                    active ? "bg-[#3D4D5C] text-white" : "bg-[#F5F8FA] text-[#8B9BAA]"
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
