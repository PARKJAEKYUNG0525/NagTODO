import React, { useState } from "react";
import ModalLayout from "../ModalLayout";

const TABS = [
  { key: "all", label: "전체" },
  { key: "friend", label: "친구" },
  { key: "system", label: "시스템" },
];

// 알림 타입 분류 함수
const getNotificationType = (notification) => {
  const content = notification.content || "";
  const title = notification.title || "";

  if (
    content.startsWith("friend_request") ||
    title === "새 친구 요청" ||
    title.includes("친구")
  ) {
    return "friend";
  }
  return "system";
};

const NotificationModal = ({
  isOpen,
  onClose,
  notifications = [],
  onItemClick,
  onAccept,
  onReject,
}) => {
  const [activeTab, setActiveTab] = useState("all");

  const filteredNotifications =
    activeTab === "all"
      ? notifications
      : notifications.filter((n) => getNotificationType(n) === activeTab);

  return (
    <ModalLayout isOpen={isOpen} onClose={onClose} title="알림">
      {/* 탭 필터 */}
      <div className="flex gap-2 mb-4">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer
              ${
                activeTab === tab.key
                  ? "bg-[#A8C8D8] text-white shadow-sm"
                  : "bg-[#EEF3F6] text-[#8B9BAA] hover:bg-[#DDE8EE]"
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 알림 목록 */}
      {filteredNotifications.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#8B9BAA]">
          새로운 알림이 없어요.
        </div>
      ) : (
        <ul className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto">
          {filteredNotifications.map((n) => {
            const parts = n.content?.split(":") || [];
            const username = parts[2] || "";
            const isFriendRequest = n.title === "새 친구 요청";

            return (
              <li key={n.notification_id}>
                <div
                  className={`w-full p-3 rounded-xl ${
                    n.is_read ? "bg-[#F5F8FA]" : "bg-[#E4EEF3]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    {/* 아바타 */}
                    <div className="w-9 h-9 rounded-full bg-[#A8C8D8] flex-shrink-0" />

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-[#3D4D5C]">
                        {username ? (
                          <>
                            <span className="font-bold">{username}</span> 님이
                            친구 요청을 보냈어요
                          </>
                        ) : (
                          n.title
                        )}
                      </p>
                      <p className="text-xs text-[#8B9BAA] mt-0.5">
                        {n.created_at
                          ? new Date(n.created_at).toLocaleDateString("ko-KR", {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "방금 전"}
                      </p>
                    </div>
                  </div>

                  {/* 친구 요청 수락/거절 버튼 */}
                  {isFriendRequest && !n.is_read && (
                    <div className="flex gap-2 mt-3 justify-end">
                      <button
                        onClick={() => onReject?.(n)}
                        className="px-5 py-1.5 rounded-xl bg-[#E89B9B] text-white text-xs font-bold cursor-pointer hover:bg-[#d98a8a] transition-colors"
                      >
                        거절
                      </button>
                      <button
                        onClick={() => onAccept?.(n)}
                        className="px-5 py-1.5 rounded-xl bg-[#A8C8D8] text-white text-xs font-bold cursor-pointer hover:bg-[#97b8c8] transition-colors"
                      >
                        수락
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