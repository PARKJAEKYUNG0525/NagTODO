import { useState, createContext, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { showErrorAlert, showSuccessAlert } from "../utils/alertUtiles.js";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const [user, setUser] = useState(null);
    const navigate = useNavigate();


    const login = async (email, password) => {
        try {
            // post(URL, data) 형식
            const response = await api.post("/users/", {email, username, password, birthday});

            // 사용자 로그인 성공 = 인증 성공
            if (response.status === 200) {
                setUser(response.data);
                setIsAuthenticated(true);
                await verifyJWT();
                showSuccessAlert("환영합니다");
                return true;
            }
        }
        catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "로그인에 실패했습니다.");
            setIsAuthenticated(false);
            return false;
        }
    };

    const signup = async ({email, username, password, confirmPassword}) => {
        if (!email.includes("@")) {
            setError("유효한 이메일을 입력하세요");
            return false;
        }
        if (username.length < 2) {
            setError("이름은 최소 2글자 이상이어야 합니다");
            return false;
        }
        if (password.length < 5) {
            setError("비밀번호는 최소 5글자 이상이어야 합니다");
            return false;
        }
        if (password !== confirmPassword) {
            setError("비밀번호가 일치하지 않습니다");
            return false;
        }
        try {
            // user/signup은 scheme/users.py-UserCreate 참고
            const response = await api.post("/users/", {
                email,
                username,
                pw: password,        
                birthday,            
            });
            if (response.status === 200) {
                showSuccessAlert("회원가입이 완료되었습니다");
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "회원가입에 실패했습니다");
        }
    };

    const logout = async () => {
        try {
            const response = await api.post("/users/logout");
            setIsAuthenticated(false);
            setUser(null);

            if (response.status === 200) {
                showSuccessAlert("로그아웃 되었습니다");
                navigate("/");
            }
        }
        catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "로그아웃에 실패하였습니다")
        }
        finally {
            setIsAuthenticated(false);
            setUser(null);
            navigate("/");
        }
    };

    // JWT 토큰 검증 + 사용자 상태 관리 함수
    // 현재 로그인한 사용자인지 확인하기 위함
    // 성공 시 서버가 사용자 정보 반환
    const verifyJWT = async () => {
        try {
            const response = await api.get("users/me");
            setIsAuthenticated(true);
            setUser(response.data);
            return true;
        }
        catch (error) {
            if (error.response?.status === 401) {
                const detail = error.response.data?.detail;

                // if (detail ===  "Access token expired") {
                //     showErrorAlert("세션이 만료되었습니다. 다시 로그인해주세요");
                //     navigate("/");
                // }
            }
            setIsAuthenticated(false);
            setUser(null);
            return false;
        }
    };

    // mount 시 JWT 인증
    // : 컴포넌트 화면에 첫 랜더링 될 때 사용자 JWT 상태를 확인하려고
    // : 세션 유지, 자동 로그인 체크 시 활용, JWT 인증에서의 필수 패턴
    useEffect(() => {
        (async () => {
            await verifyJWT();
        })(); // 여기 끝에 있는 소괄호()가 함수를 바로 실행함, 함수() 형태인 것
    }, []);

    return (
        <AuthContext.Provider
            value={{ error, setError, isAuthenticated, login, signup, logout,user }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth 사용하기 위해 AuthProvider로 감싸야한다");
    }
    return context;
};