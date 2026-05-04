import { useCallback } from "react";
import api from "@/utils/api";
import {showWarningAlert} from "@/utils/alertUtils.js";

export const useAttendance = () => {
    const createAttendance = useCallback(async () => {
        try {
            const res = await api.post("/attendance");
            return res.data;
            // 응답: {
            //   is_first_today: bool,
            //   total_days: number,
            //   reward_cloth_id: string | null,
            //   reward_cloth_title: string | null,
            //   reward_cloth_file_url: string | null,
            // }
        } catch (error) {
            showWarningAlert({title: "출석 확인이 되지 않았습니다.", text: error.message});
            return null;
        }
    }, []);

    return { createAttendance };
};

export default useAttendance;