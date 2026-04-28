import Swal from "sweetalert2";

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
        title,
        text,
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
        title,
        text,
        icon: "success",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}

/** 정보 팝업 */
export function showInfoAlert({ title, text } = {}) {
    return Swal.fire({
        title,
        text,
        icon: "info",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}

/** 경고 팝업 */
export function showWarningAlert({ title, text } = {}) {
    return Swal.fire({
        title,
        text,
        icon: "warning",
        iconColor: "#E89B9B",
        confirmButtonColor: "#A8C8D8",
        customClass: sharedCustomClass,
    });
}
