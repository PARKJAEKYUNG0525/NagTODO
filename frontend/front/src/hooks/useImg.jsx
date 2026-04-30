import api from "../utils/api.js";
import { createContext, useCallback, useContext, useState } from "react";

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
            await showWarningAlert({title : "이미지를 불러오는 데 실패했습니다.", text : error.message});
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
        } catch {
            // 인증 실패 등의 경우 조용히 무시
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