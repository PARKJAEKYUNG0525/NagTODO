import React from "react";

const SubmitButton = ({ label }) => {
    return (
        <div className="flex justify-end">
            <button
                type="submit"
                className="
          px-8 py-3
          bg-slate-900
          text-white
          rounded-lg
          font-bold
          text-sm
          tracking-tight
          transition-all
          duration-200
          hover:bg-slate-800
          active:scale-[0.98]
          focus:outline-none
          focus:ring-2
          focus:ring-slate-900
          focus:ring-offset-2
          cursor-pointer
        "
            >
                {label}
            </button>
        </div>
    );
};

export default SubmitButton;
