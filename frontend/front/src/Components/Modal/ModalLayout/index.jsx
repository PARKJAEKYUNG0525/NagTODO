import React, { useEffect } from "react";

/**
 * ModalLayout
 * - 모든 모달의 공통 껍데기 (backdrop + 둥근 흰 카드 + 헤더 + children 슬롯)
 * - 열려 있는 동안 body 스크롤을 잠급니다.
 * - backdrop 클릭 / 우상단 X 버튼으로 닫을 수 있습니다.
 *
 * props:
 *   - isOpen    : boolean  모달 표시 여부
 *   - onClose   : ()=>void 닫기 콜백
 *   - title     : string   모달 상단 타이틀
 *   - children  : 본문 영역
 *
 * ※ 아직 React 스타일로 잘게 쪼개지 않고 "한 파일짜리 레이아웃" 으로만 둡니다.
 *   나중에 Header, Backdrop 등으로 분리 예정.
 */
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
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 카드 */}
      <div className="relative bg-white rounded-[24px] shadow-2xl max-w-md w-full overflow-hidden">
        {/* 헤더 */}
        <div className="flex justify-between items-center px-6 pt-6 pb-3">
          <h2 className="text-[20px] font-bold text-[#3D4D5C]">{title}</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#8B9BAA] hover:bg-[#EEF2F5]"
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
