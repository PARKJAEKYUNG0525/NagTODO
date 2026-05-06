import Swal from "sweetalert2";
import api from "./api";

/**
 * sweetalert2 공통 래퍼 모음
 *
 * 프로젝트 디자인 시스템 색에 맞춘 기본값을 주입합니다.
 *   - 경고/삭제 계열: #E89B9B (coral)
 *   - 성공/정보 계열: #A8C8D8 (blue)
 *
 * 사용 예)
 *   const ok = await confirmDelete({ title: "정말 삭제할까요?" });
 *   if (ok) { await alertSuccess({ title: "삭제 완료" }); }
 */

const sharedCustomClass = {
    title: "!text-lg font-bold pt-6",
    popup: "rounded-3xl",
    confirmButton: "px-6 py-3 rounded-2xl",
    cancelButton: "px-6 py-3 rounded-2xl text-[#3D4D5C]",
};

/** 삭제 확인 다이얼로그 (isConfirmed 를 boolean 으로 반환) */
export async function showWarningDialog({
                                        title,
                                        text,
                                        confirmText = "삭제",
                                        cancelText = "취소",
                                    } = {}) {
    const result = await Swal.fire({
        title: title,
        text: text,
        width: '330px',
        icon: "warning",
        iconColor: "#E89B9B",
        showCancelButton: true,
        confirmButtonText: confirmText,
        cancelButtonText: cancelText,
        confirmButtonColor: "#E89B9B",
        cancelButtonColor: "#EEF2F5",
        reverseButtons: true,
        customClass: sharedCustomClass,
    });
    return result.isConfirmed;
}

/** 성공 토스트/팝업 */
export function showSuccessAlert({ title, text } = {}) {
    return Swal.fire({
        title : title,
        text : text,
        width: '330px',
        icon: "success",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}

/** 정보 팝업 */
export function showInfoAlert({ title, text } = {}) {
    return Swal.fire({
        title: title,
        text: text,
        width: '330px',
        icon: "info",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}

/** 경고 팝업 */
export function showWarningAlert({ title, text } = {}) {
    return Swal.fire({
        title: title,
        text: text,
        width: '300px',
        icon: "warning",
        iconColor: "#E89B9B",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}
/** 보상 팝업 */
export const showAttendanceReward = (totalDays, clothTitle, clothFileUrl) => {
    return Swal.fire({
        title: `누적 ${totalDays}일 출석 달성!`,
        html: `
            <div style="text-align:center;">
                <img src="${api.defaults.baseURL}${clothFileUrl}"
                     alt="${clothTitle}"
                     style="width:120px;height:120px;object-fit:cover;border-radius:50%;margin:16px auto;display:block;background:#F5F8FA;" />
                <p style="font-weight:bold;color:#3D4D5C;margin-top:8px;font-size:15px;">${clothTitle}</p>
                <p style="color:#8B9BAA;font-size:13px;margin-top:6px;">새로운 프로필이 해금되었어요</p>
            </div>
        `,
        width: '330px',
        confirmButtonColor: "#A8C8D8",
        confirmButtonText: "확인",
    });
};
