import React, {useState, useEffect} from "react";
import {showWarningDialog, showSuccessAlert, showWarningAlert} from "@/utils/alertUtils.js";
import { useAuth } from "../../hooks/useAuth";
import NotificationBell from "../../Components/Notification";
import useMypage  from "../../hooks/useMypage";
import ErrorMessage from "../../Components/Modal/FormUi/ErrorMessage";
import api from "@/utils/api.js";
import { useCloth } from "@/hooks/useCloth";
import ClothChangeModal from "@/Components/Modal/ClothChangeModal";

import useCategory from "@/hooks/useCategory.jsx";

export default function MyPage() {
    const { user, setUser, logout, deleteUser } = useAuth();
    const { updateProfile, updatePassword, checkUsername, updateStatusMessage, error: mypageError, setError: setMypageError } = useMypage();
    const { currentCloth, getUserCloth, setUserCloth } = useCloth();
    const { getCategory, addCategory, updateCategory, deleteCategory } = useCategory();

    const [isAdmin, setIsAdmin] = useState(false);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newCategoryName, setNewCategoryName] = useState("");
    const [strictMode, setStrictMode] = useState("strict"); // "strict" | "less"
    const [view, setView] = useState("main"); // "main" | "edit-profile"
    const [error, setError] = useState("");
    const [form, setForm] = useState({ 
        username: "", 
        email: "", 
        currentPassword: "",  
        password: "", 
        confirmPassword: "", 
        birthYear: "",
        birthMonth: "",
        birthDay: ""  
        });

    const [adminCategoryMode, setAdminCategoryMode] = useState("default"); // "default" | "edit" | "delete"
    const [editingCategoryId, setEditingCategoryId] = useState(null);
    const [editingValue, setEditingValue] = useState("");
    const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);

    const [categories, setCategories] = useState([]);
    const [draggedIdx, setDraggedIdx] = useState(null);
    const [editingStatusMessage, setEditingStatusMessage] = useState(null);
    const [statusMessage, setStatusMessage] = useState("");

    const [isClothModalOpen, setIsClothModalOpen] = useState(false);
    const [pendingCloth, setPendingCloth] = useState(null);

    // mount시 사용자가 선택한 프로필 이미지 불러오기
    useEffect(() => { getUserCloth(); }, []);

    // mount시, 카테고리 수정 시 카테고리 목록 불러오기
    useEffect(() => {
        loadCategory();
    }, []);

    // useEffect(() => {
    //     const checkAdmin = () => false;
    //     setIsAdmin(checkAdmin());
    //     const loadStrictMode = () => "strict";
    //     setStrictMode(loadStrictMode());
    // }, []);
    useEffect(() => {
        setIsAdmin(user?.role === "admin");
    }, [user]);

    useEffect(() => {
        // TODO: API 로 strictMode 변경 저장
    }, [strictMode]);

    useEffect(() => {
        if (user) {
            const [year, month, day] = (user.birthday || "").split("-");
            setForm(prev => ({
                ...prev,
                username: user.username || "",
                email: user.email || "",
                birthYear: year || "",
                birthMonth: month || "",
                birthDay: day || "",
            }));
        }
    }, [user]);

    useEffect(() => {
    if (user?.status_message) {
        setStatusMessage(user.status_message);
    }
    }, [user]);

    // 에러 메시지 띄운 후, 한 글자라도 수정하면 에러 메시지 즉시 내리기
    useEffect(() => {
        if (error || mypageError) {
            setError("");
            setMypageError("");
        }
    }, [form.username, form.currentPassword, form.password, form.confirmPassword]);

    // 카테고리 로드
    const loadCategory = async () => {
        const db_category = await getCategory();
        console.log("카테고리 데이터:", JSON.stringify(db_category)); 
        if (db_category) setCategories(db_category);
    };

    // 회원 가입 날짜 계산
    const getJoinDate = () => {
        if (!user) return 0;
        const createdAt = user.created_at;
        // 1. 현재 시간과 가입 시간의 차이 계산 (밀리초 단위)
        const now = new Date();
        const joinedDate = new Date(createdAt);
        // 2. 시간, 분, 초를 모두 0으로 초기화 (날짜만 남기기)
        const startOfNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const startOfJoined = new Date(joinedDate.getFullYear(), joinedDate.getMonth(), joinedDate.getDate());
        // 3. 날짜 차이 계산
        const diffInMs = startOfNow - startOfJoined;
        const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24)) + 1;

        return diffInDays;
    }

    const handleEditProfile = () => {
        setForm(prev => ({
            ...prev,
            currentPassword: "",
            password: "",
            confirmPassword: "",
        }));
        setPendingCloth(currentCloth);
        setView("edit-profile");
    };
    const handleCancelEditProfile = () => {
        setPendingCloth(null);
        setError("")
        setView("main");
    };

    const handleChangeProfileImage = () => setIsClothModalOpen(true);

    const handleApplyCloth = (cloth) => {
        setPendingCloth(cloth);
    };

    const handleSelectStrictMode = (mode) => {
        setStrictMode(mode);
        alert(`모드 변경: ${mode === "strict" ? "엄격하게" : "덜 엄격하게"}`);
    };

    const handleEnterDeleteMode = () => {
        setAdminCategoryMode("delete");
        setEditingCategoryId(null);
    };
    const handleCancelDeleteMode = () => {
        setAdminCategoryMode("default");
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
            // 개별 삭제 순차 실행
            const results = await Promise.all(
                selectedCategoryIds.map((id) => deleteCategory(id))
            );
            if (results.every(Boolean)) {
                setCategories((prev) =>
                    prev.filter((c) => !selectedCategoryIds.includes(c.category_id))
                );
                setSelectedCategoryIds([]);
                setAdminCategoryMode("default");
                showSuccessAlert({ title: "삭제 완료" });
            }
        }
    };

    const handleStartEdit = (category) => {
        console.log("handleStartEdit called:", category.id);
        // setAdminCategoryMode("edit");
        setEditingCategoryId(category.category_id);
        setEditingValue(category.name);
    };
    const handleCancelEdit = () => {
        // setAdminCategoryMode("default");
        setEditingCategoryId(null);
        setEditingValue("");
    };
    const handleConfirmEdit = async () => {
        if (!editingValue.trim()) {
            setError("카테고리 이름을 입력하세요.");
            return;
        }
        const ok = await updateCategory(editingCategoryId, editingValue.trim());
        if (ok) {
            setCategories((prev) =>
                prev.map((c) => c.category_id === editingCategoryId ? { ...c, name: editingValue.trim() } : c)
            );
            setEditingCategoryId(null);
            setEditingValue("");
            showSuccessAlert({ title: "카테고리 수정 완료" });
        }
    };

    const handleAddCategory = async () => {
        if (!newCategoryName.trim()) return;
        const newCat = await addCategory(newCategoryName.trim());
        if (newCat) {
            setCategories((prev) => [...prev, newCat]);
            setIsAddModalOpen(false);
            setNewCategoryName("");
            showSuccessAlert({ title: "카테고리가 추가되었습니다." });
        }
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

    const handleSaveProfile = async () => {
        setError("");
        // 변경 성공 메시지 한 번에 띄우기 위한 리스트
        const message = [];
        const isChangingUsername = form.username.trim() !== user?.username;
        const isChangingPassword = form.currentPassword || form.password || form.confirmPassword;
        const isChangingCloth = pendingCloth?.cloth_id !== currentCloth?.cloth_id;

        if (!isChangingUsername && !isChangingPassword && !isChangingCloth) {
            setError("변경된 내용이 없습니다.");
            return;
        }

        if (isChangingUsername) {
            if (!form.username.trim()) {
                setError("닉네임을 입력해주세요.");
                return;
            }
            const isAvailable = await checkUsername(form.username.trim());
            if (!isAvailable) return;
        }

        if (isChangingPassword) {
            if (!form.currentPassword) {
                setError("현재 비밀번호를 입력해주세요.");
                return;
            }
            if (!form.password) {
                setError("새 비밀번호를 입력해주세요.");
                return;
            }
            const pwRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
            if (!pwRegex.test(form.password)) {
                setError("새 비밀번호는 8자 이상, 영문·숫자·특수문자를 포함해야 합니다.");
                return;
            }
            
        }

        try {
            if (isChangingUsername) {
                const profileOk = await updateProfile({ username: form.username.trim() });
                if (!profileOk) return;
                message.push("닉네임");
            }

            if (isChangingPassword) {
                const pwOk = await updatePassword({
                    currentPassword: form.currentPassword,
                    newPassword: form.password,
                    confirmPassword: form.confirmPassword,
                });
                if (!pwOk) return;
                
                if (form.password !== form.confirmPassword) {
                    setError("새 비밀번호가 일치하지 않습니다.");
                    return;
                }
                message.push("비밀번호");
            }

            if (isChangingCloth) {
                await setUserCloth(pendingCloth);
                message.push("프로필 사진");
            }

            // 성공 메시지 한 번에 출력
            if (message.length > 0) {
                await showSuccessAlert({title: `${message.join(", ")}이(가) 변경되었습니다.`});
            }

            setForm(prev => ({
                    ...prev,
                    currentPassword: "",
                    password: "",
                    confirmPassword: "",
            }));
            setPendingCloth(null);
            setView("main");
        } catch (err) {
            setError("저장 중 오류가 발생했습니다.");
        }
    };

    const handleStatusMessage = async () => {
        if (editingStatusMessage) {
            if (statusMessage.length > 30) {
                showWarningAlert({title: "30자 이내로 입력하세요."})
                return;
            }

            try {
                const success = await updateStatusMessage(statusMessage);

                if (success) {
                    showSuccessAlert({ title: "상태메세지가 저장되었습니다."});
                } else {
                    showWarningDialog({
                        title: "저장 실패",
                        text: mypageError || "다시 시도해주세요."
                    });
                }
            } catch (err) {
                console.error("상태메시지 저장 중 에러 발생:", error);
                showWarningDialog({
                    title: "시스템 오류",
                    text: "서버와 통신하는 중 문제가 발생했습니다."
                });
            }
            setEditingStatusMessage(null)
        }
        else {
            setEditingStatusMessage(true)
        }

    };

    // ====== 렌더: 비관리자/관리자 - 내 정보 수정 ======
    if (view === "edit-profile") {
        return (
            <div className="flex-1 overflow-y-auto px-8 pt-10 pb-10 flex flex-col">
                <h1 className="text-xl font-bold text-[#3D4D5C]">내 정보 수정</h1>

                <div className="mt-6 flex flex-col items-center">
                    <div className={`w-24 h-24 rounded-full overflow-hidden ${!pendingCloth ? 'bg-[#A8C8D8]' : ''}`}>
                        {pendingCloth && (
                            <img src={pendingCloth.file_url}
                                 alt={pendingCloth.title} className="w-full h-full object-cover"
                            />
                        )}
                    </div>
                    <button
                        onClick={handleChangeProfileImage}
                        className="mt-2 text-xs text-[#8B9BAA]"
                    >
                        프로필 사진 변경
                    </button>
                </div>

                <div className="mt-6 flex flex-col gap-4">

                    <ErrorMessage error={error || mypageError} />

                    <Field label="닉네임" value={form.username} onChange={(e) => setForm({...form, username: e.target.value})} />
                    <Field label="이메일" value={form.email} readOnly />
                    <Field label="현재 비밀번호" type="password" value={form.currentPassword} onChange={(e) => setForm({...form, currentPassword: e.target.value})} placeholder={"••••••••"}/>
                    <Field label="새 비밀번호" type="password" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} placeholder={"••••••••"}/>
                    <Field label="새 비밀번호 확인"
                        type="password"
                        value={form.confirmPassword} onChange={(e) => setForm({...form, confirmPassword: e.target.value})}
                        placeholder={"••••••••"}
                    />

                    <div>
                        <label className="block text-xs text-[#8B9BAA] mb-2">생일</label>
                        <div className="flex gap-3">
                           <div className="flex-1 bg-[#F2F4F6] rounded-xl px-4 py-3 flex items-center text-sm text-[#B5BEC7] shadow-sm cursor-not-allowed">
                                <span>{form.birthYear || ""}</span>
                                <span className="text-[#A8C8D8] text-xs">▼</span>
                            </div>
                            <div className="flex-1 bg-[#F2F4F6] rounded-xl px-4 py-3 flex items-center text-sm text-[#B5BEC7] shadow-sm cursor-not-allowed">
                                <span>{form.birthMonth || ""}</span>
                                <span className="text-[#A8C8D8] text-xs">▼</span>
                            </div>
                             <div className="flex-1 bg-[#F2F4F6] rounded-xl px-4 py-3 flex items-center text-sm text-[#B5BEC7] shadow-sm cursor-not-allowed">
                                <span>{form.birthDay || ""}</span>
                                <span className="text-[#A8C8D8] text-xs">▼</span>
                            </div>
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
                {/* 프로필 변경 모달 추가 */}
                <ClothChangeModal
                    isOpen={isClothModalOpen}
                    onClose={() => setIsClothModalOpen(false)}
                    currentClothId={pendingCloth?.cloth_id}
                    onApply={handleApplyCloth}
                />
            </div>
        );
    }

    // ====== 렌더: 비관리자/관리자 - 마이페이지 메인 ======
    return (
        <div className="flex-1 min-h-0 flex flex-col">
            <header className="px-6 pt-6 flex items-center justify-between">
                <h1 className="text-2xl font-bold text-[#3D4D5C]">마이페이지</h1>
                    <NotificationBell />
            </header>

            <div className="flex-1 min-h-0 overflow-y-auto px-6 pb-8 flex flex-col gap-5">
                {/* 프로필 카드 */}
                <div className="bg-white rounded-2xl p-5 shadow-sm relative shrink-0">
                    <button onClick={logout} className="absolute top-4 right-5 text-[10px] text-[#8B9BAA] cursor-pointer">
                        로그아웃
                    </button>
                    <div className="flex flex-col items-center">
                        <p className="text-base font-bold text-[#3D4D5C]">{user?.username}</p>
                        <div className={`mt-3 w-20 h-20 rounded-full overflow-hidden ${!currentCloth ? 'bg-[#A8C8D8]' : ''}`}>
                            {currentCloth && (
                                <img
                                    src={currentCloth.file_url}
                                    alt={currentCloth.title}
                                    className="w-full h-full object-cover"
                                />
                            )}
                        </div>
                        <p className="mt-4 text-xs text-[#3D4D5C]">{user?.email || ""}</p>
                        <p className="mt-1 text-xs text-[#8B9BAA]">
                            함께한 지 <span className="font-semibold">{getJoinDate()}</span>일째
                        </p>
                        <button
                            onClick={handleEditProfile}
                            className="mt-4 w-full max-w-35 py-2.5 rounded-xl bg-[#EEF2F5] text-[12px] font-bold text-[#3D4D5C] active:bg-[#E2E8ED] transition-colors cursor-pointer"
                        >
                            내 정보 수정
                        </button>
                    </div>
                </div>

                {/* 상태메세지 */}
                <div className="shrink-0">
                    <div className="flex justify-between items-end mb-3 px-1">
                        <h2 className="text-[13px] font-bold text-[#3D4D5C]">상태메세지</h2>
                        <span className="text-[10px] text-[#8B9BAA]">{statusMessage?.length || 0}/30</span>
                    </div>
                    <div className="bg-white rounded-xl p-3 shadow-sm flex gap-2 items-center border border-transparent focus-within:border-[#A8C8D8]">
                        {editingStatusMessage ? (
                            <>
                                <input
                                    type="text"
                                    value={statusMessage}
                                    onChange={(e) => {
                                        if (e.target.value.length <= 30) {
                                            setStatusMessage(e.target.value);
                                        }
                                    }}
                                    maxLength={30}
                                    placeholder="상태메시지를 입력하세요."
                                    className="flex-1 px-3 py-2 bg-[#F1F3F5] rounded-lg text-xs text-[#3D4D5C] outline-none placeholder:text-[#ADB5BD]"
                                />
                            </>
                        ) : (
                            <>
                                <span className="flex-1 px-3 py-2 rounded-lg text-xs text-[#3D4D5C]">
                                    {statusMessage}
                                </span>
                            </>
                        )}
                        <button
                            onClick={handleStatusMessage}
                            className="px-4 py-2 rounded-lg bg-[#A8C8D8] text-white text-[12px] font-bold shrink-0 cursor-pointer"
                        >
                            {editingStatusMessage ? "저장" : "수정"}
                        </button>
                    </div>
                </div>

                {/* 모드 변경 - 관리자에게는 표시하지 않음 */}
                {!isAdmin && (
                    <div className="flex flex-col">
                        <h2 className="text-base font-bold text-[#3D4D5C] mb-3 px-1">모드 변경</h2>
                        <div className="flex-1 flex flex-col gap-4 mb-4">
                            {/* 엄격하게 버튼 */}
                            <button
                                onClick={() => handleSelectStrictMode("strict")}
                                className={`w-full bg-white rounded-2xl p-5 shadow-sm block text-left cursor-pointer
                                ${strictMode === "strict" ? "ring-2 ring-[#A8C8D8]" : ""}
                                `}
                            >
                                <p className="text-center text-sm font-bold text-[#3D4D5C]">엄격하게</p>
                                <div className="mt-3 h-14 bg-[#E4E9EE] rounded-xl" />
                            </button>

                            <button
                                onClick={() => handleSelectStrictMode("less")}
                                className={`w-full bg-white rounded-2xl p-5 shadow-sm block text-left cursor-pointer
                                ${strictMode === "less" ? "ring-2 ring-[#A8C8D8]" : ""}
                                `}
                            >
                                <p className="text-center text-sm text-[#8B9BAA]">덜 엄격하게</p>
                                <div className="mt-3 h-14 bg-[#E4E9EE] rounded-xl" />
                            </button>
                        </div>
                    </div>
                )}

                {/* 카테고리 관리 - 관리자만 표시 */}
{isAdmin && (
    <div className="shrink-0">
        <div className="flex items-center justify-between mb-3 px-1">
            <h2 className="text-base font-bold text-[#3D4D5C]">
                {adminCategoryMode === "delete" ? "카테고리 삭제" : "카테고리 설정"}
            </h2>
            {adminCategoryMode === "default" && (
                <div className="flex items-center gap-3 text-xs">
                    <button
                        onClick={() => { setIsAddModalOpen(true); setNewCategoryName(""); }}
                        className="text-[#8B9BAA] cursor-pointer"
                    >
                        추가
                    </button>
                    <button
                        onClick={handleEnterDeleteMode}
                        className="text-[#8B9BAA] cursor-pointer"
                    >
                        삭제
                    </button>
                </div>
            )}
            {adminCategoryMode === "delete" && (
                <div className="flex items-center gap-3 text-xs">
                    <button onClick={handleCancelDeleteMode} className="text-[#8B9BAA] cursor-pointer">취소</button>
                    <button onClick={handleDeleteSelected} className="text-[#3D4D5C] font-semibold cursor-pointer">선택한 카테고리 삭제</button>
                </div>
            )}
        </div>

        <div className="bg-white rounded-2xl p-3 shadow-sm">
            {categories.length === 0 ? (
                <p className="text-xs text-[#8B9BAA] text-center py-4">카테고리가 없습니다.</p>
            ) : (
                categories.map((cat, idx) => {
                    const isEditing = editingCategoryId === cat.category_id;
                    const isSelected = adminCategoryMode === "delete" && selectedCategoryIds.includes(cat.category_id);

                    let pillClass = "bg-[#E4EEF3] text-[#87B4C4]";
                    if (isEditing || isSelected) pillClass = "bg-[#4A5C6E] text-white";

                    return (
                        <div
                            key={cat.category_id}
                            draggable={adminCategoryMode === "default" && !isEditing}
                            onDragStart={() => handleDragStart(idx)}
                            onDragOver={handleDragOver}
                            onDrop={() => handleDrop(idx)}
                            onDragEnd={handleDragEnd}
                            className={`flex items-center py-2 px-1
                                ${adminCategoryMode === "default" && !isEditing ? "cursor-move" : ""}
                                ${draggedIdx === idx ? "opacity-50" : ""}
                            `}
                        >
                            <div className="w-6 flex flex-col gap-0.5 shrink-0">
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
                                        if (adminCategoryMode === "delete") handleToggleCategorySelect(cat.category_id);
                                    }}
                                    className="flex-1 text-left"
                                >
                                    <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold ${pillClass}`}>
                                        {cat.name}
                                    </span>
                                </button>
                            )}

                            <div className="shrink-0 text-xs">
                                {isEditing ? (
                                    <div className="flex items-center gap-3">
                                        <button onClick={handleCancelEdit} className="text-[#8B9BAA] cursor-pointer">취소</button>
                                        <button onClick={handleConfirmEdit} className="text-[#3D4D5C] font-semibold cursor-pointer">확인</button>
                                    </div>
                                ) : adminCategoryMode === "default" ? (
                                    <button
                                        onClick={() => handleStartEdit(cat)}
                                        className="text-[#8B9BAA] cursor-pointer"
                                    >
                                        수정
                                    </button>
                                ) : null}
                            </div>
                        </div>
                    );
                })
            )}
        </div>
        {/* ✅ 추가 모달 */}
        {isAddModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
                <div className="bg-white rounded-2xl p-6 w-72 shadow-xl">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-[#3D4D5C]">카테고리 생성</h3>
                        <button onClick={() => setIsAddModalOpen(false)} className="text-[#8B9BAA] text-lg leading-none cursor-pointer">✕</button>
                    </div>
                    <p className="text-xs text-[#8B9BAA] mb-2">어떤 카테고리를 생성할까요?</p>
                    <input
                        type="text"
                        autoFocus
                        value={newCategoryName}
                        onChange={(e) => setNewCategoryName(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") handleAddCategory(); }}
                        placeholder="예) 복습, 운동"
                        className="w-full px-4 py-3 rounded-xl bg-[#F2F4F6] text-sm text-[#3D4D5C] outline-none placeholder-[#B5BEC7] focus:ring-2 focus:ring-[#A8C8D8] mb-5"
                    />
                    <div className="flex gap-3">
                        <button
                            onClick={() => setIsAddModalOpen(false)}
                            className="flex-1 py-3 rounded-xl bg-[#EEF2F5] text-sm font-bold text-[#3D4D5C] cursor-pointer"
                        >
                            취소
                        </button>
                        <button
                            onClick={handleAddCategory}
                            className="flex-1 py-3 rounded-xl bg-[#E57373] text-sm font-bold text-white cursor-pointer"
                        >
                            추가 
                        </button>
                    </div>
                </div>
            </div>
        )}
    </div>
)}

                {/* 탈퇴 버튼 - 관리자에게는 표시하지 않음 */}
                {!isAdmin && (
                    <div className="flex justify-center shrink-0">
                        <button onClick={deleteUser} className="text-[10px] text-[#8B9BAA] border-b border-[#8B9BAA] pb-0.5 cursor-pointer">
                            회원 탈퇴
                        </button>
                    </div>
                )}
            </div>
        </div>
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
                className={`w-full px-4 py-3 rounded-xl text-sm shadow-sm focus:outline-none cursor-text
                        ${readOnly
                            ? "bg-[#F2F4F6] text-[#B5BEC7] cursor-not-allowed"
                            : "bg-white text-[#3D4D5C] placeholder-[#B5BEC7] focus:ring-2 focus:ring-[#A8C8D8]"
                        }`}/>
        </div>
    );
}