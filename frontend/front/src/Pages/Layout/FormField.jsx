import React from "react";

const FormField = ({
                       label,
                       name,
                       value,
                       onChange,
                       placeholder,
                       required = true,
                       type = "text",
                   }) => {

    const baseInputStyles = `
    w-full px-4 py-2.5 
    bg-white 
    border border-slate-300 
    rounded-lg 
    text-slate-900 
    placeholder:text-slate-400 
    transition-all 
    duration-200
    focus:outline-none 
    focus:border-slate-900 
    focus:ring-1 focus:ring-slate-900
    disabled:bg-slate-50 disabled:text-slate-500
  `;

    return (
        <div className="space-y-1.5">
            <label className="block text-sm font-bold text-slate-800">
                {label}
                {required && <span className="ml-1 text-rose-500">*</span>}
            </label>

            {type === "textarea" ? (
                <textarea
                    name={name}
                    value={value}
                    onChange={onChange}
                    required={required}
                    className={`${baseInputStyles} h-32 resize-none`}
                    placeholder={placeholder}
                />
            ) : (
                <input
                    type={type}
                    name={name}
                    value={value}
                    onChange={onChange}
                    required={required}
                    className={baseInputStyles}
                    placeholder={placeholder}
                />
            )}
        </div>
    );
};

export default FormField;