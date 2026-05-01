// hooks/useImg.jsx
import api from "../utils/api.js";
import { useCallback, useState } from "react";
import {showWarningAlert} from "@/utils/alertUtils.js";

export const useImg = () => {
    const [imgLoading, setImgLoading] = useState(false);

    const getAllImgs = useCallback(async () => {
        setImgLoading(true);
        try {
            const response = await api.get("/imgs");
            if (response.status === 200 || response.status === 201) {
                return response.data;
            }
            return [];
        } catch (error) {
            await showWarningAlert({title : "이미지를 불러오는 데 실패했습니다.", message : error.message});
            // console.error("이미지 목록 불러오기 실패:", error);
            return [];
        } finally {
            setImgLoading(false);
        }
    }, []);

    return { imgLoading, getAllImgs };
};

export default useImg;