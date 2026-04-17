import React, {useEffect, useCallback, useState} from "react";
import {Link} from "react-router-dom";
import {useBoard} from "../../hooks/useBoard";

const Main = () => {
    const {loading, fetchBoards} = useBoard();
    const [boards, setBoards] = useState([]);

    const loadBoards = useCallback(async () => {
        const data = await fetchBoards();
        if (data) setBoards(data);
    }, [fetchBoards]);

    useEffect(() => {
        loadBoards();
    }, [loadBoards]);

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            <div className="flex justify-between items-center mb-10 border-b border-slate-100 pb-8">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 tracking-tighter">
                        전체 게시글
                    </h1>
                    <p className="text-slate-500 mt-2 text-sm">
                        게시글
                    </p>
                </div>

                <Link
                    to="/create-board"
                    className="
            bg-slate-900
            text-white
            px-6 py-2.5
            rounded-full
            font-bold
            text-sm
            hover:bg-slate-800
            transition-all
            active:scale-[0.95]
            shadow-sm
          ">
                    새 글 생성
                </Link>
            </div>

            {loading ? (
                <div className="flex flex-col items-center py-20">
                    <div
                        className="w-8 h-8 border-4 border-slate-200 border-t-slate-900 rounded-full animate-spin"></div>
                </div>
            ) : (
                <div className="grid gap-6">
                    {boards.length > 0 ? (
                        boards.map((board) => (
                            <div
                                key={board.id} // board_id에서 id로 속성명 확인 필요
                                className="group p-8 border border-slate-100 rounded-2xl bg-white hover:border-slate-200 transition-all duration-200 cursor-default"
                            >
                                <div className="space-y-3">
                                    <div className="flex items-center gap-3">
                    <span
                        className="text-[10px] uppercase tracking-widest font-black text-slate-400 border border-slate-200 px-2 py-0.5 rounded">
                      {board.category}
                    </span>
                                        <span className="text-xs text-slate-300">
                      {new Date(board.created_at).toLocaleDateString()}
                    </span>
                                    </div>

                                    <h2 className="text-xl font-bold text-slate-900 leading-tight">
                                        {board.title}
                                    </h2>

                                    <p className="text-slate-600 text-[15px] leading-relaxed whitespace-pre-wrap">
                                        {board.description}
                                    </p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-24 border-2 border-dashed border-slate-100 rounded-3xl">
                            <p className="text-slate-400 font-medium">
                                아직 등록된 게시글이 없습니다.
                            </p>
                            <Link
                                to="/create-board"
                                className="text-slate-900 font-bold text-sm mt-3 inline-block underline underline-offset-4"
                            >
                                게시글 쓰십시오.
                            </Link>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Main;
