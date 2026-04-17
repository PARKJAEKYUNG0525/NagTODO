import { useState } from "react";
import Title from "./layout/Title";
import { useAuth } from "../../hooks/useAuth";
import AuthButtons from "./auth/AuthButtons";


function Navbar({ onLoginClick, onSignupClick }) {
    const { logout, isAuthenticated, user } = useAuth();

    const [isOpen, setIsOpen] = useState(false);

    const onLogoutClick = () => {
        logout();
        setIsOpen(false); // 로그아웃 시 드롭다운 닫기
    };

    const onCategoryClick = (category) => {
        console.log(category);
    };

    return (
        <nav className="bg-black">
            <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-14 md:h-20">
                    <div className="flex items-center flex-1">
                        <Title />
                    </div>

                    <AuthButtons
                        userName = {user?.username || "User"}
                        isAuthenticated={isAuthenticated}
                        isOpen={isOpen}
                        setIsOpen={setIsOpen}
                        onLogoutClick={onLogoutClick}
                        onLoginClick={onLoginClick}
                        onSignupClick={onSignupClick}
                    />
                </div>
            </div>
        </nav>
    );
}

export default Navbar;