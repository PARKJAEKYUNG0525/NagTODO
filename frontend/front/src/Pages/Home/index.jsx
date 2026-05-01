import React, {useEffect, useRef, useState} from "react";
import BgChangeModal from "../../Components/Modal/BgChangeModal";
import NotificationBell from "../../Components/Notification";

import { useImg } from "@/hooks/useImg";
import { useMusic } from "@/hooks/useMusic";
import api from "@/utils/api.js";

import {
  BsFillImageFill,
  BsFillSquareFill,
  BsChevronDown,
  BsPlayFill,
  BsPauseFill
} from "react-icons/bs";

export default function Home() {
    const { getUserBg, currentBg } = useImg();
    const { musics, getAllMusics, play, currentMusic, toggle, isPlaying } = useMusic();

    const [isMusicListOpen, setIsMusicListOpen] = useState(false);
    const playerRef = useRef(null);
    const [isBgOpen, setIsBgOpen] = useState(false);

    // 사진 목록 받아오기
    useEffect(() => { getUserBg(); }, []);

    // 음악 목록 받아오기
    useEffect(() => { getAllMusics(); }, []);

    // 바깥 클릭 시 드롭다운 닫기
    useEffect(() => {
        if (!isMusicListOpen) return;
        const handleClickOutside = (e) => {
            if (playerRef.current && !playerRef.current.contains(e.target)) {
                setIsMusicListOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [isMusicListOpen]);

    // 음악 재생/중지
    const handlePlayToggle = () => toggle();

    return (
        <div className="flex-1 flex flex-col bg-[#F4F7FA] bg-cover bg-center"
             style={
                 currentBg
                     ? {
                         backgroundImage: `linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url(${currentBg.file_url})`,
                     }
                     : undefined
             }>
            {/* 상단 헤더 (알림 벨) */}
            <header className="px-6 pt-6 flex justify-end">
                <NotificationBell />
            </header>

            {/* 메인 콘텐츠 (Welcome 타이포) */}
            <main className="flex-1 flex flex-col items-center justify-center px-6">
                <h1 className="text-6xl font-bold text-[#3D4D5C] tracking-tight">
                    Welcome
                </h1>
                <p className="mt-4 text-sm text-[#8B9BAA]">
                    오늘도 좋은 하루 보내세요 ✨
                </p>
            </main>

            {/* 미니 뮤직 플레이어 + 배경 이미지 변경 */}
            <section className="px-6 pb-4 flex items-center gap-3">
                <div
                    ref={playerRef}
                    className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-3 shadow-sm relative"
                >
                    {/* 재생/정지 버튼 — 자기만의 onClick */}
                    <button
                        onClick={handlePlayToggle}
                        className="w-8 h-8 rounded-full bg-[#A8C8D8] flex items-center justify-center shrink-0 mr-3 transition-colors duration-200 hover:bg-[#97b7c7] cursor-pointer"
                        aria-label={isPlaying ? "정지" : "재생"}
                    >
                        {/* play가 true면 네모(정지), false면 세모(재생) */}
                        {isPlaying ? (
                            <BsFillSquareFill className="text-white" size={10} />
                        ) : (
                            <BsPlayFill className="text-white ml-0.5" size={20} />
                        )}
                    </button>

                    {/* 재생 버튼을 제외한 나머지 영역 — 클릭 시 드롭다운 토글 */}
                    <button
                        type="button"
                        onClick={() => setIsMusicListOpen((v) => !v)}
                        className="flex-1 flex items-center justify-between overflow-hidden cursor-pointer"
                        aria-haspopup="listbox"
                        aria-expanded={isMusicListOpen}
                    >
                        <span className="text-sm font-semibold text-[#3D4D5C] truncate pr-2">
                            {currentMusic?.title ?? "음악 선택"}
                        </span>

                        <BsChevronDown
                            size={18}
                            className={`shrink-0 transition-transform duration-300 ${
                                isMusicListOpen ? "rotate-180" : "rotate-0"
                            } text-[#3D4D5C]`} 
                            strokeWidth={1} 
                        />
                    </button>

                    {/* 드롭다운 리스트 — absolute로 컨테이너 아래에 띄움 */}
                    {isMusicListOpen && (
                        <ul
                            role="listbox"
                            className="absolute left-0 right-0 bottom-full mt-2 bg-white rounded-2xl shadow-lg z-10 max-h-60 overflow-y-auto py-2"
                        >
                            {musics.length === 0 ? (
                                <li className="px-4 py-2 text-sm text-[#8B9BAA]">
                                    등록된 음악이 없어요
                                </li>
                            ) : (
                                musics.map((m) => {
                                    const isActive = currentMusic?.music_id === m.music_id;
                                    return (
                                        <li key={m.music_id}>
                                            <button
                                                type="button"
                                                role="option"
                                                aria-selected={isActive}
                                                onClick={() => {
                                                    play(m);
                                                    setIsMusicListOpen(false);
                                                }}
                                                className={`w-full text-left px-4 py-2 text-sm transition cursor-pointer ${
                                                    isActive
                                                        ? "bg-[#F5F8FA] text-[#3D4D5C] font-bold"
                                                        : "text-[#3D4D5C] hover:bg-[#F5F8FA]"
                                                }`}
                                            >
                                                {m.title}
                                            </button>
                                        </li>
                                    );
                                })
                            )}
                        </ul>
                    )}
                </div>

                <button
                    onClick={() => setIsBgOpen(true)}
                    className="w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0 cursor-pointer"
                    aria-label="배경 이미지 변경"
                >
                    <BsFillImageFill className="text-white" size={20} />
                </button>
            </section>
            <BgChangeModal
                isOpen={isBgOpen}
                onClose={() => setIsBgOpen(false)}
            />
        </div>
    );
}
