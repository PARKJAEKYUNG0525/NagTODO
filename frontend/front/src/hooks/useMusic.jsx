import api, { buildFileUrl } from "@/utils/api.js";
import React, {createContext, useCallback, useContext, useRef, useState} from "react";
import {showWarningAlert} from "@/utils/alertUtils.js";

const MusicContext = createContext(null);

export function MusicProvider({ children }) {
    // useRef : DOM 객체에 직접 접근하기 위한 React Hook, document.getElementById()와 같은 역할
    const musicRef = useRef(null);
    const [currentMusic, setCurrentMusic] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [musics, setMusics] = useState([]);

    const getAllMusics = useCallback(async () => {
        try {
            const response = await api.get("/musics");
            setMusics(Array.isArray(response.data) ? response.data : []);
        } catch (error) {
            showWarningAlert({title:"음악 목록을 불러오는 데 실패했습니다.", text: error.message});
            setMusics([]);
        }
    }, []);

    const play = (music) => {
        if (!musicRef.current) return;
        if (currentMusic?.music_id !== music.music_id) {
            // baseURL + 상대경로
            // api.defaults.baseURL은 import.meta.env.VITE_API_BASE_URL과 같음;
            musicRef.current.src = buildFileUrl(music.file_url);
            setCurrentMusic(music);
        }
        musicRef.current.play().catch((error) => showWarningAlert({title:"음악 재생에 실패했습니다.", text: error.message}));
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
                showWarningAlert({title : "음악 재생에 실패했습니다.", text : error.message});
                setIsPlaying(false);
            });
    };

    return (
        <MusicContext.Provider value={{ currentMusic, isPlaying, play, pause, toggle, musics, getAllMusics }}>
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