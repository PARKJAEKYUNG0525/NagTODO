import { useState, useEffect  } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Signup({ onLoginClick }) {
    const navigate = useNavigate();
    const { signup, error, setError } = useAuth();
    useEffect(() => {
        setError("");
    }, []);

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        birthYear: "",
        birthMonth: "",
        birthDay: "",
    });
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        setError("");
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        setError("");

        if (form.username.length < 2) {
            setError("(index)닉네임은 최소 2글자 이상이어야 합니다");
            return;
        }

        const pwRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{8,30}$/;
        if (!pwRegex.test(form.password)) {
            setError("(index)비밀번호는 8~30자, 영문/숫자/특수문자를 포함해야 합니다");
            return;
        }

        if (form.password !== form.confirmPassword) {
            setError("(index)비밀번호가 일치하지 않습니다");
            return;
        }

        if (!form.birthYear || !form.birthMonth || !form.birthDay) {
            setError("(index)생년월일을 모두 선택해주세요");
            return;
        }

        setIsLoading(true);
        try {
            const success = await signup({
                email: form.email,
                username: form.username,
                password: form.password,
                confirmPassword: form.confirmPassword,
                // "YYYY-MM-DD" 형식으로 전달
                birthday: `${form.birthYear}-${String(form.birthMonth).padStart(2, "0")}-${String(form.birthDay).padStart(2, "0")}`,
            });

            if (success) {
                setForm({
                    username: "",
                    email: "",
                    password: "",
                    confirmPassword: "",
                    birthYear: "",
                    birthMonth: "",
                    birthDay: "",
                });
                navigate("/");
                // handleLoginClick();
            }
        } catch (err) {
            console.error("Signup error:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLoginClick = () => {
        if (onLoginClick) {
            onLoginClick();
        } else {
            navigate("/");
        }
    };

    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 100 }, (_, i) => currentYear - i);   // 올해~100년 전
    const months = Array.from({ length: 12 }, (_, i) => i + 1);
    const days = Array.from({ length: 31 }, (_, i) => i + 1);

    const selectStyle = {
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%234A5568' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E")`,
        backgroundRepeat: "no-repeat",
        backgroundPosition: "right 12px center",
        paddingRight: "32px",
    };

    return (
        <>
            <div className="bg-[#EEF2F5] flex flex-col flex-1 w-full px-6 py-10">
                {/* 타이틀 */}
                <h1 className="text-2xl font-bold text-[#2D3748] tracking-tight mb-8">
                    회원가입
                </h1>

                <form onSubmit={handleSignup} className="flex flex-col gap-4">
                    {/* 이름 */}
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">닉네임</label>
                        <input
                            type="text"
                            name="username"
                            placeholder="홍길동"
                            value={form.username}
                            onChange={handleChange}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    {/* 이메일 */}
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">이메일</label>
                        <input
                            type="email"
                            name="email"
                            placeholder="name@example.com"
                            value={form.email}
                            onChange={handleChange}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    {/* 비밀번호 */}
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">비밀번호</label>
                        <input
                            type="password"
                            name="password"
                            placeholder="••••••••"
                            value={form.password}
                            onChange={handleChange}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    {/* 비밀번호 확인 */}
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">비밀번호 확인</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            placeholder="••••••••"
                            value={form.confirmPassword}
                            onChange={handleChange}
                            className="px-4 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA]"
                        />
                    </div>

                    {/* 생년월일 - 년/월/일 */}
                    <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-medium text-[#4A5568]">생년월일</label>
                        <div className="flex gap-2">
                            {/* 년도 */}
                            <select
                                name="birthYear"
                                value={form.birthYear}
                                onChange={handleChange}
                                className="flex-1 px-3 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA] appearance-none cursor-pointer"
                                style={selectStyle}
                            >
                                <option value="">년</option>
                                {years.map((y) => (
                                    <option key={y} value={y}>{y}년</option>
                                ))}
                            </select>
                            {/* 월 */}
                            <select
                                name="birthMonth"
                                value={form.birthMonth}
                                onChange={handleChange}
                                className="w-24 px-3 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA] appearance-none cursor-pointer"
                                style={selectStyle}
                            >
                                <option value="">월</option>
                                {months.map((m) => (
                                    <option key={m} value={m}>{m}월</option>
                                ))}
                            </select>
                            {/* 일 */}
                            <select
                                name="birthDay"
                                value={form.birthDay}
                                onChange={handleChange}
                                className="w-24 px-3 py-3.5 rounded-xl border-2 border-white bg-white text-[15px] text-[#2D3748] outline-none shadow-sm transition-colors duration-200 focus:border-[#9ECFDA] appearance-none cursor-pointer"
                                style={selectStyle}
                            >
                                <option value="">일</option>
                                {days.map((d) => (
                                    <option key={d} value={d}>{d}일</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* 에러 메시지 */}
                    {error && (
                        <p className="text-xs text-red-500 font-medium -mt-1">{error}</p>
                    )}

                    {/* 회원가입 버튼 */}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="mt-2 py-4 rounded-xl bg-[#9ECFDA] text-white text-base font-semibold tracking-wide transition-colors duration-200 hover:bg-[#7BBFCD] disabled:opacity-70 cursor-pointer"
                    >
                        {isLoading ? "처리 중..." : "회원가입"}
                    </button>
                </form>

                {/* 로그인 링크 */}
                <div className="mt-6 flex items-center justify-center gap-2">
                    <span className="text-xs text-[#718096]">이미 계정이 있으신가요?</span>
                    <button
                        onClick={handleLoginClick}
                        className="text-xs font-semibold text-[#7BBFCD] hover:text-[#5AAAB8] transition-colors duration-200 bg-transparent border-none cursor-pointer p-0"
                    >
                        로그인
                    </button>
                </div>
            </div>
        </>
    );
}