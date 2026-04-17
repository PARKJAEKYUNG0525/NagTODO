import Swal from "sweetalert2";

// 공통 버튼 스타일 (실무에서 자주 쓰이는 블랙 톤)
const PRIMARY_BUTTON_COLOR = "#0f172a";
const DANGER_BUTTON_COLOR = "#000000"; // 삭제 등 위험 작업도 블랙으로 처리하거나 짙은 회색 사용

export const handleAuthError = async (error) => {
    if (error.response?.status === 401) {
        await Swal.fire({
            title: "로그인이 필요합니다",
            text: "해당 기능을 이용하시려면 로그인이 필요합니다.",
            icon: "warning",
            confirmButtonText: "로그인하러 가기",
            confirmButtonColor: PRIMARY_BUTTON_COLOR,
            background: "#ffffff",
            customClass: {
                title: "text-lg font-bold text-slate-900",
                htmlContainer: "text-sm text-slate-500",
            },
        });
        return true;
    }
    return false;
};

export const showErrorAlert = (
    error,
    defaultMessage = "오류가 발생했습니다.",
) => {
    Swal.fire({
        icon: "error",
        title: "알림",
        text:
            error.response?.data?.error ||
            error.response?.data?.detail ||
            defaultMessage,
        confirmButtonColor: PRIMARY_BUTTON_COLOR,
    });
};

export const showSuccessAlert = (message) => {
    Swal.fire({
        icon: "success",
        title: "완료",
        text: message,
        confirmButtonColor: PRIMARY_BUTTON_COLOR,
    });
};

export const showConfirmDialog = async (
    title,
    text,
    confirmButtonText = "확인",
    cancelButtonText = "취소",
) => {
    return await Swal.fire({
        title,
        text,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: DANGER_BUTTON_COLOR,
        cancelButtonColor: "#94a3b8", // 취소 버튼은 연한 회색(slate-400)으로 힘을 뺍니다.
        confirmButtonText,
        cancelButtonText,
        reverseButtons: true, // 실무에서는 보통 '취소'가 왼쪽, '확인'이 오른쪽에 옵니다.
    });
};