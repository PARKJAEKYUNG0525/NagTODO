import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { showWarningDialog, showSuccessAlert } from "@/utils/alertUtils.js";
import FriendAddModal from "../../Components/Modal/FriendAddModal";
import NotificationBell from "../../Components/Notification";

import { useFriend } from "../../hooks/useFriend";
import { useAuth } from "../../hooks/useAuth";
import { useNotification } from "../../hooks/useNotification";

import api from "../../utils/api";

export default function Friend() {
    const { searchUser, sendRequest, friends, fetchFriends } = useFriend();
    const { user: currentUser } = useAuth();
    const { notifications, fetchNotifications } = useNotification();

    const [isAdmin, setIsAdmin] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    const [isFriendAddOpen, setIsFriendAddOpen] = useState(false);
    const navigate = useNavigate();

    // friendName을 state로 함께 넘김
    const handleFriendClick = (friend) => {
        const friendUserId =
            friend.requester_id === currentUser?.user_id
                ? friend.receiver_id
                : friend.requester_id;

        const friendName =
            friend.requester_id === currentUser?.user_id
                ? friend.receiver_username
                : friend.requester_username;

        navigate(`/friend/${friendUserId}`, { state: { friendName } });
    };

    const handleAddFriend = () => setIsFriendAddOpen(true);

    const handleFriendRequest = async (friend) => {
        const success = await sendRequest(friend.user_id, friend.username);
        if (success) {
            setIsFriendAddOpen(false);
        }
    };

    // ====== 관리자 뷰 ======
    if (isAdmin) {
        const filtered = friends.filter((m) => {
            const name =
                m.requester_id === currentUser?.user_id
                    ? m.receiver_username
                    : m.requester_username;
            return (name || "").includes(searchQuery.trim());
        });

        return (
            <>
                <header className="px-6 pt-6 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-[#3D4D5C]">회원 관리</h1>
                    <NotificationBell onAccept={fetchFriends} />
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
                                className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] cursor-text focus:outline-none"
                            />
                        </div>
                    </div>

                    <div className="mt-4 flex flex-col gap-3">
                        {filtered.length === 0 ? (
                            <div className="bg-white rounded-2xl py-10 text-center text-sm text-[#8B9BAA]">
                                검색 결과가 없어요.
                            </div>
                        ) : (
                            filtered.map((member) => {
                                const name =
                                    member.requester_id === currentUser?.user_id
                                        ? member.receiver_username
                                        : member.requester_username;
                                return (
                                    <div
                                        key={member.friend_id}
                                        className="bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 relative"
                                    >
                                        <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-[#3D4D5C]">{name}</p>
                                            <p className="text-xs text-[#8B9BAA] mt-1">
                                                {member.status === "수락" ? "친구" : member.status}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>
                <FriendAddModal
                    isOpen={isFriendAddOpen}
                    onClose={() => setIsFriendAddOpen(false)}
                    onSearch={searchUser}
                    onRequest={handleFriendRequest}
                />
            </>
        );
    }

    // ====== 일반 유저 친구 목록 ======
    const filteredFriends = friends.filter((f) => {
        const friendName =
            f.requester_id === currentUser?.user_id
                ? f.receiver_username
                : f.requester_username;
        return (friendName || "").includes(searchQuery.trim());
    });



return (
    <div className="flex-1 flex flex-col">
        <header className="px-6 pt-6 flex items-center justify-between">
            <h1 className="text-2xl font-bold text-[#3D4D5C]">친구</h1>
            <NotificationBell onAccept={fetchFriends} />
        </header>

            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                <div className="flex gap-2">
                    <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-2 shadow-sm">
                        <span className="text-[#8B9BAA] text-xs">🔍</span>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="친구 검색"
                            className="flex-1 text-sm text-[#3D4D5C] placeholder-[#B5BEC7] cursor-text focus:outline-none"
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
                            const friendName =
                                friend.requester_id === currentUser?.user_id
                                    ? friend.receiver_username
                                    : friend.requester_username;

                            const friendStatus =
                                friend.requester_id === currentUser?.user_id
                                    ? friend.receiver_status_message
                                    : friend.requester_status_message;

                            return (
                                <button
                                    key={friend.friend_id}
                                    onClick={() => handleFriendClick(friend)}
                                    className="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3 text-left cursor-pointer"
                                >
                                    <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                    
                                    <div className="flex flex-col">
                                            {/* 이름 */}
                                            <span className="text-sm font-bold text-[#3D4D5C]">
                                            {friendName}
                                            </span>
                                            
                                            {/* 상태메시지 (질문하신 부분) */}
                                            <span className="text-xs text-[#8B9BAA]">
                                            {friendStatus || friend.status_message || "상태메시지"}
                                            </span>
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
                className="absolute right-6 bottom-28 w-12 h-12 rounded-full bg-[#A8C8D8] flex items-center justify-center shadow-lg cursor-pointer"
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
            <FriendAddModal
                isOpen={isFriendAddOpen}
                onClose={() => setIsFriendAddOpen(false)}
                onSearch={searchUser}
                onRequest={handleFriendRequest}
            />
        </div>
    );
}