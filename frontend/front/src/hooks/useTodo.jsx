import api from "../utils/api.js";
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtiles.js";

import React, {useCallback, useState} from 'react';
import {showErrorAlert} from "@/utils/alertUtiles.js";

export const useTodo = () => {

    const [loading, setLoading] = useState(false);

    // C 생성
    const createTodo = useCallback(async (newTodo) => {
        setLoading(true);
        try {
            const response = await api.post("/todos", newTodo);

            if (response.status === 200 || response.status === 201) {
                showSuccessAlert("게시글이 생성되었습니다.");
                return response.data;
            }
        }
        catch (error) {
            showErrorAlert("게시글을 생성할 수 없습니다.", error.message);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, []);


    // R 조회 - todo 전체 조회
    const getAllTodos = useCallback(async() => {
        setLoading(true);

        try {
            const response = await api.get("/user/{userid}")

            if (response.status === 200) {
                return response.data;
            }
            return [];
        }
        catch (error) {
            showWarningAlert("게시글을 불러올 수 없습니다.", error.message);
        }
        finally {
            setLoading(false);
        }
    }, [])


    return {loading, getAllTodos, createTodo};
};

export default useTodo;