import api from "../utils/api.js";
import { useCallback, useState } from "react";

export const useCloth = () => {
    const [clothLoading, setClothLoading] = useState(false);
    const [currentCloth, setCurrentCloth] = useState(null);

    // 전체 cloth 목록
    const getAllCloths = useCallback(async () => {
        setClothLoading(true);
        try {
            const response = await api.get("/cloths/");
            if (response.status === 200 || response.status === 201) {
                return response.data;
            }
            return [];
        } catch (error) {
            console.error("프로필 목록 불러오기 실패:", error);
            return [];
        } finally {
            setClothLoading(false);
        }
    }, []);

    // 현재 사용자의 cloth 조회 (객체 매핑까지)
    const getUserCloth = useCallback(async () => {
        try {
            const userRes = await api.get("/users/me");
            if (!userRes.data.cloth_id) {
                setCurrentCloth(null);
                return;
            }
            const clothsRes = await api.get("/cloths");
            const myCloth = (clothsRes.data ?? []).find(
                (c) => c.cloth_id === userRes.data.cloth_id
            );
            setCurrentCloth(myCloth ?? null);
        } catch (err) {
            console.warn("프로필 로드 실패:", err);
            setCurrentCloth(null);
        }
    }, []);

    // 현재 사용자의 cloth 변경 (낙관적 업데이트)
    const setUserCloth = useCallback(async (cloth) => {
        setCurrentCloth(cloth);   // 즉시 UI 반영
        try {
            await api.patch("/users/me", { cloth_id: cloth?.cloth_id ?? null });
        } catch (err) {
            console.warn("프로필 저장 실패:", err);
            // 실패 시 롤백하려면 이전 값 백업 필요. 일단 silent.
        }
    }, []);

    return {
        clothLoading,
        currentCloth,
        getAllCloths,
        getUserCloth,
        setUserCloth,
    };
};

export default useCloth;