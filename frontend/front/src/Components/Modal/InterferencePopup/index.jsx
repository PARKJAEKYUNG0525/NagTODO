import ModalLayout from "../ModalLayout";
import { useInterference } from "../../../hooks/useInterference";

/**
 * InterferencePopup
 * - 어느 화면에서든 todo 생성 직후 나타나는 AI 잔소리 팝업
 * - 로딩 중: 스피너 표시
 * - 완료: LLM 피드백 문장 표시
 */
const InterferencePopup = () => {
    const { popup, dismiss } = useInterference();

    return (
        <ModalLayout isOpen={popup.open} onClose={dismiss} title="잔소리꾼의 한 마디">
            <p className="text-sm leading-relaxed text-[#3D4D5C] font-medium min-h-[60px]">
                {popup.feedback}
            </p>
            <button
                onClick={dismiss}
                className="mt-5 w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9]"
            >
                알겠다고
            </button>
        </ModalLayout>
    );
};

export default InterferencePopup;
