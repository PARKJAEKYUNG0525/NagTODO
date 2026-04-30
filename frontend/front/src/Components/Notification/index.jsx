import React, { useState } from "react";
import { BsFillBellFill } from "react-icons/bs";
import NotificationModal from "../Modal/NotificationModal";
import { useNotification } from "../../hooks/useNotification";
import { useFriend } from "../../hooks/useFriend";
import { showSuccessAlert } from "@/utils/alertUtils.js";
import api from "../../utils/api";

export default function NotificationBell() {
    const { notifications, fetchNotifications } = useNotification();
    const { fetchFriends } = useFriend();
    const [isOpen, setIsOpen] = useState(false);

    const handleAccept = async (notification) => {
        try {
            const friendId = notification.content.split(":")[1];
            await api.patch(`/friends/${friendId}`, { status: "수락" });
            await api.patch(`/notifications/${notification.notification_id}`, { is_read: true });
            fetchNotifications();
            fetchFriends();
            showSuccessAlert({ title: "친구 추가!", text: "친구가 되었어요!" });
        } catch (e) {
            console.error("수락 실패:", e);
        }
    };

    const handleReject = async (notification) => {
        try {
            const friendId = notification.content.split(":")[1];
            await api.delete(`/friends/${friendId}`);  
            await api.patch(`/notifications/${notification.notification_id}`, { is_read: true });
            fetchNotifications();
        } catch (e) {
            console.error("거절 실패:", e);
        }
    };

    return (
        <>
            <button
                onClick={() => setIsOpen(true)}
                className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
            >
                <BsFillBellFill className="w-5 h-5 text-white" />
                {notifications.length > 0 && (
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
                )}
            </button>

            <NotificationModal
                isOpen={isOpen}
                onClose={() => setIsOpen(false)}
                notifications={notifications}
                onAccept={handleAccept}
                onReject={handleReject}
            />
        </>
    );
}