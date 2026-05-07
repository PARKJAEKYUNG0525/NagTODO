import React from "react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { BsListCheck, BsPeople, BsClipboardData, BsPerson, BsHouse } from 'react-icons/bs';

const TABS = [
    { key: "main",   label: "홈",      path: "/main", Icon: BsHouse },
    { key: "friend", label: "친구",    path: "/friend", Icon: BsPeople },
    { key: "todo",   label: "todo",    path: "/todo" , Icon: BsListCheck},
    { key: "report", label: "월간리포트", path: "/report", Icon: BsClipboardData },
    { key: "mypage", label: "마이페이지", path: "/mypage", Icon: BsPerson },
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
                        className={`flex flex-col items-center gap-1 px-3 py-1 text-[11px] cursor-pointer ${
                            active ? "text-[#3D4D5C] font-semibold" : "text-[#8B9BAA]"
                        }`}
                    >
                        {/* 아이콘 위치: 탭별 Bootstrap Icon */}
                        <div
                            className={`w-10 h-10 rounded-full flex items-center justify-center mb-1 ${
                                active ? "bg-[#A8C8D8] text-white" : "bg-[#EEF2F5] text-[#8B9BAA]"
                            }`}
                        >
                            {/* 탭별 아이콘 렌더링 */}
                            {tab.Icon && <tab.Icon size={20} />}
                        </div>

                        {/* 원 아래 텍스트 */}
                        <span>{tab.label}</span>
                    </button>
                );
            })}
        </nav>
    );
};

export default Navbar;