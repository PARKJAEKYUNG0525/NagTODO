import { createContext, useContext, useState } from "react";

const InterferenceContext = createContext(null);

export const InterferenceProvider = ({ children }) => {
    const [popup, setPopup] = useState({ open: false, loading: false, feedback: null });

    const showLoading = () => setPopup({ open: true, loading: true, feedback: null });
    const showFeedback = (feedback) => setPopup({ open: true, loading: false, feedback });
    const dismiss = () => setPopup({ open: false, loading: false, feedback: null });

    return (
        <InterferenceContext.Provider value={{ popup, showLoading, showFeedback, dismiss }}>
            {children}
        </InterferenceContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useInterference = () => {
    const ctx = useContext(InterferenceContext);
    if (!ctx) throw new Error("InterferenceProvider로 감싸야 합니다");
    return ctx;
};
