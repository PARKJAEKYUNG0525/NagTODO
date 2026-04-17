import React from "react";

const AuthLink = ({ message, buttonText, onClick }) => {
    return (
        <div className="mt-6 text-center text-[13px] text-gray-500 border-t border-gray-100 pt-4">
            <span className="font-light">{message}</span>{" "}
            <button
                type="button"
                onClick={onClick}
                className="ml-1 text-gray-900 hover:text-black font-semibold underline underline-offset-4 decoration-gray-300 hover:decoration-black transition-all duration-200"
            >
                {buttonText}
            </button>
        </div>
    );
};

export default AuthLink;