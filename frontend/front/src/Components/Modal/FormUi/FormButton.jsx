import React from "react";

const FormButton = (
    {
        type = "submit",
        onClick,
        children,
        className,
        disabled,
    }
    ) => {
    return (
        <button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`
            bg-gray-900 text-white text-[14px] font-semibold
            rounded-xl 
            hover:bg-black active:scale-[0.98]
            cursor-pointer 
            disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed
            transition-all duration-200 shadow-sm
            ${className}
            `}
        >
            {children}
        </button>
    );
};

export default FormButton;