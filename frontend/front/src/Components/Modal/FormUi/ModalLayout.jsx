import React, { useEffect } from "react";

const ModalLayout = ({ isOpen, onClose, children, title }) => {

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">

            <div
                className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity cursor-pointer "
                onClick={onClose}
            />

            <div className="relative bg-white rounded-[24px] shadow-2xl max-w-md w-full overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-300">

                <div className="flex justify-between items-center px-8 pt-8 pb-4">
                    <h2 className="text-[22px] font-bold text-gray-900 tracking-tight">
                        {title}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 -mr-2 text-gray-400 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-all cursor-pointer "
                        aria-label="Close modal"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2.5"
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>
                <div className="px-8 pb-10">{children}</div>
            </div>
        </div>
    );
};

export default ModalLayout;