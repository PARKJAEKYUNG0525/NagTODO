import React from "react";

const FormInput = (
    {
        type,
        name,
        value,
        onChange,
        placeholder,
        required = true,
        className, // 추가적인 스타일 확장을 위해 유지
    }
    ) => {
    return (
        <div className="w-full">
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                required={required}
                className={`
          w-full px-4 py-3
          text-[14px] text-gray-900 
          bg-gray-50/50 border border-gray-200 
          rounded-xl outline-none
          placeholder:text-gray-400
          focus:border-gray-900 focus:bg-white focus:ring-0
          transition-all duration-200
          ${className}
        `}
            />
        </div>
    );
};

export default FormInput;