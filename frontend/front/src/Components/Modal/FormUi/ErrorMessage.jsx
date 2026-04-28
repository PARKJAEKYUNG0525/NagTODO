import React from "react";

const ErrorMessage = ({ error }) => {
    if (!error) return null;

    return (
        <div className="flex items-center justify-center gap-2 px-4 py-2 bg-red-50/50 border border-red-100 rounded-lg animate-in fade-in slide-in-from-top-1 duration-200">
            {/* 작은 경고 아이콘 (SVG) */}
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="w-4 h-4 text-shadow-orange-300 flex-shrink-0"
            >
                <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z"
                    clipRule="evenodd"
                />
            </svg>
            <p className="text-[12px] font-medium text-shadow-orange-200 leading-tight">
                {error}
            </p>
        </div>
    );
};

export default ErrorMessage;
