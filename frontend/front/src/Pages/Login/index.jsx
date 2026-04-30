import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import {showWarningAlert} from "../../utils/alertUtils.js";

export default function Login({ onSignupClick }) {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const { login, error, setError } = useAuth();

    const handleLogin = async (e) => {
            e.preventDefault();
            setError("");
            setIsLoading(true);

            const success = await login(email, password);
            if (success) {
                navigate("/main");
            }
            setIsLoading(false);
        };

    const handleSignupClick = () => {
        if (onSignupClick) {
            onSignupClick();
        } else {
            navigate("/signup");
        }
    };

    return (
        // 모바일: 배경색이 카드색과 동일 → 전체화면처럼 보임
        // PC(sm 이상): 흰 배경에 카드 형태로 중앙 정렬
        <>
            <div className="bg-[#EEF2F5] flex flex-col flex-1 w-full px-6 py-10">
                {/* 프로필 아이콘 */}
                <div className="flex flex-col items-center">
                    <div className="mb-5 ">
                        <div className="w-20 h-20 rounded-full bg-[#9ECFDA]"/>
                    </div>

                    {/* 타이틀 */}
                    <h1 className="text-[32px] font-bold text-[#2D3748] tracking-tight mb-2">
                        Welcome
                    </h1>
                    <p className="text-sm text-[#718096] mb-8">
                        로그인하고 오늘의 할 일을 시작하세요
                    </p>
                </div>

                {/* 폼 */}
                <form onSubmit={handleLogin} className="w-full flex flex-col gap-4">
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">이메일</label>
                        <input
                            type="email"
                            placeholder="user@user.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">비밀번호</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="mt-2 py-4 rounded-xl bg-[#9ECFDA] text-white text-base font-semibold tracking-wide transition-colors duration-200 hover:bg-[#7BBFCD] disabled:opacity-70 cursor-pointer"
                    >
                        {isLoading ? "로그인 중..." : "로그인"}
                    </button>
                </form>

                {/* 회원가입 링크 */}
                <div className="mt-6 flex items-center justify-center gap-2">
                    <span className="text-xs text-[#718096]">계정이 없으신가요?</span>
                    <button
                        onClick={handleSignupClick}
                        className="text-xs font-semibold text-[#7BBFCD] hover:text-[#5AAAB8] transition-colors duration-200 bg-transparent border-none cursor-pointer p-0"
                    >
                        회원가입
                    </button>
                </div>
            </div>
        </>
    );
}