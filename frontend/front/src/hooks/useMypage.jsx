import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { showSuccessAlert } from "../utils/alertUtils.js";
import { useAuth } from "./useAuth";

const useMypage = () => {
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const { setUser, logout } = useAuth();
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
                return true; // 사용 가능
            }
        } catch (error) {
            console.log(error);
            if (error.response?.status === 409) {
                setError("이미 사용 중인 닉네임입니다.");
            } else {
                setError(error.response?.data.detail || "닉네임 확인에 실패했습니다.");
            }
            return false; // 사용 불가
        }
    };

    // 프로필 수정
    const updateProfile = async ({ username }) => {
        try {
            const response = await api.patch("/users/me", { username } );
            if (response.status === 200) {
                setUser(response.data);
                // showSuccessAlert("프로필이 수정되었습니다");
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
                showSuccessAlert("비밀번호가 변경되었습니다");
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "비밀번호 변경에 실패했습니다.");
            return false;
        }
    };

    // 회원 탈퇴
    const deleteAccount = async () => {
        try {
            const response = await api.delete("/users/me");
            if (response.status === 200) {
                showSuccessAlert("회원 탈퇴가 완료되었습니다");
                await logout();
                navigate("/");
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "회원 탈퇴에 실패했습니다.");
            return false;
        }
    };

    return {
        error,
        setError,
        isLoading,
        getProfile,
        updateProfile,
        updatePassword,
        deleteAccount,
        checkUsername,
    };
};

export default useMypage;