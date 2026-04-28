import { useState, createContext, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { showSuccessAlert, showWarningAlert } from "../utils/alertUtiles.js";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [error, setError] = useState("");
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState(null);
    const navigate = useNavigate();


    const login = async (email, password) => {
        try {
            const response = await api.post("/users/login", { email, pw: password })
            if (response.status === 200) {
                setUser(response.data.user);
                setIsAuthenticated(true);
                await verifyJWT();
                showSuccessAlert({title:"환영합니다"});
                navigate("/main");
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

    const signup = async ({email, username, password, confirmPassword, birthday}) => {
        try {
            const response = await api.post("/users/", { email, username, pw: password, birthday })
            if (response.status === 201) {
                showSuccessAlert({title:"(useAuth)회원가입이 완료되었습니다"});
                return true;
            }
        } catch (error) {
            console.log(error);
            setError(error.response?.data.detail || "(useAuth)회원가입에 실패했습니다");
        }
    };

    const logout = async () => {
        try {
            const response = await api.post("/users/logout");
            setIsAuthenticated(false);
            setUser(null);

            if (response.status === 200) {
                showSuccessAlert({title:"로그아웃 되었습니다"});
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

                if (detail ===  "Access token expired") {
                    showWarningAlert("세션이 만료되었습니다. 다시 로그인해주세요");
                    navigate("/");
                }
            }
            setIsAuthenticated(false);
            setUser(null);
            return false;
        }
        finally {
            setIsLoading(false); 
        }
    };

    // JWT 인증하기 위해(확인 및 검증)
    // 세션 유지, 자동 로그인 체크 시 활용, JWT 인증에서의 필수 패턴
    useEffect(() => {
        (async () => {
            await verifyJWT();
        })();
    }, []);

    return (
        <AuthContext.Provider
            value={{ error, setError, isAuthenticated, login, signup, logout, user, setUser }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth 사용하기 위해 AuthProvider로 감싸야한다");
    }
    return context;
};