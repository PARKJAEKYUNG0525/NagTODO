import React from "react";
import ModalLayout from "../ModalLayout";

/**
 * NotificationModal
 * - 헤더의 알림 벨 클릭 시 열리는 알림 목록 모달.
 * - ModalLayout 안에 간단한 알림 리스트를 렌더합니다.
 *
 * props:
 *   - isOpen        : boolean
 *   - onClose       : ()=>void
 *   - notifications : [{ id, title, body, time, read }]
 *   - onItemClick   : (notification)=>void
 *
 * ※ 지금은 간단한 카드 리스트만. 추후 필터/탭/알림 설정 버튼 분리 예정.
 */
const NotificationModal = ({
  isOpen,
  onClose,
  notifications = [],
  onItemClick,
}) => {
  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="알림">
      {notifications.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#8B9BAA]">
          새로운 알림이 없어요.
        </div>
      ) : (
        <ul className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto">
          {notifications.map((n) => (
            <li key={n.id}>
              <button
                type="button"
                onClick={() => onItemClick?.(n)}
                className={`w-full text-left p-3 rounded-xl ${
                  n.read ? "bg-[#F5F8FA]" : "bg-[#E4EEF3]"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-semibold text-[#3D4D5C]">
                    {n.title}
                  </p>
                  <span className="text-[11px] text-[#8B9BAA] shrink-0">
                    {n.time}
                  </span>
                </div>
                {n.body && (
                  <p className="text-xs text-[#8B9BAA] mt-1">{n.body}</p>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </ModalLayout>
  );
};

export default NotificationModal;
