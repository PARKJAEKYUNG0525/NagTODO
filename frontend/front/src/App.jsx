import React, { useState, useEffect } from "react";
import {
    createBrowserRouter,
    RouterProvider,
    Outlet,
    Navigate,
    useNavigate,
} from "react-router-dom";
import Navbar from "./Components/Navbar";
// import Notification from "./Components/Notification";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { InterferenceProvider } from "./hooks/useInterference";
import InterferencePopup from "./Components/Modal/InterferencePopup";
import Swal from "sweetalert2";
import Login from "./Pages/Login";
import Signup from "./Pages/Signup";
import Home from "./Pages/Home/index.jsx";
import Friend from "./Pages/Friend/index.jsx";
import Todo from "./Pages/Todo/index.jsx";
import Report from "./Pages/Report/index.jsx";
import MyPage from "./Pages/MyPage/index.jsx";
import FriendDetail from "./Pages/FriendDetail/index.jsx";
import { MusicProvider } from "@/hooks/useMusic.jsx";
import { ImgProvider, useImg } from "./hooks/useImg";
import api from "@/utils/api.js";


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
    return (
        <div className="min-h-screen bg-gray-200 flex items-center justify-center font-sans">
            <main className="bg-[#EEF2F5] flex flex-col w-full min-h-screen sm:w-[390px] sm:min-h-0 sm:h-auto sm:aspect-[390/844] sm:rounded-[32px] sm:shadow-2xl overflow-hidden relative">
                <Outlet />
                <InterferencePopup />
            </main>
        </div>
    );
};

const ProtectedLayout = () => {
    const { currentBg, getUserBg } = useImg();

    useEffect(() => { getUserBg(); }, []);

    return (
        <MusicProvider>
            <div
                className="flex-1 flex flex-col bg-[#F4F7FA] bg-cover bg-center"
                style={
                    currentBg
                        ? {
                            backgroundImage: `linear-gradient(rgba(255,255,255,0.4), rgba(255,255,255,0.4)), url(${api.defaults.baseURL}${currentBg.file_url})`,
                        }
                        : undefined
                }
            >
                <Outlet />
            </div>
            <Navbar />
        </MusicProvider>
    );
};

const router = createBrowserRouter([
    {
        path: "/",
        element: (
            <InterferenceProvider>
                <AuthProvider>
                    <ImgProvider>
                        <RootLayout />
                    </ImgProvider>
                </AuthProvider>
            </InterferenceProvider>
        ),
        children: [
            { index: true, element: <Login /> },
            { path: "login", element: <Login /> },
            { path: "signup", element: <Signup /> },
            // { index: true, element: <Navigate to="/login" replace /> }, // 기본 경로를 /login으로 리다이렉트
            // { path: "main", element: <Home /> },
            // { path: "friend", element: <Friend/>},
            // { path: "todo", element: <Todo/>},
            // { path: "report", element: <Report/>},
            // { path: "mypage", element: <MyPage/>},
            {
                element: (
                    <ProtectedRoute>
                        <ProtectedLayout />
                    </ProtectedRoute>
                ),
                children: [
                    { path: "main", element: <Home /> },
                    { path: "friend", element: <Friend/>},
                    { path: "friend/:userId", element: <FriendDetail/>},
                    { path: "todo", element: <Todo/>},
                    { path: "report", element: <Report/>},
                    { path: "mypage", element: <MyPage/>}
                ],
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