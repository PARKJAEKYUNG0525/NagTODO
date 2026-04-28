import React, { useEffect, useState } from "react";
import ModalLayout from "../ModalLayout";

const FriendAddModal = ({ isOpen, onClose, onSearch, onSendRequest }) => {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  

  // 실시간 검색 (debounce 적용)
  useEffect(() => {
    const trimmedQuery = query.trim();

    // 입력값 없으면 초기화
    if (!trimmedQuery) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    const delay = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await onSearch?.(trimmedQuery);
        setSearchResults(results || []);
        setHasSearched(true);
      } catch (error) {
        console.error("검색 중 에러:", error);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(delay);
  }, [query]);


  // 친구 요청
  const handleSendRequest = async (user) => {
    if (!user || !user.user_id) return;

    try {
      const success = await onSendRequest?.(user.user_id);
      if (success) {
        alert(`${user.username}님께 친구 요청을 보냈습니다.`);
        // 성공 시 상태 초기화 및 모달 닫기
        setQuery("");
        setSearchResults([]);
        setHasSearched(false);
        onClose?.();
      } else {
        alert("이미 친구이거나 요청 대기 중인 사용자입니다.");
      }
    } catch (error) {
      alert("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
    }
  };

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="친구 추가">
      <div className="flex flex-col gap-4">

        {/* 입력 영역 */}
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-base pointer-events-none">
            🔍
          </span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="닉네임 또는 이메일로 검색"
            className="w-full pl-10 px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
          />
        </div>

        {/* 결과 제목 */}
        <div>
          <span className="text-sm font-bold text-[#3D4D5C]">
            검색 결과
          </span>
        </div>

        {/* 결과 리스트 */}
        <div className="flex flex-col gap-3 min-h-[100px] max-h-[300px] overflow-y-auto">

          {/* 로딩 상태 */}
          {isLoading && (
            <div className="flex justify-center py-6 text-sm text-gray-400">
              검색 중...
            </div>
          )}

          {/* 검색 결과 */}
          {!isLoading && hasSearched ? (
            searchResults.length > 0 ? (
              searchResults.map((user) => (
                <div
                  key={user.user_id}
                  className="flex items-center justify-between p-4 rounded-2xl bg-white border border-[#E1E8ED]"
                >
                  <div className="flex items-center gap-3">
                    {/* 프로필 */}
                    <div className="w-10 h-10 rounded-full bg-[#A8C8D8] opacity-50"></div>

                    {/* 유저 정보 */}
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-[#3D4D5C]">
                        {user.username}
                      </span>
                      <span className="text-xs text-[#8B9BAA]">
                        {user.status_message || "상태메시지"}
                      </span>
                    </div>
                  </div>

                  {/* 친구 요청 버튼 */}
                  <button
                    onClick={() => handleSendRequest(user)}
                    className="px-4 py-1.5 rounded-full bg-[#A8C8D8] text-white text-xs font-bold hover:bg-[#97BAC9]"
                  >
                    요청
                  </button>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center py-10">
                <p className="text-xs text-[#8B9BAA]">
                  검색 결과가 없습니다.
                </p>
              </div>
            )
          ) : (
            !isLoading && (
              <div className="flex items-center justify-center py-10 border-2 border-dashed border-[#F5F8FA] rounded-2xl">
                <p className="text-xs text-[#8B9BAA]">
                  친구를 검색해 보세요!
                </p>
              </div>
            )
          )}
        </div>
      </div>
    </ModalLayout>
  );
};

export default FriendAddModal;
