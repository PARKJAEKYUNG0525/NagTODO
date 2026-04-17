import React, { useState, useEffect } from "react";
import {
    createBrowserRouter,
    RouterProvider,
    Outlet,
    Navigate,
    useNavigate,
} from "react-router-dom";
import Navbar from "./Components/Navbar";
import LoginModal from "./Components/Modal/LoginModal";
import SignupModal from "./Components/Modal/SignupModal";
import Main from "./Pages/Main";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import Swal from "sweetalert2";
import CreateBoard from "./Pages/CreateBoard";

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, isLoading } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        // 로딩이 끝났는데 인증이 안 된 경우에만 알림 후 이동
        if (!isLoading && !isAuthenticated) {
            Swal.fire({
                icon: "warning",
                title: "로그인 필요",
                text: "로그인이 필요한 서비스입니다.",
                confirmButtonColor: "#10B981",
            }).then(() => {
                navigate("/", { replace: true });
            });
        }
    }, [isAuthenticated, isLoading, navigate]);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
            </div>
        );
    }

    return isAuthenticated ? children : null;
};


const RootLayout = () => {
    const [isLoginOpen, setIsLoginOpen] = useState(false);
    const [isSignupOpen, setIsSignupOpen] = useState(false);

    // 로그인 버튼 클릭 시 로그인 창 열기
    const onLoginClick = () => {
        // 회원가입 창 닫고
        setIsSignupOpen(false);
        // 로그인 창 열기
        setIsLoginOpen(true);
    }
    // 회원가입 버튼 클릭 시 회원가입 창 열기
    const onSignupClick = () => {
        // 로그인 창 닫고
        setIsLoginOpen(false);
        // 회원가입 창 열기
        setIsSignupOpen(true);
    }
    // 로그인&회원가입 창 전부 닫기
    const handleCloseModals = () => {
        setIsLoginOpen(false);
        setIsSignupOpen(false);
    }

    return (
        <>
            <Navbar onLoginClick={onLoginClick} onSignupClick={onSignupClick} />
            <main className="flex-grow container mx-auto px-4 py-8">
                <Outlet />
            </main>
            <LoginModal
                isOpen={isLoginOpen}
                onClose={handleCloseModals}
                onSignupClick={onSignupClick}
            />
            <SignupModal
                isOpen={isSignupOpen}
                onClose={handleCloseModals}
                onLoginClick={onLoginClick}
            />
        </>
    );
};

const router = createBrowserRouter([
    {
        path: "/",
        element: (
            // AuthProvider를 여기에 두어 모든 자식(ProtectedRoute 포함)이 context를 쓸 수 있게
            // AuthProvider : 인증 상태를 앱 전체에 공유하기 위한 컴포넌트
            <AuthProvider>
                <RootLayout />
            </AuthProvider>
        ),
        children: [
            { index: true, element: <Main /> },
            {
                element: (
                    // ProtectedRoute 내에 있는 컴포넌트만 보호되도록
                    <ProtectedRoute>
                        {/* 여기에 <CreateBoard />가 들어오게 됨*/}
                        <Outlet />
                    </ProtectedRoute>
                ),
                // 화면을 더 추가하고 싶다면 여기 children list에 추가하면 됨
                children: [{ path: "create-board", element: <CreateBoard /> }],
            },
        ],
    },
]);

const App = () => {
    // 위에 작성한 router를 RouterProvider를 통해 전달
    // RouterProvider : 앱 전체에 라우터 적용
    return <RouterProvider router={router} />;
};

export default App;