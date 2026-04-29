import api from "../utils/api.js";
import {createContext, useCallback, useContext, useState} from "react";
import {showWarningAlert} from "@/utils/alertUtils.js";

const ImgContext = createContext(null);

export const ImgProvider = ({children}) => {
    const [imgLoading, setImgLoading] = useState(false);
    const [currentBg, setCurrentBg] = useState(null);

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

    const getUserBg = useCallback(async () => {
        try {
            const response = await api.get("/users/me");
            if (response.data.img_id) {
                const imgs = await getAllImgs();
                const userImg = imgs.find(i => i.img_id === response.data.img_id);
                if (userImg) setCurrentBg(userImg);
            }
        } catch (error) {
            await showWarningAlert({title: "배경 불러오기 실패", message: error.message});
        }
    }, [getAllImgs]);

    return (
        <ImgContext.Provider value={{ imgLoading, getAllImgs, currentBg, setCurrentBg, getUserBg }}>
            {children}
        </ImgContext.Provider>
    )
};

export const useImg = () => {
    const context = useContext(ImgContext);
    if (!context) throw new Error("useImg를 사용하려면 ImgProvider로 감싸야 합니다");
    return context;
};

export default useImg;