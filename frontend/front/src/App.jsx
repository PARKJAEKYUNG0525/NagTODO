import React, { useState, useEffect } from "react";
import {
    createBrowserRouter,
    RouterProvider,
    Outlet,
    Navigate,
    useNavigate,
} from "react-router-dom";
import Navbar from "./Components/Navbar";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import Swal from "sweetalert2";
import Login from "./Pages/Login";
import Signup from "./Pages/Signup";
import Home from "./Pages/Home/index.jsx";
import Friend from "./Pages/Friend/index.jsx";
import Todo from "./Pages/Todo/index.jsx";
import Report from "./Pages/Report/index.jsx";
import MyPage from "./Pages/MyPage/index.jsx";

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
            <div className="bg-[#EEF2F5] flex flex-col w-full min-h-screen sm:w-110 sm:min-h-0 sm:h-auto sm:aspect-9/16 sm:rounded-[32px] sm:shadow-2xl overflow-hidden relative">
                <Outlet />
            </div>
        </div>
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
            { index: true, element: <Login /> },
            { path: "login", element: <Login /> },
            { path: "signup", element: <Signup /> },
            // { index: true, element: <Navigate to="/login" replace /> }, // 기본 경로를 /login으로 리다이렉트
            { path: "home", element: <Home /> },
            { path: "friend", element: <Friend/>},
            { path: "todo", element: <Todo/>},
            { path: "report", element: <Report/>},
            { path: "mypage", element: <MyPage/>},
            {
                element: (
                    // ProtectedRoute 내에 있는 컴포넌트만 보호되도록
                    // = 로그인 해야 사용할 수 있는 화면 목록
                    <ProtectedRoute>
                        {/* 여기에 <Friend/>,<Todo/>,<Report/>,<MyPage/>가 들어오게 됨*/}
                        {/*<Outlet />*/}
                    </ProtectedRoute>
                ),
                // 화면을 더 추가하고 싶다면 여기 children list에 추가하면 됨
                children: [
                    { path: "home", element: <Home /> },
                    { path: "friend", element: <Friend/>},
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