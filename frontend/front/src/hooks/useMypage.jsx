import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { showSuccessAlert, showWarningDialog } from "../utils/alertUtils.js";
import { useAuth } from "./useAuth";

const useMypage = () => {
    const { setUser, logout, isDeleting, setIsDeleting} = useAuth();
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();


    // 프로필 조회
    const getProfile = async () => {
        try {
            const response = await api.get("/users/me");
            if (response.status === 200) {
                return response.data;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "프로필 조회에 실패했습니다.");
        }
    };

    const checkUsername = async (username) => {
        try {
            const response = await api.get(`/users/check-username?username=${username}`);
            if (response.status === 200) {
                return true; 
            }
        } catch (error) {
            console.log(error);
            if (error.response?.status === 409) {
                setError("이미 사용 중인 닉네임입니다.");
            } else {
                setError(error.response?.data.detail || "닉네임 확인에 실패했습니다.");
            }
            return false;
        }
    };

    // 프로필 수정
    const updateProfile = async ({ username }) => {
        try {
            const response = await api.patch("/users/me", { username } );
            if (response.status === 200) {
                setUser(response.data);
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "프로필 수정에 실패했습니다.");
            return false;
        }
    };

    // 비밀번호 변경
    const updatePassword = async ({ currentPassword, newPassword, confirmPassword }) => {
        try {
            const response = await api.patch("/users/me/password", {
                current_pw: currentPassword,
                new_pw: newPassword,
                confirm_pw: confirmPassword,
            });
            if (response.status === 200) {
                showSuccessAlert({title:"비밀번호가 변경되었습니다"});
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "비밀번호 변경에 실패했습니다.");
            return false;
        }
    };

    // 상태메세지
    const updateStatusMessage = async (status_message) => {
        try {
            const response = await api.patch("/users/me", { status_message });
            if (response.status === 200) {
                setUser(response.data); 
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "상태 메시지 수정에 실패했습니다.");
            return false;
        }
    };

    //회원탈퇴
    const deleteUser = async () => {
        const confirmed = await showWarningDialog({
        title: "정말 탈퇴하시겠습니까?",
        text: "탈퇴 시 모든 데이터가 삭제됩니다",
        confirmText: "탈퇴",
        });
        if (!confirmed) return;

        try {
            const response = await api.delete("/users/me");
            if (response.status === 200) {
                setIsDeleting(true);
                setIsAuthenticated(false);
                setUser(null);
                await showSuccessAlert({ title: "탈퇴가 완료되었습니다" });
                navigate("/");
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "회원탈퇴에 실패했습니다");
        } finally {
        setIsDeleting(false);
        }
    };

    // 모드 변경
    const updateMode = async (mode) => {
        try {
            const response = await api.patch("/users/me", { mode });
            if (response.status === 200) {
                setUser(response.data);
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "모드 변경에 실패했습니다.");
            return false;
        }
    };


    return {
        error,
        setError,
        getProfile,
        updateProfile,
        updatePassword,
        checkUsername,
        updateStatusMessage,
        deleteUser,
        updateMode
    };
};

export default useMypage;