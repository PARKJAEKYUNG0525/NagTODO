import { useState, useCallback, useEffect } from "react";
import api from "../utils/api";
import { useAuth } from "./useAuth";

export const useNotification = () => {
    const [notifications, setNotifications] = useState([]);
    const { user: currentUser } = useAuth();

    // 알림 조회
    const fetchNotifications = useCallback(async () => {
        if (!currentUser?.user_id) return;
        try {
            const res = await api.get(`/notifications/user/${currentUser.user_id}`);
            setNotifications(Array.isArray(res.data) ? res.data : []);
        } catch (e) {
            console.error("알림 조회 실패:", e);
        }
    }, [currentUser]);

        // 개별 알림 전송
    const sendNotification = useCallback(async (userId, title, content) => {
        try {
            await api.post("/notifications/", {
                user_id: userId,
                title,
                content,
                type: "system",
            });
            return true;
        } catch (e) {
            console.error("알림 전송 실패:", e);
            return false;
        }
    }, []);

    // 전체 알림 전송
    const sendNotificationToAll = useCallback(async (users, title, content) => {
        try {
            await Promise.all(
                users.map((user) =>
                    api.post("/notifications/", {
                        user_id: user.user_id,
                        title,
                        content,
                        type: "system",
                    })
                )
            );
            return true;
        } catch (e) {
            console.error("전체 알림 전송 실패:", e);
            return false;
        }
    }, []);

    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    return {
        notifications,
        fetchNotifications,
        sendNotification,
        sendNotificationToAll,
    };
};