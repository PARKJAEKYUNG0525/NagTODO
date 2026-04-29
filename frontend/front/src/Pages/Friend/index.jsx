import React, { useState, useEffect, useCallback } from "react"; 
import { Calendar } from "@/components/ui/calendar";
import { format, isSameDay, startOfDay } from "date-fns";
import { ko } from "date-fns/locale";
import { showWarningDialog, showSuccessAlert } from "@/utils/alertUtils.js";
import FriendAddModal from "../../Components/Modal/FriendAddModal";
import NotificationModal from "../../Components/Modal/NotificationModal";

import { useFriend } from "../../hooks/useFriend";
import { useAuth } from "../../hooks/useAuth"; 
import { useNotification } from "../../hooks/useNotification";

import api from "../../utils/api"; 

export default function Friend() {
    // const [friends, setFriends] = useState([]);
    const [isAdmin, setIsAdmin] = useState(false);                              // 관리자 여부 상태
    const [view, setView] = useState("list");                                   // 현재 화면 (list / detail)
    const [selectedFriend, setSelectedFriend] = useState(null);                 // 선택된 친구
    const [searchQuery, setSearchQuery] = useState("");                         // 검색어 상태

    const { searchUser, sendRequest, friends, fetchFriends } = useFriend();     // 친구 관련 로직 hooks
    const { user: currentUser } = useAuth();                                    // 로그인 유저 정보 hooks
    const { notifications, fetchNotifications } = useNotification();            // 알림 hooks

    const [friendDetailDate, setFriendDetailDate] = useState(
        startOfDay(new Date(2026, 3, 21))
    );                                                                           // 친구 상세 날짜

    // 모달 상태
    const [isFriendAddOpen, setIsFriendAddOpen] = useState(false);              // 친구 추가 모달
    const [isNotiOpen, setIsNotiOpen] = useState(false);                        // 알림 모달

    // 컴포넌트 로드시 알림 불러오기
    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    // 관리자 체크 (현재는 항상 false)
    useEffect(() => {
        const checkAdmin = () => false;
        setIsAdmin(checkAdmin());
    }, []);


    const handleNotification = () => setIsNotiOpen(true);                       // 알림 모달 열기

    const handleFriendClick = (friend) => {
        setSelectedFriend(friend);
        setView("detail");
    };
    const handleBackToList = () => {
        setView("list");
        setSelectedFriend(null);
    };
    const handleAddFriend = () => setIsFriendAddOpen(true);                     // 친구 추가 모달 열기

    // 친구 요청 보내기
    const handleFriendRequest = async (friend) => { 
        const success = await sendRequest(friend.user_id, friend.username);
        if (success) {
            setIsFriendAddOpen(false);
        }
    };

    // 친구 요청 수락
    const handleAcceptFriend = async (notification) => {
        try {
            const friendId = notification.content.split(":")[1];
            await api.patch(`/friends/${friendId}`, { status: "수락" });
            await api.patch(`/notifications/${notification.notification_id}`, { is_read: true });
            fetchNotifications();
            fetchFriends(); // ← 친구 목록 갱신
            showSuccessAlert({ title: "친구 추가!", text: "친구가 되었어요!" });
        } catch (e) {
            console.error("수락 실패:", e);
        }
    };

    // 친구 요청 거절
    const handleRejectFriend = async (notification) => {
        try {
            const friendId = notification.content.split(":")[1];
            await api.patch(`/friends/${friendId}`, { status: "거절" });
            await api.patch(`/notifications/${notification.notification_id}`, { is_read: true });
            fetchNotifications();
        } catch (e) {
            console.error("거절 실패:", e);
        }
    };

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
    <div className="flex gap-2">
        <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
            <span className="text-[#8B9BAA] text-xs">🔍</span>
            <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="친구검색"
                className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] focus:outline-none"
            />
        </div>
    </div>


    // ====== 렌더: 친구 상세 (비관리자) ======
    if (!isAdmin && view === "detail" && selectedFriend) {
        const todos =
            friendTodosByDate.find((entry) =>
                isSameDay(entry.date, friendDetailDate)
            )?.todos || [];
        const formattedFriendDate = format(friendDetailDate, "M월 d일", {
            locale: ko,
        });

        const handleFriendDateSelect = (date) => {
            if (!date) return;
            setFriendDetailDate(startOfDay(date));
        };

        return (
            <>
                <header className="px-6 pt-6 flex items-center justify-between">
                    <button onClick={handleBackToList} className="flex items-center gap-2">
                        <h1 className="text-2xl font-bold text-[#3D4D5C]">
                            {selectedFriend.name}
                        </h1>
                    </button>
                    <NotificationBell />
                </header>

                <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
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
                                study: "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#E88A8A]",
                                workout: "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#F4D58A]",
                                daily: "relative after:content-[''] after:absolute after:bottom-1 after:left-1/2 after:-translate-x-1/2 after:w-1 after:h-1 after:rounded-full after:bg-[#A8D5B4]",
                            }}
                            className="w-full"
                        />
                    </div>

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
                            <div key={todo.id} className="w-full bg-white rounded-2xl p-4 shadow-sm">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start gap-3 flex-1">
                                        <div
                                            className="w-6 h-6 rounded-full shrink-0 mt-0.5 flex items-center justify-center"
                                            style={{ backgroundColor: todo.dotColor }}
                                        >
                                            {todo.dotLetter && (
                                                <span className="text-white text-xs font-bold">
                                                    {todo.dotLetter}
                                                </span>
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-[#3D4D5C]">{todo.title}</p>
                                            {todo.memo && (
                                                <p className="text-xs text-[#8B9BAA] mt-1">{todo.memo}</p>
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
                <NotificationModal
                    isOpen={isNotiOpen}
                    onClose={() => setIsNotiOpen(false)}
                    notifications={notifications}
                    onItemClick={(n) => console.log(n)}
                    onAccept={handleAcceptFriend}
                    onReject={handleRejectFriend}
                />
                <FriendAddModal
                    isOpen={isFriendAddOpen}
                    onClose={() => setIsFriendAddOpen(false)}
                    onSearch={searchUser}
                    onRequest={handleFriendRequest}
                />
            </>
        );
    }

    // 관리자 - 회원 검색 
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
                    <div className="flex gap-2">
                        <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
                            <span className="text-[#8B9BAA] text-xs">🔍</span>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="회원 검색"
                                className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] focus:outline-none"
                            />
                        </div>
                    </div>

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
                                    <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-[#3D4D5C]">{member.name}</p>
                                        <p className="text-xs text-[#8B9BAA] mt-1">{member.status === "수락" ? "친구" : member.status}</p>
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
                <NotificationModal
                    isOpen={isNotiOpen}
                    onClose={() => setIsNotiOpen(false)}
                    notifications={notifications}
                    onItemClick={(n) => console.log(n)}
                    onAccept={handleAcceptFriend}
                    onReject={handleRejectFriend}
                />
                <FriendAddModal
                    isOpen={isFriendAddOpen}
                    onClose={() => setIsFriendAddOpen(false)}
                    onSearch={searchUser}
                    onRequest={handleFriendRequest}
                />
            </>
        );
    }

    // 사용자 친구(친구되어있는 사람만) 검색 
    const filteredFriends = friends.filter((f) => {
        const friendName = f.requester_id === currentUser?.user_id
            ? f.receiver_username
            : f.requester_username;
        return (friendName || "").includes(searchQuery.trim());
    });
    
return (
    <>
        <header className="px-6 pt-6 flex items-center justify-between">
            <h1 className="text-2xl font-bold text-[#3D4D5C]">친구</h1>
            <NotificationBell />
        </header>

        <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
            <div className="flex gap-2">
                <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
                    <span className="text-[#8B9BAA] text-xs">🔍</span>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="회원 검색"
                        className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] focus:outline-none"
                    />
                </div>
            </div>

            <div className="mt-4 flex flex-col gap-3">
                {filteredFriends.length === 0 ? (
                    <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                        검색 결과가 없어요.
                    </div>
                ) : (
                    filteredFriends.map((friend) => {
                        const friendName = friend.requester_id === currentUser?.user_id
                            ? friend.receiver_username
                            : friend.requester_username;

                        return (
                            <button
                                key={friend.friend_id}
                                onClick={() => handleFriendClick(friend)}
                                className="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 text-left"
                            >
                                <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                <div className="flex-1">
                                    <p className="text-sm font-bold text-[#3D4D5C]">{friendName}</p>
                                    <p className="text-xs text-[#8B9BAA] mt-1">{friend.status === "수락" ? "친구" : friend.status}</p>
                                </div>
                            </button>
                        );
                    })
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
                onItemClick={(n) => console.log(n)}
                onAccept={handleAcceptFriend}
                onReject={handleRejectFriend}
            />
            <FriendAddModal
                isOpen={isFriendAddOpen}
                onClose={() => setIsFriendAddOpen(false)}
                onSearch={searchUser}
                onRequest={handleFriendRequest}
            />
        </>
    );
}