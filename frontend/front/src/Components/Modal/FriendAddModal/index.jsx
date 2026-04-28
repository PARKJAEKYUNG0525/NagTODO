import React, { useEffect, useState } from "react";
import ModalLayout from "../ModalLayout";

// /**
//  * FriendAddModal
//  * - 친구 목록 화면에서 "+" 버튼 클릭 시 열리는 친구 추가 모달.
//  * - 닉네임/이메일 입력 → 검색 → onSubmit(query).
//  *
//  * props:
//  *   - isOpen   : boolean
//  *   - onClose  : ()=>void
//  *   - onSubmit : (query)=>void
//  *
//  * ※ 실제 검색 결과 렌더링은 추후. 지금은 입력 + 제출까지만.
//  */
// const FriendAddModal = ({ isOpen, onClose, onSearch, onSendRequest }) => {
//   const [query, setQuery] = useState("");
//   const [searchResults, setSearchResults] = useState([]); // 결과가 여러 명일 수 있으므로 배열로 변경
//   const [hasSearched, setHasSearched] = useState(false);

//   // 검색 핸들러: 엔터를 치거나 검색을 실행할 때
//   useEffect(() => {
//     const fetchResults = async () => {
//       const trimmedQuery = query.trim();
      
//       if (trimmedQuery.length > 0) {
//         // 부모 컴포넌트의 검색 함수 호출 (검색 결과 배열을 반환한다고 가정)
//         const results = await onSearch?.(trimmedQuery); 
//         setSearchResults(results || []);
//         setHasSearched(true);
//       } else {
//         // 입력창이 비어있으면 결과 초기화
//         setSearchResults([]);
//         setHasSearched(false);
//       }
//     };

//     fetchResults();
//   }, [query, onSearch]);

//   // 신청 핸들러: 검색 결과 옆 '요청' 버튼 클릭 시
//   const handleSearchSubmit = (e) => {
//     e.preventDefault(); // 실시간 검색 중이므로 엔터 시 페이지 새로고침만 막음
//   };
  
//   const handleSendRequest = async (user) => {
//     if (!user || !user.user_id) return;

//     try {
//       // 1. 부모로부터 받은 요청 함수 실행
//       const success = await onSendRequest?.(user.user_id);

//       if (success) {
//         // 2. 성공 알림
//         alert(`${user.username}님께 친구 요청을 보냈습니다.`);

//         // 3. UI 상태 초기화 (깔끔한 다음 사용을 위해)
//         setQuery("");            // 입력창 비우기
//         setSearchResults([]);     // 검색 결과 리스트 비우기
//         setHasSearched(false);   // 검색 상태 초기화

//         // 4. 모달 닫기
//         onClose?.();
//       } else {
//         // 서버에서 실패 응답을 준 경우 (이미 친구거나 요청 중일 때 등)
//         alert("요청을 보낼 수 없습니다. 이미 친구이거나 요청 대기 중인지 확인해 주세요.");
//       }
//     } catch (error) {
//       console.error("친구 요청 중 에러 발생:", error);
//       alert("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
//     }
//   };




//   // const handleSubmit = (e) => {
//   //   e.preventDefault();
//   //   if (!query.trim()) {
//   //     alert("닉네임 또는 이메일을 입력해 주세요.");
//   //     return;
//   //   }
//   //   onSubmit?.(query.trim());
//   //   setQuery("");
//   //   onClose?.();
//   // };

//   return (
//     <ModalLayout isOpen={isOpen} onClose={onClose} title="친구 추가">
//       <form onSubmit={handleSearchSubmit} className="flex flex-col gap-4">
//         <label className="flex flex-col gap-1">
//           <span className="text-xs text-[#8B9BAA]">닉네임 또는 이메일</span>
//           <input
//             type="text"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             placeholder="예: nagtodo_user 또는 user@email.com"
//             className="px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
//           />
//         </label>

//         <p className="text-[11px] text-[#8B9BAA] leading-relaxed">
//           * 친구 요청을 보내면 상대가 수락해야 친구로 추가됩니다.
//         </p>

//       {/* 검색 결과 영역 */}
//         <div className="min-h-[80px]">
//           {searchResults.length > 0 ? (
//             searchResults.map((user) => (
//             <div key={user.user_id} className="flex items-center justify-between p-4 rounded-2xl bg-[#F5F8FA] border border-[#E1E8ED]">
//               <div className="flex flex-col">
//                 <span className="text-sm font-bold text-[#3D4D5C]">
//                   {user.username}
//                 </span>
//                 <span className="text-xs text-[#8B9BAA]">
//                   {user.email}
//                 </span>
//               </div>
//               <button
//                 onClick={() => handleSendRequest(user)}
//                 className="px-4 py-2 rounded-lg bg-[#A8C8D8] text-white text-xs font-bold hover:bg-[#97BAC9]"
//               >
//                 요청
//               </button>
//             </div>
//           )) 
//           ) : (
//             <div className="flex items-center justify-center py-8 border-2 border-dashed border-[#F5F8FA] rounded-2xl">
//               <p className="text-xs text-[#8B9BAA]">검색 결과가 없습니다.</p>
//             </div>
//           )}
//         </div>
//       </form>
//     </ModalLayout>
//   );
// };



const FriendAddModal = ({ isOpen, onClose, onSearch, onSendRequest }) => {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 검색 실행 함수 (버튼 클릭 시 호출)
  const handleSearch = async (e) => {
    e.preventDefault(); // 폼 제출 막기
    const trimmedQuery = query.trim();
    
    if (!trimmedQuery) {
      alert("닉네임 또는 이메일을 입력해 주세요.");
      return;
    }

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
  };

  // 친구 요청 전송 함수
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
        <form onSubmit={handleSearch} className="flex flex-col gap-4">
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-base pointer-events-none">🔍</span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="닉네임 또는 이메일로 검색"
              className="w-full pl-10 px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8]"
            />
          </div>

          {/* 검색 버튼 (사진의 '친구 요청 보내기' 버튼 위치) */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-bold text-sm hover:bg-[#97BAC9] transition-colors disabled:bg-gray-300"
          >
            {isLoading ? "검색 중..." : "검색"}
          </button>
        </form>

        {/* 결과 섹션 제목 */}
        <div className="mt-2">
          <span className="text-sm font-bold text-[#3D4D5C]">검색 결과</span>
        </div>

        {/* 검색 결과 리스트 */}
        <div className="flex flex-col gap-3 min-h-[100px] max-h-[300px] overflow-y-auto">
          {hasSearched ? (
            searchResults.length > 0 ? (
              searchResults.map((user) => (
                <div key={user.user_id} className="flex items-center justify-between p-4 rounded-2xl bg-white border border-[#E1E8ED]">
                  <div className="flex items-center gap-3">
                    {/* 프로필 이미지 아이콘 (사진의 원형 부분) */}
                    <div className="w-10 h-10 rounded-full bg-[#A8C8D8] opacity-50"></div>
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-[#3D4D5C]">{user.username}</span>
                      <span className="text-xs text-[#8B9BAA]">{user.status_message || "상태메시지"}</span>
                    </div>
                  </div>
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
