// hooks/useAudio.jsx
import React, { createContext, useContext, useRef, useState } from "react";

const AudioContext = createContext(null);

export function AudioProvider({ children }) {
    // useRef : DOM 객체에 직접 접근하기 위한 React Hook, document.getElementById()와 같은 역할
    const audioRef = useRef(null);
    const [currentMusic, setCurrentMusic] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const play = (music) => {
        if (!audioRef.current) return;
        // 같은 곡이면 이어서 재생, 다른 곡이면 src 교체
        if (currentMusic?.music_id !== music.music_id) {
            audioRef.current.src = music.file_url;
            setCurrentMusic(music);
        }
        audioRef.current.play();
        setIsPlaying(true);
    };

    const pause = () => {
        audioRef.current?.pause();
        setIsPlaying(false);
    };

    const toggle = () => {
        if (isPlaying) pause();
        else if (currentMusic) audioRef.current.play()
            .then(() => setIsPlaying(true))
            .catch((err) => {
                console.warn("재생 실패:", err);
                setIsPlaying(false);
            });
    };

    return (
        <AudioContext.Provider value={{ currentMusic, isPlaying, play, pause, toggle }}>
            <audio
                ref={audioRef}
                loop
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
            />
            {children}
        </AudioContext.Provider>
    );
}

export const useAudio = () => {
    const context = useContext(AudioContext);
    if (!context) throw new Error("useAudio 사용하기 위해 AudioProvider로 감싸야 합니다");
    return context;
};