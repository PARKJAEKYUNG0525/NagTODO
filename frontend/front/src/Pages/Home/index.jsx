import React, {useEffect, useRef, useState} from "react";
import NotificationModal from "../../Components/Modal/NotificationModal";
import BgChangeModal from "../../Components/Modal/BgChangeModal";
import {useMusic} from "@/hooks/useMusic.jsx";
import api from "@/utils/api.js";
import useImg from "@/hooks/useImg.jsx";

/**
 * Home 화면
 * - 상단 우측 알림 벨 → NotificationModal
 * - 중앙 "Welcome" + 서브 카피
 * - 하단: 백색소음 미니 플레이어 + 배경 이미지 변경 → BgChangeModal
 *
 * ※ 9:16 프레임과 하단 Navbar 는 App.jsx 에서 처리합니다.
 *   이 컴포넌트는 프레임 내부에 들어갈 콘텐츠만 Fragment 로 반환합니다.
 */
export default function Home() {
    const { getUserBg, currentBg } = useImg();
    const { musics, getAllMusics, play, currentMusic, toggle } = useMusic();
    const [isMusicListOpen, setIsMusicListOpen] = useState(false);
    const playerRef = useRef(null);

    const [isNotiOpen, setIsNotiOpen] = useState(false);
    const [isBgOpen, setIsBgOpen] = useState(false);

    const notifications = [
        {
            id: 1,
            title: "React 복습 알림",
            body: "오늘 계획한 할 일을 아직 완료하지 않았어요.",
            time: "10분 전",
            read: false,
        },
        {
            id: 2,
            title: "친구 요청",
            body: "'codehaeun' 님이 친구 요청을 보냈어요.",
            time: "1시간 전",
            read: false,
        },
        {
            id: 3,
            title: "4월 리포트 준비 완료",
            body: "이번 달 리포트를 확인해 보세요.",
            time: "어제",
            read: true,
        },
    ];

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
                         backgroundImage: `linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url(${api.defaults.baseURL}${currentBg.file_url})`,
                     }
                     : undefined
             }>
            {/* 상단 헤더 (알림 벨) */}
            <header className="px-6 pt-6 flex justify-end">
                <button
                    onClick={() => setIsNotiOpen(true)}
                    className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm"
                >
                    {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
                    <span className="w-5 h-5 block" />
                    {/* 알림 도트 */}
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
                </button>
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
                        className="w-8 h-8 rounded-xl bg-[#A8C8D8] flex items-center justify-center shrink-0"
                        aria-label="재생/정지"
                    >
                        <span className="w-4 h-4 block" />
                    </button>

                    {/* 재생 버튼을 제외한 나머지 영역 — 클릭 시 드롭다운 토글 */}
                    <button
                        type="button"
                        onClick={() => setIsMusicListOpen((v) => !v)}
                        className="flex-1 text-left text-sm font-semibold text-[#3D4D5C] truncate"
                        aria-haspopup="listbox"
                        aria-expanded={isMusicListOpen}
                    >
                        {currentMusic?.title ?? "음악 선택"}
                    </button>

                    {/* 드롭다운 리스트 — absolute로 컨테이너 아래에 띄움 */}
                    {isMusicListOpen && (
                        <ul
                            role="listbox"
                            className="absolute left-0 right-0 bottom-full mb-2 bg-white rounded-2xl shadow-lg z-10 max-h-60 overflow-y-auto py-2"
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
                                                className={`w-full text-left px-4 py-2 text-sm transition ${
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
                    className="w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
                    aria-label="배경 이미지 변경"
                >
                    <span className="w-5 h-5 block" />
                </button>
            </section>

            {/* ─── 모달들 ─── */}
            <NotificationModal
                isOpen={isNotiOpen}
                onClose={() => setIsNotiOpen(false)}
                notifications={notifications}
                onItemClick={(n) => alert(`"${n.title}" 상세 보기`)}
            />
            <BgChangeModal
                isOpen={isBgOpen}
                onClose={() => setIsBgOpen(false)}
            />
        </div>
    );
}
