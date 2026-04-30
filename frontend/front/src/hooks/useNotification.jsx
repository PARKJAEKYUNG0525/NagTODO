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
            setNotifications((res.data || []).filter(n => !n.is_read));
        } catch (e) {
            console.error("알림 조회 실패:", e);
        }
    }, [currentUser]);

    useEffect(() => {
        fetchNotifications();
    }, [fetchNotifications]);

    return {
        notifications,
        fetchNotifications,
    };
};