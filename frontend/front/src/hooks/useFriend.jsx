import { useState, useCallback, useEffect } from "react";
import api from "../utils/api";
import { showSuccessAlert, showWarningAlert } from "../utils/alertUtils.js";
import { useAuth } from "./useAuth";

export const useFriend = () => {
    const [friends, setFriends] = useState([]);          // 수락된 친구 목록
    const [receivedRequests, setReceivedRequests] = useState([]); // 받은 신청 목록
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSearching, setIsSearching] = useState(false); // 검색 전용 로딩 상태 추가

    const { user: currentUser } = useAuth(); 

    // 받은 신청 목록 조회
    const fetchReceivedRequests = useCallback(async () => {
        setIsLoading(true);
        try {
            // Router: @router.get("/received")
            const response = await api.get("/friends/received");
            if (response.status === 200) {
                setReceivedRequests(response.data);
                return response.data;
            }
        } catch (error) {
            console.error(error);
            setError("신청 목록을 불러오지 못했습니다.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 이메일 또는 닉네임으로 유저 검색 (Search)
    const searchUser = useCallback(async (query) => {
        if (!query.trim()) return [];
        
        setIsSearching(true);
        try {
        setError("");
        const response = await api.get(`/users/search?query=${query}`);
        console.log("검색 결과:", response.data);
        
        if (response.status === 200) {
            return Array.isArray(response.data) ? response.data : [response.data];
        }
        return [];
        } catch (error) {
        console.error("검색 실패:", error.response?.data); 
        return [];
        } finally {
        setIsSearching(false);
        }
    }, []);

    // 친구 신청 보내기
    const sendRequest = async (receiverId, username) => { // ← username 추가
        try {
            setError("");
            const response = await api.post("/friends/", { receiver_id: receiverId });
            
            if (response.status === 201) {
                await api.post("/notifications/", {
                    user_id: receiverId,
                    title: "새 친구 요청",
                    content: `friend_request:${response.data.friend_id}:${currentUser.username}`, // ← 닉네임 저장
                });
                showSuccessAlert({ title: "신청 완료", text: "성공적으로 요청을 보냈습니다." });
                return true;
            }
        } catch (error) {
            const detail = error.response?.data.detail || "신청에 실패했습니다.";
            setError(detail);
            showWarningAlert("요청 실패", detail);
            return false;
        }
    };

    // 4. 컴포넌트 마운트 시 자동 실행 (초기화)
    useEffect(() => {
        fetchReceivedRequests();
    }, [fetchReceivedRequests]);

    // 수락된 친구 목록 조회
    const fetchFriends = useCallback(async () => {
        try {
            const res = await api.get("/friends/accepted"); // 백엔드 엔드포인트
            setFriends(res.data || []);
        } catch (e) {
            console.error("친구 목록 조회 실패:", e);
        }
    }, []);


    const deleteFriend = async (friendId) => {
        try {
            await api.delete(`/friends/${friendId}`);
            await fetchFriends(); // 목록 새로고침
            return true;
        } catch (err) {
            console.error("친구 삭제 실패:", err);
            return false;
        }
    };

    const deleteUser = async (userId) => {
        try {
            await api.delete(`/users/${userId}`);
            return true;
        } catch (err) {
            console.error("회원 삭제 실패:", err);
            return false;
        }
    };

    useEffect(() => {
        fetchFriends();
    }, [fetchFriends]);    

    // 외부로 노출할 객체
    return {
        friends,
        receivedRequests,
        fetchFriends,
        error,
        setError,
        isLoading,
        isSearching,
        searchUser,
        sendRequest,
        fetchReceivedRequests,
        deleteFriend,
        deleteUser
    };
};