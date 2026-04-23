import React, { useState } from "react";
import NotificationModal from "../../Components/Modal/NotificationModal";
import BgChangeModal from "../../Components/Modal/BgChangeModal";

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
    const [isNotiOpen, setIsNotiOpen] = useState(false);
    const [isBgOpen, setIsBgOpen] = useState(false);
    const [currentBg, setCurrentBg] = useState("forest");

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

    const handlePlayToggle = () => alert("백색소음 재생/정지");

    return (
        <>
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
                <div className="flex-1 bg-white rounded-full px-4 py-3 flex items-center gap-3 shadow-sm">
                    <button
                        onClick={handlePlayToggle}
                        className="w-8 h-8 rounded-xl bg-[#A8C8D8] flex items-center justify-center shrink-0"
                        aria-label="재생/정지"
                    >
                        {/* 아이콘 위치: 정지/재생 (bi-stop-fill / bi-play-fill) */}
                        <span className="w-4 h-4 block" />
                    </button>
                    <span className="text-sm font-semibold text-[#3D4D5C]">
            비 내리는 숲
          </span>
                </div>
                <button
                    onClick={() => setIsBgOpen(true)}
                    className="w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
                    aria-label="배경 이미지 변경"
                >
                    {/* 아이콘 위치: 이미지 (bi-image) */}
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
                currentBg={currentBg}
                onApply={(key) => {
                    setCurrentBg(key);
                    alert(`배경 "${key}" 적용`);
                }}
            />
        </>
    );
}
