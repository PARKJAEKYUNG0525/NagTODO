import React, { useState, useEffect } from "react";
import { showWarningDialog, showSuccessAlert } from "@/utils/alertUtils.js";
import { useAuth } from "../../hooks/useAuth";

/**
 * Mypage 화면 (통합본)
 * isAdmin 여부에 따라 완전히 다른 UX.
 *
 * ───── 비관리자 ─────
 *  [1] 기본: 프로필 카드 + 모드 변경 (엄격하게 / 덜 엄격하게)
 *  [2] 내 정보 수정
 *
 * ───── 관리자 ─────
 *  [A] 카테고리 설정
 *  [B] 카테고리 수정 (인라인)
 *  [C] 카테고리 삭제 (체크 모드 + alertUtils.showWarningDialog)
 *
 * ※ 9:16 프레임 / 하단 Navbar 는 App.jsx 담당.
 */
export default function MyPage() {
    const { user } = useAuth();
    const [isAdmin, setIsAdmin] = useState(false);
    const [strictMode, setStrictMode] = useState("strict"); // "strict" | "less"
    const [view, setView] = useState("main"); // "main" | "edit-profile"
    const [form, setForm] = useState({ username: "", email: "", password: "", confirmPassword: "", birthYear: "",
    birthMonth: ""});


    const [adminMode, setAdminMode] = useState("default"); // "default" | "edit" | "delete"
    const [editingCategoryId, setEditingCategoryId] = useState(null);
    const [editingValue, setEditingValue] = useState("");
    const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);
    const [categories, setCategories] = useState([
        { id: 1, name: "공부" },
        { id: 2, name: "업무" },
        { id: 3, name: "운동" },
        { id: 4, name: "일상" },
        { id: 5, name: "약속" },
        { id: 6, name: "기타" },
    ]);
    const [draggedIdx, setDraggedIdx] = useState(null);


    useEffect(() => {
        if (user) {
            console.log("birthday 값:", user.birthday);
            const [year, month] = (user.birthday || "").split("-");
            console.log("year:", year, "month:", month);
        }
    }, [user]);

    useEffect(() => {
        const checkAdmin = () => false;
        setIsAdmin(checkAdmin());
        const loadStrictMode = () => "strict";
        setStrictMode(loadStrictMode());
    }, []);

    useEffect(() => {
        // TODO: API 로 strictMode 변경 저장
    }, [strictMode]);

    useEffect(() => {
        if (user) {
            const [year, month] = (user.birthday || "").split("-");
            setForm(prev => ({
                ...prev,
                username: user.username || "",
                email: user.email || "",
                birthYear: year || "",
                birthMonth: month || "",
            }));
        }
    }, [user]);

    const handleNotification = () => alert("알림 아이콘 클릭");

    const handleWithdraw = () => alert("회원탈퇴 안내");
    const handleEditProfile = () => setView("edit-profile");
    const handleCancelEditProfile = () => setView("main");
    const handleSaveProfile = () => {
        alert("프로필 저장");
        setView("main");
    };
    const handleChangeProfileImage = () => alert("프로필 사진 변경");
    const handleSelectStrictMode = (mode) => {
        setStrictMode(mode);
        alert(`모드 변경: ${mode === "strict" ? "엄격하게" : "덜 엄격하게"}`);
    };

    const handleEditAdmin = () => alert("관리자 정보 수정");

    const handleEnterDeleteMode = () => {
        setAdminMode("delete");
        setEditingCategoryId(null);
    };
    const handleCancelDeleteMode = () => {
        setAdminMode("default");
        setSelectedCategoryIds([]);
    };
    const handleToggleCategorySelect = (id) => {
        setSelectedCategoryIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    };
    const handleDeleteSelected = async () => {
        if (selectedCategoryIds.length === 0) {
            alert("삭제할 카테고리를 선택하세요.");
            return;
        }
        const ok = await showWarningDialog({
            title: "카테고리를 삭제할까요?",
            text: "삭제된 카테고리는 복구할 수 없어요.",
        });
        if (ok) {
            setCategories((prev) =>
                prev.filter((c) => !selectedCategoryIds.includes(c.id))
            );
            setSelectedCategoryIds([]);
            setAdminMode("default");
            showSuccessAlert({ title: "삭제 완료" });
        }
    };

    const handleStartEdit = (category) => {
        setAdminMode("edit");
        setEditingCategoryId(category.id);
        setEditingValue(category.name);
    };
    const handleCancelEdit = () => {
        setAdminMode("default");
        setEditingCategoryId(null);
        setEditingValue("");
    };
    const handleConfirmEdit = () => {
        if (!editingValue.trim()) {
            alert("카테고리 이름을 입력하세요.");
            return;
        }
        setCategories((prev) =>
            prev.map((c) =>
                c.id === editingCategoryId ? { ...c, name: editingValue.trim() } : c
            )
        );
        setAdminMode("default");
        setEditingCategoryId(null);
        setEditingValue("");
        alert("카테고리 수정 완료");
    };

    // 드래그 앤 드롭
    const handleDragStart = (idx) => setDraggedIdx(idx);
    const handleDragOver = (e) => e.preventDefault();
    const handleDrop = (idx) => {
        if (draggedIdx === null || draggedIdx === idx) return;
        const next = [...categories];
        const [moved] = next.splice(draggedIdx, 1);
        next.splice(idx, 0, moved);
        setCategories(next);
        setDraggedIdx(null);
    };
    const handleDragEnd = () => setDraggedIdx(null);

    const NotificationBell = () => (
        <button
            onClick={handleNotification}
            className="relative w-12 h-12 rounded-full bg-[#4A5C6E] flex items-center justify-center shadow-sm shrink-0"
        >
            {/* 아이콘 위치: 알림 벨 (bi-bell-fill) */}
            <span className="w-5 h-5 block" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[#A8C8D8]" />
        </button>
    );

    

    // ====== 렌더: 비관리자 - 내 정보 수정 ======
    if (!isAdmin && view === "edit-profile") {
        return (
            <div className="flex-1 overflow-y-auto px-8 pt-10 pb-10 flex flex-col">
                <h1 className="text-xl font-bold text-[#3D4D5C]">내 정보 수정</h1>

                <div className="mt-6 flex flex-col items-center">
                    <div className="w-24 h-24 rounded-full bg-[#A8C8D8]">
                        {/* 아이콘 위치: 프로필 이미지 (bi-person-fill) */}
                    </div>
                    <button
                        onClick={handleChangeProfileImage}
                        className="mt-2 text-xs text-[#8B9BAA]"
                    >
                        프로필 사진 변경
                    </button>
                </div>

                <div className="mt-6 flex flex-col gap-4">
                    <Field label="닉네임" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} />
                    <Field label="이메일" value={form.email} readOnly />
                    <Field label="비밀번호" type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} />
                    <Field
                        label="비밀번호 확인"
                        type="password"
                        value={form.confirmPassword} onChange={(e) => setForm({...form, confirmPassword: e.target.value})}
                    />

                    <div>
                        <label className="block text-xs text-[#8B9BAA] mb-2">생일</label>
                        <div className="flex gap-3">
                            <button
                                onClick={() => alert("년도 선택")}
                                className="flex-1 bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                            >
                                <span>{form.birthYear || ""}</span>
                                <span className="text-[#A8C8D8] text-xs">▼</span>
                            </button>
                            <button
                                onClick={() => alert("월 선택")}
                                className="flex-1 bg-white rounded-xl px-4 py-3 flex items-center justify-between text-sm text-[#3D4D5C] shadow-sm"
                            >
                                <span>{form.birthMonth || ""}</span>
                                <span className="text-[#A8C8D8] text-xs">▼</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mt-8 flex gap-3">
                    <button
                        onClick={handleCancelEditProfile}
                        className="flex-1 py-4 rounded-2xl bg-[#4A5C6E] text-white font-bold text-sm"
                    >
                        취소
                    </button>
                    <button
                        onClick={handleSaveProfile}
                        className="flex-1 py-4 rounded-2xl bg-[#B4D0DB] text-white font-bold text-sm"
                    >
                        저장
                    </button>
                </div>
            </div>
        );
    }

    // ====== 렌더: 관리자 - 카테고리 설정/수정/삭제 ======
    if (isAdmin) {
        return (
            <>
                <header className="px-6 pt-6 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-[#3D4D5C]">관리자기능</h1>
                    <NotificationBell />
                </header>

                <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                    <div className="bg-white rounded-2xl p-6 shadow-sm flex flex-col items-center">
                        <p className="text-lg font-bold text-[#3D4D5C]">admin</p>
                        <div className="mt-3 w-20 h-20 rounded-full bg-[#A8C8D8]">
                            {/* 아이콘 위치: 프로필 이미지 (bi-person-fill) */}
                        </div>
                        <p className="mt-4 text-xs text-[#3D4D5C]">test@test.com</p>
                        <p className="mt-1 text-xs text-[#8B9BAA]">
                            서비스와 함께 한 지 <span className="font-semibold">40일째</span>
                        </p>
                        <button
                            onClick={handleEditAdmin}
                            className="mt-3 px-4 py-1.5 rounded-full bg-[#EEF2F5] text-xs font-semibold text-[#3D4D5C]"
                        >
                            관리자 수정
                        </button>
                    </div>

                    <div className="mt-6 flex items-center justify-between">
                        <h2 className="text-base font-bold text-[#3D4D5C]">
                            {adminMode === "edit"
                                ? "카테고리 수정"
                                : adminMode === "delete"
                                    ? "카테고리 삭제"
                                    : "카테고리 설정"}
                        </h2>
                        {adminMode === "default" && (
                            <button
                                onClick={handleEnterDeleteMode}
                                className="text-xs text-[#8B9BAA]"
                            >
                                삭제
                            </button>
                        )}
                        {adminMode === "delete" && (
                            <div className="flex items-center gap-3 text-xs">
                                <button
                                    onClick={handleCancelDeleteMode}
                                    className="text-[#8B9BAA]"
                                >
                                    취소
                                </button>
                                <button
                                    onClick={handleDeleteSelected}
                                    className="text-[#3D4D5C] font-semibold"
                                >
                                    선택한 카테고리 삭제
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="mt-3 bg-white rounded-2xl p-3 shadow-sm">
                        {categories.map((cat, idx) => {
                            const isEditing =
                                adminMode === "edit" && editingCategoryId === cat.id;
                            const isOtherEditing =
                                adminMode === "edit" && editingCategoryId !== cat.id;
                            const isSelected =
                                adminMode === "delete" && selectedCategoryIds.includes(cat.id);

                            let pillClass = "bg-[#E4EEF3] text-[#87B4C4]";
                            if (isEditing || isSelected) {
                                pillClass = "bg-[#4A5C6E] text-white";
                            }

                            return (
                                <div
                                    key={cat.id}
                                    draggable={adminMode === "default"}
                                    onDragStart={() => handleDragStart(idx)}
                                    onDragOver={handleDragOver}
                                    onDrop={() => handleDrop(idx)}
                                    onDragEnd={handleDragEnd}
                                    className={`
                    flex items-center py-2 px-1
                    ${adminMode === "default" ? "cursor-move" : ""}
                    ${draggedIdx === idx ? "opacity-50" : ""}
                  `}
                                >
                                    <div className="w-6 flex flex-col gap-0.5 shrink-0">
                                        {/* 아이콘 위치: 드래그 핸들 (bi-list) */}
                                        <span className="block w-4 h-0.5 bg-[#B5BEC7] rounded-full" />
                                        <span className="block w-4 h-0.5 bg-[#B5BEC7] rounded-full" />
                                        <span className="block w-4 h-0.5 bg-[#B5BEC7] rounded-full" />
                                    </div>

                                    {isEditing ? (
                                        <div className="flex-1">
                                            <div className="inline-flex items-center bg-[#4A5C6E] rounded-full px-4 py-1.5">
                                                <input
                                                    type="text"
                                                    autoFocus
                                                    value={editingValue}
                                                    onChange={(e) => setEditingValue(e.target.value)}
                                                    className="bg-transparent text-xs font-semibold text-white outline-none w-20"
                                                />
                                            </div>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => {
                                                if (adminMode === "delete") {
                                                    handleToggleCategorySelect(cat.id);
                                                } else if (!isOtherEditing) {
                                                    handleStartEdit(cat);
                                                }
                                            }}
                                            disabled={isOtherEditing}
                                            className="flex-1 text-left"
                                        >
                      <span
                          className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold ${pillClass}`}
                      >
                        {cat.name}
                      </span>
                                        </button>
                                    )}

                                    <div className="shrink-0 text-xs">
                                        {adminMode === "default" && (
                                            <button
                                                onClick={() => handleStartEdit(cat)}
                                                className="text-[#8B9BAA]"
                                            >
                                                수정
                                            </button>
                                        )}
                                        {isEditing && (
                                            <div className="flex items-center gap-3">
                                                <button
                                                    onClick={handleCancelEdit}
                                                    className="text-[#8B9BAA]"
                                                >
                                                    취소
                                                </button>
                                                <button
                                                    onClick={handleConfirmEdit}
                                                    className="text-[#3D4D5C] font-semibold"
                                                >
                                                    확인
                                                </button>
                                            </div>
                                        )}
                                        {adminMode === "edit" && !isEditing && (
                                            <span className="text-[#B5BEC7]">수정</span>
                                        )}
                                        {adminMode === "delete" && <span className="block w-0" />}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </>
        );
    }

    // ====== 렌더: 비관리자 - 마이페이지 메인 ======
    return (
        <>
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">마이페이지</h1>
                <NotificationBell />
            </header>

            <div className="flex-1 overflow-y-auto px-6 pt-4 pb-4">
                <div className="bg-white rounded-2xl p-6 shadow-sm relative">
                    <button
                        onClick={handleWithdraw}
                        className="absolute top-4 right-5 text-[11px] text-[#8B9BAA]"
                    >
                        회원탈퇴
                    </button>

                    <div className="flex flex-col items-center">
                        <p className="text-lg font-bold text-[#3D4D5C]">{user?.username || ""}</p>
                        <div className="mt-3 w-20 h-20 rounded-full bg-[#A8C8D8]">
                            {/* 아이콘 위치: 프로필 이미지 (bi-person-fill) */}
                        </div>
                        <p className="mt-4 text-xs text-[#3D4D5C]">{user?.email || ""}</p>
                        <p className="mt-1 text-xs text-[#8B9BAA]">
                            함께한 지 <span className="font-semibold">40일째</span>
                        </p>
                        <button
                            onClick={handleEditProfile}
                            className="mt-3 px-4 py-1.5 rounded-full bg-[#EEF2F5] text-xs font-semibold text-[#3D4D5C]"
                        >
                            내 정보 수정
                        </button>
                    </div>
                </div>

                <h2 className="mt-6 text-base font-bold text-[#3D4D5C]">모드 변경</h2>

                <button
                    onClick={() => handleSelectStrictMode("strict")}
                    className={`
            mt-3 w-full bg-white rounded-2xl p-5 shadow-sm block text-left
            ${strictMode === "strict" ? "ring-2 ring-[#A8C8D8]" : ""}
          `}
                >
                    <p className="text-center text-sm font-bold text-[#3D4D5C]">
                        엄격하게
                    </p>
                    <div className="mt-3 h-14 bg-[#E4E9EE] rounded-xl" />
                </button>

                <button
                    onClick={() => handleSelectStrictMode("less")}
                    className={`
            mt-3 w-full bg-white rounded-2xl p-5 shadow-sm block text-left
            ${strictMode === "less" ? "ring-2 ring-[#A8C8D8]" : ""}
          `}
                >
                    <p className="text-center text-sm text-[#8B9BAA]">덜 엄격하게</p>
                    <div className="mt-3 h-14 bg-[#E4E9EE] rounded-xl" />
                </button>
            </div>
        </>
    );
}

/* ============ 서브 컴포넌트 ============ */
function Field({ label, type = "text", value, onChange, placeholder, readOnly }) {
    return (
        <div>
            <label className="block text-xs text-[#8B9BAA] mb-2">{label}</label>
            <input
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                readOnly={readOnly}
                className="w-full px-4 py-3 rounded-xl bg-white text-sm text-[#3D4D5C] placeholder-[#B5BEC7] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#A8C8D8]"
            />
        </div>
    );
}
