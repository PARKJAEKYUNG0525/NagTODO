import api from "../utils/api.js";
import {showWarningAlert} from "../utils/alertUtils.js";
import { useCallback, useState } from 'react';

export const useCategory = () => {
    const [ctLoading, setCtLoading] = useState(false);

    // R 전체 조회
    const getCategory = useCallback(async() => {
        setCtLoading(true);
        try {
            const response = await api.get("/category/")
            if (response.status === 200) return response.data;
            return [];
        } catch (error) {
            showWarningAlert({ title: "카테고리를 불러올 수 없습니다.", text: error.message });
            return null;
        } finally {
            setCtLoading(false);
        }
    }, []);

    // C 추가 
    const addCategory = useCallback(async(name) => {
        setCtLoading(true);
        try {
            const response = await api.post("/category/", { name });
            if (response.status === 201) return response.data; // category_id, name 반환
            return null;
        } catch (error) {
            showWarningAlert({ title: "카테고리 추가 실패", text: error.message });
            return null;
        } finally {
            setCtLoading(false);
        }
    }, []);

    // U 수정 - PATCH /{category_id}
    const updateCategory = useCallback(async(category_id, name) => {
        setCtLoading(true);
        try {
            const response = await api.patch(`/category/${category_id}`, { name });
            if (response.status === 200) return true;
            return false;
        } catch (error) {
            showWarningAlert({ title: "카테고리 수정 실패", text: error.message });
            return false;
        } finally {
            setCtLoading(false);
        }
    }, []);

    // D 삭제 - 개별 삭제
    const deleteCategory = useCallback(async(category_id) => {
        setCtLoading(true);
        try {
            const response = await api.delete(`/category/${category_id}`);
            if (response.status === 200) return true;
            return false;
        } catch (error) {
            showWarningAlert({ title: "카테고리 삭제 실패", text: error.message });
            return false;
        } finally {
            setCtLoading(false);
        }
    }, []);

    return { ctLoading, getCategory, addCategory, updateCategory, deleteCategory };
};

export default useCategory;