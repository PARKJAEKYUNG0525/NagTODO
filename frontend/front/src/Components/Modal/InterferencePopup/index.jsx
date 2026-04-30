import ModalLayout from "../ModalLayout";
import { useInterference } from "../../../hooks/useInterference";

const InterferencePopup = () => {
    const { popup, dismiss } = useInterference();
    const { todoTitle, feedback, globalRate, personalRate, similarCount, topFailures } = popup;

    return (
        <ModalLayout isOpen={popup.open} onClose={dismiss} title="잔소리꾼의 한 마디">
            {/* 어떤 todo인지 */}
            {todoTitle && (
                <p className="text-base font-bold text-[#3D4D5C] mb-4">
                    "{todoTitle}"
                </p>
            )}

            {/* 성공률 통계 */}
            <div className="bg-[#F5F8FA] rounded-xl px-4 py-3 mb-4">
                {similarCount != null && (
                    <p className="text-xs text-[#8B9BAA] mb-2">유사 todo {similarCount}개 기준</p>
                )}
                <div className="flex justify-around">
                    <div className="flex flex-col items-center gap-0.5">
                        <span className="text-xs text-[#8B9BAA]">내 성공률</span>
                        <span className="text-lg font-bold text-[#3D4D5C]">
                            {personalRate != null ? `${personalRate.toFixed(1)}%` : "-"}
                        </span>
                    </div>
                    <div className="w-px bg-[#D9DFE4]" />
                    <div className="flex flex-col items-center gap-0.5">
                        <span className="text-xs text-[#8B9BAA]">전체 성공률</span>
                        <span className="text-lg font-bold text-[#3D4D5C]">
                            {globalRate != null ? `${globalRate.toFixed(1)}%` : "-"}
                        </span>
                    </div>
                </div>
            </div>

            {/* 실패 사례 top 3 */}
            {topFailures.length > 0 && (
                <div className="mb-4">
                    <p className="text-xs text-[#8B9BAA] mb-1">비슷한 실패 사례</p>
                    <ul className="flex flex-col gap-1">
                        {topFailures.map((f, i) => (
                            <li key={i} className="text-xs text-[#3D4D5C] bg-[#F5F8FA] rounded-lg px-3 py-2">
                                {f}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* LLM 피드백 */}
            <p className="text-sm leading-relaxed text-[#3D4D5C] font-medium min-h-[60px]">
                {feedback}
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
