import React, { useEffect, useState } from "react";
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
const FriendAddModal = ({ isOpen, onClose, onSearch, onSendRequest }) => {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false); // 로딩 상태
  const [hasSearched, setHasSearched] = useState(false);

  // 검색
  useEffect(() => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    setIsSearching(true);
    const handler = setTimeout(async () => {
      const results = await onSearch?.(trimmedQuery);
      setSearchResults(results || []);
      setHasSearched(true);
      setIsSearching(false);
    }, 400);

    return () => clearTimeout(handler);
  }, [query, onSearch]);

  // 신청
  const handleSearchSubmit = (e) => {
    e.preventDefault(); // 실시간 검색 중이므로 엔터 시 페이지 새로고침만 막음
  };
  
  const handleSendRequest = async (user) => {
    if (!user?.user_id) return;

    try {
      const success = await onSendRequest?.(user.user_id);

      if (success) {
        alert(`${user.username}님께 친구 요청을 보냈습니다.`);
        setQuery("");
        onClose?.();
      } else {
        alert("요청을 보낼 수 없습니다. 이미 친구이거나 요청 대기 중인지 확인해 주세요.");
      }
    } 
    catch (error) {
      alert("오류가 발생했습니다.");
    }
  };




  // const handleSubmit = (e) => {
  //   e.preventDefault();
  //   if (!query.trim()) {
  //     alert("닉네임 또는 이메일을 입력해 주세요.");
  //     return;
  //   }
  //   onSubmit?.(query.trim());
  //   setQuery("");
  //   onClose?.();
  // };

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="친구 추가">
      <form onSubmit={handleSearchSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-xs text-[#8B9BAA]">닉네임 또는 이메일</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="닉네임 또는 이메일로 검색"
            className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
          />
        </label>

        <p className="text-[11px] text-[#8B9BAA] leading-relaxed">
          * 친구 요청을 보내면 상대가 수락해야 친구로 추가됩니다.
        </p>

      {/* 검색 결과 영역 */}
        <div className="min-h-[80px]">
          {searchResults.length > 0 ? (
            searchResults.map((user) => (
            <div key={user.user_id} className="flex items-center justify-between p-4 rounded-2xl bg-[#F5F8FA] border border-[#E1E8ED]">
              <div className="flex flex-col">
                <span className="text-sm font-bold text-[#3D4D5C]">
                  {user.username}
                </span>
                <span className="text-xs text-[#8B9BAA]">
                  {user.email}
                </span>
              </div>
              <button
                onClick={() => handleSendRequest(user)}
                className="px-4 py-2 rounded-lg bg-[#A8C8D8] text-white text-xs font-bold hover:bg-[#97BAC9]"
              >
                요청
              </button>
            </div>
          )) 
          ) : (
            <div className="flex items-center justify-center py-8 border-2 border-dashed border-[#F5F8FA] rounded-2xl">
              <p className="text-xs text-[#8B9BAA]">검색 결과가 없습니다.</p>
            </div>
          )}
        </div>
      </form>
    </ModalLayout>
  );
};

export default FriendAddModal;
