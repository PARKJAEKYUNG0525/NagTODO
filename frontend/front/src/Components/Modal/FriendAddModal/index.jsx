import React, { useState } from "react";
import ModalLayout from "../ModalLayout";

/**
 * FriendAddModal
 * - 친구 목록 화면에서 "+" 버튼 클릭 시 열리는 친구 추가 모달.
 * - 닉네임/이메일 입력 → 검색 → onSubmit(query).
 *
 * props:
 *   - isOpen   : boolean
 *   - onClose  : ()=>void
 *   - onSubmit : (query)=>void
 *
 * ※ 실제 검색 결과 렌더링은 추후. 지금은 입력 + 제출까지만.
 */
const FriendAddModal = ({ isOpen, onClose, onSubmit }) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) {
      alert("닉네임 또는 이메일을 입력해 주세요.");
      return;
    }
    onSubmit?.(query.trim());
    setQuery("");
    onClose?.();
  };

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="친구 추가">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-xs text-[#8B9BAA]">닉네임 또는 이메일</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="예: nagtodo_user 또는 user@email.com"
            className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
          />
        </label>

        <p className="text-[11px] text-[#8B9BAA] leading-relaxed">
          * 친구 요청을 보내면 상대가 수락해야 친구로 추가됩니다.
        </p>

        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9] disabled:opacity-60"
          disabled={!query.trim()}
        >
          친구 요청 보내기
        </button>
      </form>
    </ModalLayout>
  );
};

export default FriendAddModal;
