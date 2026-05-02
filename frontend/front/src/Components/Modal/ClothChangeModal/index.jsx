import React, { useState, useEffect, useCallback } from "react";
import ModalLayout from "../ModalLayout";
import api from "@/utils/api.js";
import { useAuth } from "@/hooks/useAuth";
import useCloth from "@/hooks/useCloth.jsx";

const TABS = [
    { key: "default",   label: "기본",   prefix: "default_" },
    { key: "croissant", label: "크루와상", prefix: "croissant_" },
];

const ClothChangeModal = ({ isOpen, onClose, currentClothId, onApply }) => {
    const { getAllCloths } = useCloth();
    const { user } = useAuth();
    const [cloths, setCloths] = useState([]);
    const [selected, setSelected] = useState(currentClothId ?? null);
    const [activeTab, setActiveTab] = useState("default");
    const rewardSet = new Set(user?.reward_cloth_ids ?? []);

    const loadCloths = useCallback(async () => {
        const data = await getAllCloths();
        setCloths(Array.isArray(data) ? data : []);
    }, [getAllCloths]);

    useEffect(() => {
        if (isOpen) loadCloths();
    }, [isOpen, loadCloths]);

    useEffect(() => {
        setSelected(currentClothId ?? null);
        // 모달 열릴 때 현재 cloth가 속한 탭으로 자동 이동
        if (currentClothId) {
            const tab = TABS.find((t) => currentClothId.startsWith(t.prefix));
            if (tab) setActiveTab(tab.key);
        }
    }, [currentClothId, isOpen]);

    // 현재 탭에 해당하는 cloth만 필터링
    const activePrefix = TABS.find((t) => t.key === activeTab)?.prefix ?? "";
    const filteredCloths = cloths.filter((c) =>
        c.cloth_id?.startsWith(activePrefix)
    );

    // TODO: 출석 보상 도입 시 백엔드의 owned_cloths로 대체
    const isUnlocked = (cloth_id) => {
        if (!cloth_id) return false;
        if (cloth_id.startsWith("default_")) return true;     // 기본 제공 (DB 안 봄)
        return rewardSet.has(cloth_id);                        // 보상으로 받은 것
    };

    const handleApply = () => {
        const selectedCloth = cloths.find((c) => c.cloth_id === selected);
        if (selectedCloth && isUnlocked(selectedCloth.cloth_id)) {
            onApply?.(selectedCloth);
        }
        onClose?.();
    };

    const handleReset = () => {
        setSelected(null);
        onApply?.(null);
        onClose?.();
    };

    return (
        <ModalLayout isOpen={isOpen} onClose={onClose} title="프로필 변경">
            {/* 탭 헤더 */}
            <div className="flex gap-1 mb-4 border-b border-[#E4E9EE]">
                {TABS.map((tab) => {
                    const active = activeTab === tab.key;
                    return (
                        <button
                            key={tab.key}
                            type="button"
                            onClick={() => setActiveTab(tab.key)}
                            className={`pb-2 px-4 text-sm font-semibold transition ${
                                active
                                    ? "text-[#3D4D5C] border-b-2 border-[#A8C8D8]"
                                    : "text-[#8B9BAA] border-b-2 border-transparent hover:text-[#3D4D5C]"
                            }`}
                        >
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* 그리드 — 활성 탭의 cloth만 렌더 */}
            <div className="grid grid-cols-3 gap-3 max-h-[60vh] overflow-y-auto">
                {cloths.length === 0 ? (
                    <div className="col-span-3 py-10 text-center text-sm text-[#8B9BAA]">
                        프로필을 불러오는 중...
                    </div>
                ) : filteredCloths.length === 0 ? (
                    <div className="col-span-3 py-10 text-center text-sm text-[#8B9BAA]">
                        이 카테고리에는 아직 프로필이 없어요
                    </div>
                ) : (
                    filteredCloths.map((cloth) => {
                        const unlocked = isUnlocked(cloth.cloth_id);
                        const active = unlocked && selected === cloth.cloth_id;

                        return (
                            <button
                                key={cloth.cloth_id}
                                type="button"
                                onClick={() => unlocked && setSelected(cloth.cloth_id)}
                                disabled={!unlocked}
                                aria-disabled={!unlocked}
                                title={unlocked ? cloth.title : "출석 보상으로 해금 예정"}
                                className={`relative flex flex-col items-center gap-2 p-2 rounded-xl transition ${
                                    active ? "ring-2 ring-[#A8C8D8]" : ""
                                } ${
                                    !unlocked ? "cursor-not-allowed" : "hover:bg-[#F5F8FA]"
                                }`}
                            >
                                <div className="w-full aspect-square rounded-xl shadow-inner overflow-hidden bg-[#F5F8FA] relative">
                                    <img
                                        src={`${api.defaults.baseURL}${cloth.file_url}`}
                                        alt={cloth.title}
                                        className={`w-full h-full object-cover transition ${
                                            unlocked ? "" : "grayscale opacity-40"
                                        }`}
                                        loading="lazy"
                                    />
                                    {!unlocked && (
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <span className="px-2 py-0.5 rounded-md bg-black/55 text-white text-[10px] font-semibold tracking-wide">
                                                잠김
                                            </span>
                                        </div>
                                    )}
                                </div>
                                <span
                                    className={`text-[11px] font-medium truncate w-full text-center ${
                                        unlocked ? "text-[#3D4D5C]" : "text-[#B8C2CC]"
                                    }`}
                                >
                                    {cloth.title}
                                </span>
                            </button>
                        );
                    })
                )}
            </div>

            <button
                type="button"
                onClick={handleApply}
                disabled={!selected || !isUnlocked(selected)}
                className="mt-5 w-full py-3 rounded-xl bg-[#A8C8D8] text-white font-semibold text-sm hover:bg-[#97BAC9] disabled:opacity-50 disabled:cursor-not-allowed"
            >
                적용하기
            </button>
            <div className="flex flex-col items-center">
                <button
                    onClick={handleReset}
                    className="mt-3 px-4 py-1.5 text-xs text-[#F4A6A6]"
                >
                    초기화
                </button>
            </div>
        </ModalLayout>
    );
};

export default ClothChangeModal;