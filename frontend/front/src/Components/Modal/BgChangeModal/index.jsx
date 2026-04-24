import React, { useState } from "react";
import ModalLayout from "../ModalLayout";

/**
 * BgChangeModal
 * - Home 화면에서 "배경 이미지 변경" 버튼 클릭 시 열리는 모달.
 * - 프리셋 썸네일을 고르는 간단한 그리드.
 *
 * props:
 *   - isOpen     : boolean
 *   - onClose    : ()=>void
 *   - currentBg  : string  현재 배경 key
 *   - onApply    : (key)=>void
 *
 * ※ 실제 이미지 파일 연결은 나중에. 지금은 색상 placeholder.
 */
const BACKGROUNDS = [
  { key: "forest", label: "비 내리는 숲", color: "#7FA7A1" },
  { key: "ocean", label: "파도 소리", color: "#87B4C4" },
  { key: "fire", label: "모닥불", color: "#E89B9B" },
  { key: "cafe", label: "카페 소음", color: "#C2B280" },
  { key: "rain", label: "빗소리", color: "#8796A5" },
  { key: "night", label: "고요한 밤", color: "#4A5C6E" },
];

const BgChangeModal = ({ isOpen, onClose, currentBg = "forest", onApply }) => {
  const [selected, setSelected] = useState(currentBg);

  const handleApply = () => {
    onApply?.(selected);
    onClose?.();
  };

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="배경 이미지 변경">
      <div className="grid grid-cols-3 gap-3">
        {BACKGROUNDS.map((bg) => {
          const active = selected === bg.key;
          return (
            <button
              key={bg.key}
              type="button"
              onClick={() => setSelected(bg.key)}
              className={`flex flex-col items-center gap-2 p-2 rounded-xl transition ${
                active ? "ring-2 ring-[#A8C8D8]" : ""
              }`}
            >
              <div
                className="w-full aspect-square rounded-xl shadow-inner"
                style={{ backgroundColor: bg.color }}
              />
              <span className="text-[11px] text-[#3D4D5C] font-medium">
                {bg.label}
              </span>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        onClick={handleApply}
        className="mt-5 w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9]"
      >
        적용하기
      </button>
    </ModalLayout>
  );
};

export default BgChangeModal;
