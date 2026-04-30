import React, { createContext, useContext, useRef, useState } from "react";
import {showWarningAlert} from "@/utils/alertUtils.js";

const MusicContext = createContext(null);

export function MusicProvider({ children }) {
    // useRef : DOM 객체에 직접 접근하기 위한 React Hook, document.getElementById()와 같은 역할
    const musicRef = useRef(null);
    const [currentMusic, setCurrentMusic] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const play = (music) => {
        if (!musicRef.current) return;
        if (currentMusic?.music_id !== music.music_id) {
            musicRef.current.src = music.file_url;
            setCurrentMusic(music);
        }
        musicRef.current.play().catch((error) => console.warn("재생 실패:", error));
        setIsPlaying(true);
    };

    const pause = () => {
        musicRef.current?.pause();
        setIsPlaying(false);
    };

    const toggle = () => {
        if (isPlaying) pause();
        else if (currentMusic) musicRef.current.play()
            .then(() => setIsPlaying(true))
            .catch((error) => {
                showWarningAlert({title : "음악 재생에 실패했습니다.", message : error.message});
                // console.warn("재생 실패:", error);
                setIsPlaying(false);
            });
    };

    return (
        <MusicContext.Provider value={{ currentMusic, isPlaying, play, pause, toggle }}>
            <audio
                ref={musicRef}
                loop
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
            />
            {children}
        </MusicContext.Provider>
    );
}

export const useMusic = () => {
    const context = useContext(MusicContext);
    if (!context) throw new Error("useMusic 사용하기 위해 MusicProvider로 감싸야 합니다");
    return context;
};