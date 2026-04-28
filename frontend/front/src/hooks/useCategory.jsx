import api from "../utils/api.js";
<<<<<<< HEAD
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtils.js";

import React, {useCallback, useState} from 'react';
=======
import { showWarningAlert } from "../utils/alertUtiles.js";

import React, { useCallback, useState } from 'react';
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247

export const useCategory = () => {

    const [ctLoading, setCtLoading] = useState(false);

    // R 조회 - Category 조회
    const getCategory = useCallback(async() => {
        setCtLoading(true);

        try {
            const response = await api.get("/category/")

            if (response.status === 200) {
                return response.data;
            }
            return [];
        }
        catch (error){
<<<<<<< HEAD
            showWarningAlert("게시글을 생성할 수 없습니다.", error.message);
=======
            showWarningAlert({ title: "카테고리를 불러올 수 없습니다.", text: error.message });
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247
            return null;
        }
        finally {
            setCtLoading(false);
        }
    }, [])

    return { ctLoading, getCategory };
};

<<<<<<< HEAD
export default useCategory;
=======
export default useCategory;
>>>>>>> 85cd134ffdf55ba4a575c91ffc79de9699d6e247
