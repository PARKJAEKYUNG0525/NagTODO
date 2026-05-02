import React, { useState, useEffect, useCallback } from "react";
import ModalLayout from "../ModalLayout";
import api from "@/utils/api.js";
import {useImg} from "@/hooks/useImg.jsx";
import {showWarningAlert} from "@/utils/alertUtils.js";

/**
 * BgChangeModal
 * - 배경 이미지 변경 모달
 * - 백엔드 /imgs에서 받아온 이미지 그리드
 *
 * props:
 *   - isOpen     : boolean
 *   - onClose    : ()=>void
 *   - currentBg  : string  현재 배경 img_id
 *   - onApply    : (img)=>void   선택한 img 객체 전체를 넘김
 */
const BgChangeModal = ({ isOpen, onClose }) => {
    const { getAllImgs, currentBg, setCurrentBg } = useImg();
    const [imgs, setImgs] = useState([]);
    const [selected, setSelected] = useState(currentBg?.img_id ?? null);

    // 모달이 열릴 때 이미지 목록 fetch
    const loadImgs = useCallback(async () => {
        const data = await getAllImgs();
        setImgs(Array.isArray(data) ? data : []);
    }, [getAllImgs]);

    useEffect(() => {
        if (isOpen) loadImgs();
    }, [isOpen, loadImgs]);

    // currentBg가 바뀔 때 선택 상태 동기화
    useEffect(() => {
        setSelected(currentBg ?? null);
    }, [currentBg]);
    
    const handleApply = () => {
        const selectedImg = imgs.find((i) => i.img_id === selected);
        if (selectedImg) {
            setCurrentBg(selectedImg);
            api.patch("/users/me", { img_id : selectedImg.img_id})
                .catch(error => showWarningAlert({"title": "배경 적용 실패", "text" : error.message}));
        }
        onClose?.();
    };

    const handleReset = () => {
        setCurrentBg(null);
        onClose?.();
    };

    return (
        <ModalLayout isOpen={isOpen} onClose={onClose} title="배경 이미지 변경">
            <div className="grid grid-cols-3 gap-3">
                {imgs.length === 0 ? (
                    <div className="col-span-3 py-10 text-center text-sm text-[#8B9BAA]">
                        이미지를 불러오는 중...
                    </div>
                ) : (
                    imgs.map((img) => {
                        const active = selected === img.img_id;
                        return (
                            <button
                                key={img.img_id}
                                type="button"
                                onClick={() => setSelected(img.img_id)}
                                className={`flex flex-col items-center gap-2 p-2 rounded-xl transition ${
                                    active ? "ring-2 ring-[#A8C8D8]" : ""
                                }`}
                            >
                                <div className="w-full aspect-square rounded-xl shadow-inner overflow-hidden bg-[#F5F8FA]">
                                    <img
                                        src={`${api.defaults.baseURL}${img.file_url}`}
                                        alt={img.title}
                                        className="w-full h-full object-cover"
                                        loading="lazy"
                                    />
                                </div>
                                <span className="text-[11px] text-[#3D4D5C] font-medium truncate w-full text-center">
                                    {img.title}
                                </span>
                            </button>
                        );
                    })
                )}
            </div>

            <button
                type="button"
                onClick={handleApply}
                disabled={!selected}
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

export default BgChangeModal;