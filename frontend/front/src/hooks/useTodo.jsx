import api from "../utils/api.js";
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtils.js";

import { useAuth } from "@/hooks/useAuth.jsx";
import React, { useCallback, useState } from 'react';

export const useTodo = () => {

    const { user } = useAuth();

    const [todoLoading, setTodoLoading] = useState(false);

    // C 생성
    const createTodo = useCallback(async (newTodo) => {
        setTodoLoading(true);
        try {
            const response = await api.post("/todos", newTodo);

            if (response.status === 200 || response.status === 201) {
                showSuccessAlert({title: "게시글이 생성되었습니다."});
                return response.data;
            }
        }
        catch (error) {
            showWarningAlert({ title: "게시글을 생성할 수 없습니다.", text: error.message });
            return null;
        }
        finally {
            setTodoLoading(false);
        }
    }, []);


    // R 조회 - todo 전체 조회
    const getAllTodos = useCallback(async() => {
        if (!user?.user_id) return;

        setTodoLoading(true);

        try {
            const response = await api.get(`/todos/user/${user.user_id}`)

            if (response.status === 200 || response.status === 201) {
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

    // D 삭제 - todo 단건 삭제
    const deleteTodo = useCallback(async (todoId) => {
        setTodoLoading(true);
        try {
            await api.delete(`/todos/${todoId}`);
            return true;
        } catch (error) {
            showWarningAlert({ title: "할 일을 삭제할 수 없습니다.", text: error.message });
            return false;
        } finally {
            setTodoLoading(false);
        }
    }, []);

    return { todoLoading, getAllTodos, createTodo, deleteTodo };
};

export default useTodo;