import React, { useState,useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { showWarningDialog, showWarningUserDialog, showSuccessAlert } from "@/utils/alertUtils.js";
import FriendAddModal from "../../Components/Modal/FriendAddModal";
import NotificationBell from "../../Components/Notification";

import { useFriend } from "../../hooks/useFriend";
import { useAuth } from "../../hooks/useAuth";
import { useImg } from "@/hooks/useImg";

import api from "../../utils/api";

export default function Friend() {
    const { searchUser, sendRequest, friends, fetchFriends, deleteFriend, deleteUser  } = useFriend();
    const { user: currentUser } = useAuth();
    const { currentBg, setCurrentBg, getUserBg } = useImg();

    // const [isAdmin, setIsAdmin] = useState(false);
    const isAdmin = currentUser?.role === "admin";
    const [allUsers, setAllUsers] = useState([]);
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

    const handleDeleteFriend = async (e, friendId) => {
        e.stopPropagation(); // 카드 클릭(navigate) 이벤트 막기
        const confirmed = await showWarningDialog();
        if (!confirmed) return;
        const success = await deleteFriend(friendId);
        if (success) showSuccessAlert({ title: "친구가 삭제되었어요." });
    };

    const handleDeleteUser = async (e, userId) => {
        e.stopPropagation();
        const confirmed = await showWarningUserDialog();
        if (!confirmed) return;
        const success = await deleteUser(userId);
        if (success) {
            setAllUsers((prev) => prev.filter((u) => u.user_id !== userId));
            showSuccessAlert({ title: "회원이 삭제되었어요." });
        }
    };

    useEffect(() => {
        if (isAdmin) {
            api.get("/users/user").then((res) => setAllUsers(res.data));
        }
    }, [isAdmin]);

    // ====== 관리자 뷰 ======
    if (isAdmin) {
        const filtered = allUsers.filter((u) =>
            (u.username || "").includes(searchQuery.trim())
        );

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
                            filtered.map((user) => (
                                <div
                                    key={user.user_id}
                                    className="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3"
                                >
                                    <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                    <div className="flex-1 flex flex-col">
                                        <span className="text-sm font-bold text-[#3D4D5C]">
                                            {user.username}
                                        </span>
                                        <span className="text-xs text-[#8B9BAA]">
                                            {user.status_message || "상태메시지"}
                                        </span>
                                    </div>
                                    <button
                                        onClick={(e) => handleDeleteUser(e, user.user_id)}
                                        className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-[#B5BEC7] hover:bg-red-50 hover:text-red-400 transition-colors"
                                        aria-label="회원 삭제"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                            fill="none" stroke="currentColor" strokeWidth="2"
                                            strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                                            <polyline points="3 6 5 6 21 6" />
                                            <path d="M19 6l-1 14H6L5 6" />
                                            <path d="M10 11v6M14 11v6" />
                                            <path d="M9 6V4h6v2" />
                                        </svg>
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
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
    <div className="flex-1 flex flex-col bg-[#F4F7FA] bg-cover bg-center"
         style={
             currentBg
                 ? {
                     backgroundImage: `linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url(${api.defaults.baseURL}${currentBg.file_url})`,
                 }
                 : undefined
         }
    >
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
                                <div
                                    key={friend.friend_id}
                                    className="w-full bg-white rounded-2xl p-4 shadow-sm flex items-center gap-3"
                                >
                                    {/* 기존 button을 div로 감싸고, 클릭 영역을 분리 */}
                                    <button
                                        onClick={() => handleFriendClick(friend)}
                                        className="flex items-center gap-3 flex-1 text-left cursor-pointer"
                                    >
                                        <div className="w-12 h-12 rounded-full bg-[#A8C8D8] shrink-0" />
                                        <div className="flex flex-col">
                                            <span className="text-sm font-bold text-[#3D4D5C]">
                                                {friendName}
                                            </span>
                                            <span className="text-xs text-[#8B9BAA]">
                                                {friendStatus || friend.status_message || "상태메시지"}
                                            </span>
                                        </div>
                                    </button>

                                    {/* 삭제 버튼 */}
                                    <button
                                        onClick={(e) => handleDeleteFriend(e, friend.friend_id)}
                                        className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-[#B5BEC7] hover:bg-red-50 hover:text-red-400 transition-colors"
                                        aria-label="친구 삭제"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                            fill="none" stroke="currentColor" strokeWidth="2"
                                            strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                                            <polyline points="3 6 5 6 21 6" />
                                            <path d="M19 6l-1 14H6L5 6" />
                                            <path d="M10 11v6M14 11v6" />
                                            <path d="M9 6V4h6v2" />
                                        </svg>
                                    </button>
                                </div>
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