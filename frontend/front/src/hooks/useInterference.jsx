import { createContext, useContext, useState } from "react";

const InterferenceContext = createContext(null);

const INITIAL = { open: false, loading: false, todoTitle: null, feedback: null, globalRate: null, personalRate: null, similarCount: null, topFailures: [] };

export const InterferenceProvider = ({ children }) => {
    const [popup, setPopup] = useState(INITIAL);

    const showLoading = () => setPopup({ ...INITIAL, open: true, loading: true });

    const showFeedback = (todoTitle, interference) => setPopup({
        open: true,
        loading: false,
        todoTitle,
        feedback: interference?.feedback ?? "잘 좀 하렴",
        globalRate: interference?.global_rate ?? null,
        personalRate: interference?.personal_rate ?? null,
        similarCount: interference?.similar_count ?? null,
        topFailures: (interference?.similar_failures ?? []).slice(0, 3),
    });

    const dismiss = () => setPopup(INITIAL);

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
