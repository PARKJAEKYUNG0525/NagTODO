import api from "../utils/api.js";
<<<<<<< HEAD
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtils.js";

import {useAuth} from "@/hooks/useAuth.jsx";
import React, {useCallback, useState} from 'react';
=======
import { showWarningAlert, showSuccessAlert } from "../utils/alertUtiles.js";

import { useAuth } from "@/hooks/useAuth.jsx";
import React, { useCallback, useState } from 'react';
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247

export const useTodo = () => {

    const { user } = useAuth();

    const [todoLoading, setTodoLoading] = useState(false);

    // C 생성
    const createTodo = useCallback(async (newTodo) => {
        setTodoLoading(true);
        try {
            const response = await api.post("/todos", newTodo);

            if (response.status === 200 || response.status === 201) {
<<<<<<< HEAD
                showSuccessAlert("게시글이 생성되었습니다.");
=======
                showSuccessAlert({ title: "게시글이 생성되었습니다." });
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247
                return response.data;
            }
        }
        catch (error) {
<<<<<<< HEAD
            showWarningAlert("게시글을 생성할 수 없습니다.", error.message);
=======
            showWarningAlert({ title: "게시글을 생성할 수 없습니다.", text: error.message });
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247
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

    return { todoLoading, getAllTodos, createTodo };
};

<<<<<<< HEAD
export default useTodo;
=======
export default useTodo;
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247
