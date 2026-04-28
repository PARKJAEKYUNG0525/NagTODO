import { useState, useCallback, useEffect } from "react";
import api from "../utils/api";
import { showSuccessAlert, showWarningAlert } from "../utils/alertUtiles.js";

export const useFriend = () => {
    const [friends, setFriends] = useState([]);          // 수락된 친구 목록
    const [receivedRequests, setReceivedRequests] = useState([]); // 받은 신청 목록
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSearching, setIsSearching] = useState(false); // 검색 전용 로딩 상태 추가

    // 1. 받은 신청 목록 조회 (R)
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

    // 2. 이메일 또는 닉네임으로 유저 검색 (Search)
    const searchUser = useCallback(async (query) => {
        if (!query.trim()) return [];
        
        setIsSearching(true);
        try {
            setError("");
            const response = await api.get(`/friends/search?query=${query}`);
            if (response.status === 200) {
                // 결과가 단일 객체라면 [response.data], 배열이라면 response.data
                return Array.isArray(response.data) ? response.data : [response.data];
            }
            return [];
        } catch (error) {
            // 실시간 검색 시에는 Alert를 띄우지 않고 에러만 기록
            console.error("검색 실패:", error.response?.data.detail);
            return [];
        } finally {
            setIsSearching(false);
        }
    }, []);

    // 3. 친구 신청 보내기 (C)
    const sendRequest = async (receiverId) => {
        try {
            setError("");
            // Router: @router.post("/") -> FriendUpdate { "receiver_id": int }
            const response = await api.post("/friends/", { receiver_id: receiverId });
            
            if (response.status === 201) {
                showSuccessAlert({title:"신청 완료", text:"성공적으로 요청을 보냈습니다."});
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

    // 외부로 노출할 객체
    return {
        friends,
        receivedRequests,
        error,
        setError,
        isLoading,
        searchUser,
        sendRequest,
        fetchReceivedRequests
    };
};