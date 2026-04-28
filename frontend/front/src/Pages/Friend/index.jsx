import React, { useState, useEffect } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";
import { showWarningDialog, showSuccessAlert } from "@/utils/alertUtiles.js";
import FriendAddModal from "../../Components/Modal/FriendAddModal";
import NotificationModal from "../../Components/Modal/NotificationModal";

import { useFriend } from "../../hooks/useFriend";

/**
 * Friend 화면 (통합본)
 * 현재 계정의 관리자 여부(isAdmin)에 따라 분기합니다.
 *
 *  [비관리자] isAdmin = false
 *   - view === "list" : 친구 목록
 *   - view === "detail" : 친구 상세 - 친구의 캘린더 + 할 일
 *
 *  [관리자] isAdmin = true
 *   - 회원 관리 화면
 *   - 각 회원 카드 우측 "삭제" → alertUtils.confirmDelete
 *
 * ※ 9:16 프레임 / 하단 Navbar 는 App.jsx 담당.
 * ※ shadcn/ui Calendar, date-fns 사용.
 */
export default function Friend() {
    const [friends, setFriends] = useState([]);
    const { searchUser, sendRequest } = useFriend();

    const [isAdmin, setIsAdmin] = useState(false);
    const [view, setView] = useState("list"); // "list" | "detail"
    const [selectedFriend, setSelectedFriend] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [friendDetailDate, setFriendDetailDate] = useState(
        startOfDay(new Date(2026, 3, 21))
    );

    // 모달 상태
    const [isFriendAddOpen, setIsFriendAddOpen] = useState(false);
    const [isNotiOpen, setIsNotiOpen] = useState(false);

    //검색 모달
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const [searchResults, setSearchResults] = useState([]);

    

    const notifications = [
        {
            id: 1,
            title: "새 친구 요청",
            body: "'codehaeun' 님이 친구 요청을 보냈어요.",
            time: "방금 전",
            read: false,
        },
        {
            id: 2,
            title: "친구 목표 달성",
            body: "'친구1' 님이 오늘의 할 일을 모두 완료했어요.",
            time: "1시간 전",
            read: true,
        },
    ];

    useEffect(() => {
        // TODO: 실제 로직으로 교체 (예: useAuth)
        const checkAdmin = () => false;
        setIsAdmin(checkAdmin());
    }, []);


    const [members, setMembers] = useState([
        { id: 1, name: "회원1", status: "상태메시지" },
        { id: 2, name: "회원2", status: "상태메시지" },
        { id: 3, name: "회원3", status: "상태메시지" },
        { id: 4, name: "회원4", status: "상태메시지" },
    ]);

    const friendTodosByDate = [
        {
            date: new Date(2026, 3, 21),
            todos: [
                {
                    id: 1,
                    title: "React 복습하기",
                    memo: "useContext, customHook",
                    category: "공부",
                    dotColor: "#D9DFE4",
                    dotLetter: "",
                },
                {
                    id: 2,
                    title: "FastAPI 복습하기",
                    memo: "DB 연동 연습하기",
                    category: "공부",
                    dotColor: "#E89B9B",
                    dotLetter: "V",
                },
            ],
        },
    ];

    const handleNotification = () => setIsNotiOpen(true);
    const handleAdvancedSearch = () => alert("검색 옵션 열기");

    const handleFriendClick = (friend) => {
        setSelectedFriend(friend);
        setView("detail");
    };
    const handleBackToList = () => {
        setView("list");
        setSelectedFriend(null);
    };
    const handleAddFriend = () => setIsFriendAddOpen(true);

    // // 모든 분기에서 공용으로 렌더할 모달들
    // const SharedModals = () => (
    //     <>
    //         <NotificationModal
    //             isOpen={isNotiOpen}
    //             onClose={() => setIsNotiOpen(false)}
    //             notifications={notifications}
    //             onItemClick={(n) => alert(`"${n.title}" 상세 보기`)}
    //         />
    //         <FriendAddModal
    //             isOpen={isFriendAddOpen}
    //             onClose={() => setIsFriendAddOpen(false)}
    //             onSearch={searchUser}   
    //             onSendRequest={sendRequest}
    //         />
    //     </>
    // );

    const handleDeleteMember = async (member) => {
        const ok = await showWarningDialog({
            title: "회원을 삭제할까요?",
            text: "삭제된 회원은 복구할 수 없어요.",
        });
        if (ok) {
            setMembers((prev) => prev.filter((m) => m.id !== member.id));
            showSuccessAlert({
                title: "삭제 완료",
                text: `${member.name} 님을 삭제했어요.`,
            });
        }
    };

    // 공용 UI: 상단 벨 버튼
    const NotificationBell = () => (
        <button
            onClick={handleNotification}
            className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
        >
            {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
            <span className="w-5 h-5 block" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
        </button>
    );

    // 공용 UI: 검색 바
    const SearchBar = ({ placeholder }) => (
        <div className="flex gap-2">
            <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
                {/* 아이콘 위치: 돋보기 (bi-search) */}
                <span className="text-[#8B9BAA] text-xs">🔍</span>
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder={placeholder}
                    className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] focus:outline-none"
                />
            </div>
            <button
                onClick={handleAdvancedSearch}
                className="w-12 h-12 rounded-2xl bg-[#A8C8D8] flex items-center justify-center shadow-sm shrink-0"
                aria-label="상세 검색"
            >
                {/* 아이콘 위치: 사람+돋보기 (bi-person-add / bi-search-heart) */}
                <span className="w-5 h-5 block" />
            </button>
        </div>
    );

    // ====== 렌더: 친구 상세 (비관리자) ======
    if (!isAdmin && view === "detail" && selectedFriend) {
        const todos =
            friendTodosByDate.find((entry) =>
                isSameDay(entry.date, friendDetailDate)
            )?.todos || [];

        const studyDays = [
            new Date(2026, 3, 3),
            new Date(2026, 3, 7),
            new Date(2026, 3, 12),
            new Date(2026, 3, 25),
            new Date(2026, 3, 28),
        ];
        const workoutDays = [new Date(2026, 3, 9)];
        const dailyDays = [new Date(2026, 3, 5), new Date(2026, 3, 14)];

        const formattedFriendDate = format(friendDetailDate, "M월 d일", {
            locale: ko,
        });

        const handleFriendDateSelect = (date) => {
            if (!date) return;
            setFriendDetailDate(startOfDay(date));
        };

        return (
            <>
                {/* 헤더: 뒤로가기 + 친구 이름 */}
                <header className="px-6 pt-6 flex items-center justify-between">
                    <button
                        onClick={handleBackToList}
                        className="flex items-center gap-2"
                    >
                        {/* 아이콘 위치: 뒤로가기 (bi-chevron-left) */}
                        <h1 className="text-2xl font-bold text-[#3D4D5C]">
                            {selectedFriend.name}
                        </h1>
                    </button>
                    <NotificationBell />
                </header>

                <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                    {/* 캘린더 카드 (shadcn/ui Calendar) */}
                    <div className="bg-white rounded-2xl p-4 shadow-sm">
                        <Calendar
                            mode="single"
                            selected={friendDetailDate}
                            onSelect={handleFriendDateSelect}
                            locale={ko}
                            showOutsideDays
                            modifiers={{
                                study: studyDays,
                                workout: workoutDays,
                                daily: dailyDays,
                            }}
                            modifiersClassNames={{
                                study:
                                    "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#E88A8A]",
                                workout:
                                    "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#F4D58A]",
                                daily:
                                    "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#A8D5B4]",
                            }}
                            className="w-full"
                        />
                    </div>

                    {/* 친구의 할 일 */}
                    <div className="mt-6">
                        <h2 className="text-base font-bold text-[#3D4D5C]">
                            {selectedFriend.name}의 할 일
                        </h2>
                        <p className="text-xs text-[#8B9BAA] mt-1">
                            {formattedFriendDate} · {todos.length}개
                        </p>
                    </div>

                    <div className="mt-3 flex flex-col gap-3">
                        {todos.map((todo) => (
                            <div
                                key={todo.id}
                                className="w-full bg-white rounded-2xl p-4 shadow-sm"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start gap-3 flex-1">
                                        <div
                                            className="w-6 h-6 rounded-full shrink-0 mt-0.5 flex items-center justify-center"
                                            style={{ backgroundColor: todo.dotColor }}
                                        >
                                            {/* 아이콘 위치: 카테고리/완료 아이콘 */}
                                            {todo.dotLetter && (
                                                <span className="text-white text-xs font-bold">
                          {todo.dotLetter}
                        </span>
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-[#3D4D5C]">
                                                {todo.title}
                                            </p>
                                            {todo.memo && (
                                                <p className="text-xs text-[#8B9BAA] mt-1">
                                                    {todo.memo}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    <span className="text-[11px] text-[#87B4C4] bg-[#E4EEF3] px-2 py-0.5 rounded-full shrink-0">
                    {todo.category}
                  </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* <SharedModals /> */}
            </>
        );
    }

    // ====== 렌더: 관리자 - 회원 관리 ======
    if (isAdmin) {
        const filtered = members.filter((m) =>
            m.name.includes(searchQuery.trim())
        );

        return (
            <>
                <header className="px-6 pt-6 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-[#3D4D5C]">회원 관리</h1>
                    <NotificationBell />
                </header>

                <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                    <SearchBar placeholder="회원 검색" />

                    <div className="mt-4 flex flex-col gap-3">
                        {filtered.length === 0 ? (
                            <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                                검색 결과가 없어요.
                            </div>
                        ) : (
                            filtered.map((member) => (
                                <div
                                    key={member.id}
                                    className="bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 relative"
                                >
                                    <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0">
                                        {/* 아이콘 위치: 프로필 이미지 (bi-person-fill) */}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-[#3D4D5C]">
                                            {member.name}
                                        </p>
                                        <p className="text-xs text-[#8B9BAA] mt-1">
                                            {member.status}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteMember(member)}
                                        className="absolute right-4 bottom-3 px-4 py-1.5 rounded-full bg-[#E89B9B] text-[11px] font-semibold text-white"
                                    >
                                        삭제
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* <SharedModals /> */}
            </>
        );
    }

    // ====== 렌더: 비관리자 - 친구 목록 (기본) ======
    const filteredFriends = friends.filter((f) =>
        f.name.includes(searchQuery.trim())
    );

    return (
        <>
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">친구</h1>
                <NotificationBell />
            </header>

            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                <SearchBar placeholder="친구 검색" />

                <div className="mt-4 flex flex-col gap-3">
                    {filteredFriends.length === 0 ? (
                        <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                            검색 결과가 없어요.
                        </div>
                    ) : (
                        filteredFriends.map((friend) => (
                            <button
                                key={friend.id}
                                onClick={() => handleFriendClick(friend)}
                                className="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 text-left"
                            >
                                <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0">
                                    {/* 아이콘 위치: 프로필 이미지 (bi-person-fill) */}
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-[#3D4D5C]">
                                        {friend.name}
                                    </p>
                                    <p className="text-xs text-[#8B9BAA] mt-1">{friend.status}</p>
                                </div>
                            </button>
                        ))
                    )}
                </div>
            </div>

            {/* 플로팅 친구 추가 버튼 */}
            <button
                onClick={handleAddFriend}
                className="absolute right-6 bottom-28 w-12 h-12 rounded-full bg-[#A8C8D8] flex items-center justify-center shadow-lg"
                aria-label="친구 추가"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="none"
                    stroke="white"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    viewBox="0 0 24 24"
                >
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <line x1="19" y1="8" x2="19" y2="14" />
                    <line x1="22" y1="11" x2="16" y2="11" />
                </svg>
            </button>

            <NotificationModal
                isOpen={isNotiOpen}
                onClose={() => setIsNotiOpen(false)}
                notifications={notifications}
                onItemClick={(n) => alert(n.title)}
            />

            <FriendAddModal
                isOpen={isFriendAddOpen}
                onClose={() => setIsFriendAddOpen(false)}
                onSearch={searchUser}
                onSendRequest={sendRequest}
            />
        </>
    );
}
