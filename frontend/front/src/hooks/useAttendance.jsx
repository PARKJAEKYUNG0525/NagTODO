import { useCallback } from "react";
import api from "@/utils/api";
import {showWarningAlert} from "@/utils/alertUtils.js";

export const useAttendance = () => {
    const createAttendance = useCallback(async () => {
        try {
            const res = await api.post("/attendance");
            return res.data;
        } catch (error) {
            showWarningAlert({title: "출석 확인이 되지 않았습니다.", text: error.message});
            return null;
        }
    }, []);

    return { createAttendance };
};

export default useAttendance;