import React, { useState, useEffect } from "react";
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";
import { showWarningDialog, showSuccessAlert } from "@/utils/alertUtiles.js";
import FriendAddModal from "../../Components/Modal/FriendAddModal";
import NotificationModal from "../../Components/Modal/NotificationModal";

import { useFriend } from "../../hooks/useFriend";

export default function Friend() {
    const [friends, setFriends] = useState([]);
    const [view, setView] = useState("list");
    const [selectedFriend, setSelectedFriend] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const { searchUser } = useFriend();


    // 모달 상태
    const [isFriendAddOpen, setIsFriendAddOpen] = useState(false);
    const [isNotiOpen, setIsNotiOpen] = useState(false);



    // 알림 데이터
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



    const handleNotification = () => setIsNotiOpen(true);
    const handleAdvancedSearch = () => alert("검색 옵션 열기");

    const handleAddFriend = () => setIsFriendAddOpen(true);



    // 공용 UI: 상단 벨 버튼
    const NotificationBell = () => (
        <button
            onClick={handleNotification}
            className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
        >
            <span className="w-5 h-5 block" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
        </button>
    );

    // 공용 UI: 검색 바
    const SearchBar = ({ placeholder }) => (
        <div className="flex gap-2">
            <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
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
                <span className="w-5 h-5 block" />
            </button>
        </div>
    );



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
                                <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-[#3D4D5C]">{friend.name}</p>
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
                onItemClick={(n) => alert(`"${n.title}" 상세 보기`)}
            />
            <FriendAddModal
                isOpen={isFriendAddOpen}
                onClose={() => setIsFriendAddOpen(false)}
                onSearch={searchUser}
            />
        </>
    );
}