import api from "../utils/api.js";
import {showWarningAlert, showSuccessAlert} from "../utils/alertUtils.js";

import React, { useCallback, useState } from 'react';

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
            showWarningAlert({ title: "카테고리를 불러올 수 없습니다.", text: error.message });
            return null;
        }
        finally {
            setCtLoading(false);
        }
    }, [])

    return { ctLoading, getCategory };
};

export default useCategory;