import api from "../utils/api.js";
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtiles.js";

import {useAuth} from "@/hooks/useAuth.jsx";
import React, {useCallback, useState} from 'react';

export const useTodo = () => {

    const { user } = useAuth();

    const [todoLoading, setTodoLoading] = useState(false);

    // C 생성
    const createTodo = useCallback(async (newTodo) => {
        setTodoLoading(true);
        try {
            const response = await api.post("/todos", newTodo);

            if (response.status === 200 || response.status === 201) {
                showSuccessAlert("게시글이 생성되었습니다.");
                return response.data;
            }
        }
        catch (error) {
            showWarningAlert("게시글을 생성할 수 없습니다.", error.message);
            return null;
        }
        finally {
            setTodoLoading(false);
        }
    }, []);


    // R 조회 - todo 전체 조회
    const getAllTodos = useCallback(async() => {
        setTodoLoading(true);

        if (!user?.user_id) return;

        try {
            const response = await api.get("/user/{userid}")

            if (response.status === 200) {
                return response.data;
            }
            return [];
        }
        catch {

        }
        finally {
            setTodoLoading(false);
        }
    }, [user?.user_id])

    return {todoLoading, getAllTodos, createTodo};
};

export default useTodo;