import React, { useState, useEffect } from "react";
import ModalLayout from "../ModalLayout";
import { showSuccessAlert, showWarningAlert } from "../../../utils/alertUtils";

const MAX_LENGTH = 30;

const AdminMessageModal = ({ isOpen, onClose, users = [], sendNotification, sendNotificationToAll }) => {
    const [activeTab, setActiveTab] = useState("all"); // "all" | "individual"
    const [title, setTitle] = useState("");
    const [selectedUserId, setSelectedUserId] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    // 모달 닫힐 때 초기화
    useEffect(() => {
        if (!isOpen) {
            setTitle("");
            setSelectedUserId("");
            setActiveTab("all");
        }
    }, [isOpen]);

    const handleTitleChange = (e) => {
        if (e.target.value.length <= MAX_LENGTH) {
            setTitle(e.target.value);
        }
    };

    const handleSend = async () => {
        if (!title.trim()) {
            showWarningAlert({ title: "메세지를 입력해주세요." });
            return;
        }

        if (activeTab === "individual" && !selectedUserId) {
            showWarningAlert({ title: "회원을 선택해주세요." });
            return;
        }

        setIsLoading(true);
        try {
            if (activeTab === "all") {
                const success = await sendNotificationToAll(users, title.trim(), title.trim());
                if (success) await showSuccessAlert({ title: "전체 회원에게 메세지를 보냈어요." });
                else showWarningAlert({ title: "메세지 전송에 실패했어요." });
            } else {
                const success = await sendNotification(Number(selectedUserId), title.trim(), title.trim());
                if (success) await showSuccessAlert({ title: "메세지를 보냈어요." });
                else showWarningAlert({ title: "메세지 전송에 실패했어요." });
            }
            onClose();
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <ModalLayout isOpen={isOpen} onClose={onClose} title="메세지 보내기">
            <div className="flex flex-col gap-4">

                {/* 탭 */}
                <div className="flex gap-2">
                    {[
                        { key: "all", label: "전체 공지" },
                        { key: "individual", label: "개별 발송" },
                    ].map((tab) => (
                        <button
                            key={tab.key}
                            onClick={() => setActiveTab(tab.key)}
                            className={`flex-1 py-2 rounded-xl text-sm font-bold transition-all cursor-pointer
                                ${activeTab === tab.key
                                    ? "bg-[#A8C8D8] text-white"
                                    : "bg-[#F5F8FA] text-[#8B9BAA]"
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* 개별 발송 - 회원 선택 */}
                {activeTab === "individual" && (
                    <select
                        value={selectedUserId}
                        onChange={(e) => setSelectedUserId(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8] cursor-pointer"
                    >
                        <option value="">회원 선택</option>
                        {users.map((user) => (
                            <option key={user.user_id} value={user.user_id}>
                                {user.username}
                            </option>
                        ))}
                    </select>
                )}

                {/* 메세지 입력 */}
                <div className="relative">
                    <input
                        type="text"
                        value={title}
                        onChange={handleTitleChange}
                        placeholder="메세지를 입력해주세요"
                        className="w-full px-4 py-3 rounded-xl bg-[#F5F8FA] text-sm text-[#3D4D5C] outline-none focus:ring-2 focus:ring-[#A8C8D8] cursor-text pr-16"
                    />
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-[#8B9BAA]">
                        {title.length}/{MAX_LENGTH}
                    </span>
                </div>

                {/* 전송 버튼 */}
                <button
                    onClick={handleSend}
                    disabled={isLoading}
                    className="w-full py-3 rounded-xl bg-[#A8C8D8] text-white text-sm font-bold hover:bg-[#8BB5C8] active:scale-95 transition-all cursor-pointer disabled:opacity-50"
                >
                    {isLoading ? "전송 중..." : "보내기"}
                </button>
            </div>
        </ModalLayout>
    );
};

export default AdminMessageModal;