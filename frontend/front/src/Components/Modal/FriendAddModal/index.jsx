import React, { useEffect, useState, useRef, useCallback } from "react";
import ModalLayout from "../ModalLayout";

const FriendAddModal = ({ isOpen, onClose, onSearch }) => {
  const [query, setQuery] = useState("");                 // 검색창에 입력된 텍스트
  const [searchResults, setSearchResults] = useState([]); // API에서 받아온 검색 결과 목록
  const [hasSearched, setHasSearched] = useState(false);  // 검색을 한 번이라도 했는지 여부 (결과 없음 vs 아직 검색 안 함 구분용)
  const [isLoading, setIsLoading] = useState(false);      // API 호출 중인지 여부 (로딩 스피너 표시용)
  const [isComposing, setIsComposing] = useState(false);  // 한글 조합 중인지 여부 (조합 완료 전에 검색 실행 방지용)
  const debounceTimer = useRef(null);                     // 디바운스 타이머 ID 저장 (타이핑할 때마다 API 호출 방지, 입력 멈춘 후 500ms 뒤에만 검색)

  // 모달 닫힐 때 상태 초기화
  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      setSearchResults([]);
      setHasSearched(false);
      setIsLoading(false);
    }
  }, [isOpen]);

  // 실제 검색 실행
  const runSearch = async (value) => {
      const trimmed = value.trim();
      if (!trimmed) {
        setSearchResults([]);
        setHasSearched(false);
        setIsLoading(false);
        return;
      }
      setIsLoading(true);
      try {
        const results = await onSearch?.(trimmed); // 실제 API 호출
        setSearchResults(results || []);
        setHasSearched(true);
      } catch (error) {
        console.error("검색 중 에러:", error);
        setSearchResults([]);
        setHasSearched(true);
      } finally {
        setIsLoading(false);
      }
    };

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    if (isComposing) return; // 한글 조합 중엔 검색 안 함

    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (!value.trim()) {
      setSearchResults([]);
      setHasSearched(false);
      return;
    }

    debounceTimer.current = setTimeout(() => {
      runSearch(value);
    }, 500);
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = (e) => {
    setIsComposing(false);
    const value = e.target.value;
    setQuery(value);

    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      runSearch(value);
    }, 500);
  };

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="친구 추가">
      <div className="flex flex-col gap-4">
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-base pointer-events-none">
            {isLoading ? "⏳" : "🔍"}
          </span>
          <input
            type="text"
            value={query}
            onChange={handleChange}
            onCompositionStart={handleCompositionStart}
            onCompositionEnd={handleCompositionEnd}
            placeholder="닉네임 또는 이메일로 검색"
            className="w-full pl-10 px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
          />
        </div>

        <div className="mt-2">
          <span className="text-sm font-bold text-[#3D4D5C]">검색 결과</span>
        </div>

        <div className="flex flex-col gap-3 min-h-[100px] max-h-[300px] overflow-y-auto">
          {hasSearched ? (
            searchResults.length > 0 ? (
              searchResults.map((user) => (
                <div
                  key={user.user_id}
                  className="flex items-center p-4 rounded-2xl bg-white border border-[#E1E8ED]"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#A8C8D8] opacity-50"></div>
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-[#3D4D5C]">
                        {user.username}
                      </span>
                      <span className="text-xs text-[#8B9BAA]">
                        {user.status_message || "상태메시지"}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center py-10">
                <p className="text-xs text-[#8B9BAA]">검색 결과가 없습니다.</p>
              </div>
            )
          ) : (
            <div className="flex items-center justify-center py-10 border-2 border-dashed border-[#F5F8FA] rounded-2xl">
              <p className="text-xs text-[#8B9BAA]">친구를 검색해 보세요!</p>
            </div>
          )}
        </div>
      </div>
    </ModalLayout>
  );
};

export default FriendAddModal;