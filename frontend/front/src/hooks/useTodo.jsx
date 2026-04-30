import api from "../utils/api.js";
import {showWarningAlert} from "../utils/alertUtils.js";

import { useAuth } from "@/hooks/useAuth.jsx";
import React, { useCallback, useState } from 'react';

export const useTodo = () => {

    const { user } = useAuth();

    const [todoLoading, setTodoLoading] = useState(false);

    // C 생성
    const createTodo = useCallback(async (newTodo) => {
        setTodoLoading(true);
        try {
            // axios는 2xx 응답을 resolve로 처리하므로 별도 status 체크 불필요
            const response = await api.post("/todos", newTodo);
            return response.data;
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
    const getAllTodos = useCallback(async(targetUserId) => {
        const id = targetUserId ?? user?.user_id;
        if (!id) return;

        setTodoLoading(true);

        try {
            const response = await api.get(`/todos/user/${id}`);
            return response.data;
        }
        catch (error) {
            console.warn("할 일 목록을 불러올 수 없습니다.", error.message);
            return [];
        }
        finally {
            setTodoLoading(false);
        }
    }, [user?.user_id])

    // U 수정 - todo 단건 수정
    const updateTodo = useCallback(async (todoId, data) => {
        setTodoLoading(true);
        try {
            const response = await api.patch(`/todos/${todoId}`, data);
            return response.data;
        } catch (error) {
            showWarningAlert({ title: "할 일을 수정할 수 없습니다.", text: error.message });
            return null;
        } finally {
            setTodoLoading(false);
        }
    }, []);

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

    return { todoLoading, getAllTodos, createTodo, updateTodo, deleteTodo };
};

export default useTodo;