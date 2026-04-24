import React from "react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * 하단 탭 네비게이션 바 (5 탭)
 *
 * 순서:
 *   1) 메인 화면 → Home
 *   2) 친구      → Friend
 *   3) 투두리스트 → TodoMain
 *   4) 월간리포트 → MonthlyReport
 *   5) 마이페이지 → Mypage
 *
 * Props
 *  - activeTab     (string) 현재 활성 탭 key. 부모가 state/router 로 제어 (옵션)
 *  - onTabClick    (fn)     탭 클릭 시 호출. 시그니처: (key, path) => void
 *
 * activeTab / onTabClick 이 없으면 내부 state 로 동작 (프리뷰 용도)
 */

const TABS = [
    { key: "main",   label: "홈",      path: "/main" },
    { key: "friend", label: "친구",    path: "/friend" },
    { key: "todo",   label: "todo",    path: "/todo" },
    { key: "report", label: "월간리포트", path: "/report" },
    { key: "mypage", label: "마이페이지", path: "/mypage" },
];

const Navbar = () => {
    const { pathname } = useLocation();
    const navigate = useNavigate();

    return (
        <nav className="bg-white border-t border-[#E4E9EE] flex justify-around py-2">
            {TABS.map((tab) => {
                const active = pathname.startsWith(tab.path);
                return (
                    <button
                        key={tab.key}
                        onClick={() => navigate(tab.path)}
                        className={`flex flex-col items-center gap-1 px-3 py-1 text-[11px] ${
                            active ? "text-[#3D4D5C] font-semibold" : "text-[#8B9BAA]"
                        }`}
                    >
                        {/* 아이콘 위치: 탭별 Bootstrap Icon */}
                        <span
                            className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                active ? "bg-[#A8C8D8] text-white" : "bg-[#EEF2F5]"
                            }`}
                        />
                        <span>{tab.label}</span>
                    </button>
                );
            })}
        </nav>
    );
};

export default Navbar;