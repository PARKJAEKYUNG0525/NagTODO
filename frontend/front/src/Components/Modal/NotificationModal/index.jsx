import React from "react";
import ModalLayout from "../ModalLayout";

// const [notifications, setNotifications] = useState([]);

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
  onAccept,
  onReject, 
}) => {
  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="알림">
      {notifications.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#8B9BAA]">
          새로운 알림이 없어요.
        </div>
      ) : (
        <ul className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto">
          {notifications.map((n) => {
            // content에서 닉네임 파싱: "friend_request:3:닉네임"
            const parts = n.content?.split(":") || [];
            const username = parts[2] || "";

            return (
              <li key={n.notification_id}> {/* ← notification_id로 수정 */}
                <div className={`w-full p-3 rounded-xl ${n.is_read ? "bg-[#F5F8FA]" : "bg-[#E4EEF3]"}`}>
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-semibold text-[#3D4D5C]">
                      {n.title}
                    </p>
                  </div>
                  {/* 닉네임 표시 */}
                  {username && (
                    <p className="text-xs text-[#8B9BAA] mt-1">
                      '{username}' 님이 친구 요청을 보냈어요.
                    </p>
                  )}
                  {/* 친구 요청 알림에만 수락/거절 버튼 */}
                  {n.title === "새 친구 요청" && !n.is_read && (
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => onAccept?.(n)}
                        className="flex-1 py-1.5 rounded-xl bg-[#A8C8D8] text-white text-xs font-bold"
                      >
                        수락
                      </button>
                      <button
                        onClick={() => onReject?.(n)}
                        className="flex-1 py-1.5 rounded-xl bg-[#E89B9B] text-white text-xs font-bold"
                      >
                        거절
                      </button>
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </ModalLayout>
  );
};

export default NotificationModal;
