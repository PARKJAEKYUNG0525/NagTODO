import React from "react";


const ProfileHolder = ({name}) => {
    const initial = name ? name : "U";

    return (
        <div
            className="w-9 h-9 bg-gray-900 text-white flex items-center justify-center rounded-full font-semibold text-[13px] hover:bg-black transition-colors shadow-sm">
            {initial}
        </div>
    );
};

const AuthButtons = (
    {
        userName,
        isAuthenticated,
        isOpen,
        setIsOpen,
        onLogoutClick,
        onLoginClick,
        onSignupClick,
    }) => {
    return (
        <div className="hidden md:flex items-center ml-auto">
            {isAuthenticated ? (

                <div className="relative ml-4">
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="flex items-center focus:outline-none group"
                    >
                        <ProfileHolder name={userName}/>

                        <svg
                            className={`w-4 h-4 ml-1 text-gray-400 group-hover:text-gray-900 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 9l-7 7-7-7"
                            />
                        </svg>
                    </button>

                    {isOpen && (
                        <div
                            className="absolute right-0 mt-3 w-40 bg-white rounded-xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] border border-gray-100 py-2 z-50 animate-in fade-in slide-in-from-top-2">
                            <button
                                onClick={onLogoutClick}
                                className="block w-full text-left px-4 py-2.5 text-[13px] text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
                            >
                                로그아웃
                            </button>
                        </div>
                    )}
                </div>
            ) : (

                <div className="flex items-center space-x-2">
                    <button
                        onClick={onLoginClick}
                        className="text-gray-600 hover:text-black px-4 py-2 text-[14px] font-medium transition-colors"
                    >
                        로그인
                    </button>
                    <button
                        onClick={onSignupClick}
                        className="bg-gray-900 text-white hover:bg-black px-5 py-2.5 rounded-full text-[13px] font-semibold transition-all active:scale-95 shadow-sm"
                    >
                        시작하기
                    </button>
                </div>
            )}
        </div>
    );
};

export default AuthButtons;