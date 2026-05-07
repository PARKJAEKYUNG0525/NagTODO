import React, { useEffect } from "react";

const ModalLayout = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* 배경 오버레이 */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm cursor-pointer"
        onClick={onClose}
      />

      {/* 카드 */}
      <div className="relative bg-white rounded-[24px] shadow-2xl max-w-md w-full overflow-hidden "
      onClick={(e) => e.stopPropagation()}>
        {/* 헤더 */}
        <div className="flex justify-between items-center px-6 pt-6 pb-3">
          <h2 className="text-[20px] font-bold text-[#3D4D5C]">{title}</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#8B9BAA] hover:bg-[#EEF2F5] cursor-pointer"
            aria-label="닫기"
          >
            {/* 아이콘 위치: 닫기 (bi-x-lg) */}
            <span className="text-lg leading-none">×</span>
          </button>
        </div>

        {/* 본문 */}
        <div className="px-6 pb-8">{children}</div>
      </div>
    </div>
  );
};

export default ModalLayout;
