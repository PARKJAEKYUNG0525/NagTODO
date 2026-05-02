// import React, { useCallback, useState } from "react";
// import {
//     ModalLayout,
//     ErrorMessage,
//     FormButton,
//     FormInput,
//     AuthLink,
// } from "../FormUi";
// import { useAuth } from "@/hooks/useAuth.jsx";
//
// const LoginModal = ({ isOpen, onClose, onSignupClick }) => {
//     const [formData, setFormData] = useState({ email: "", password: "" });
//     const { error, setError, login, isLoading } = useAuth(); // isLoading 추가
//
//     const handleChange = useCallback(
//         (e) => {
//             setError("");
//             setFormData((prev) => ({
//                 ...prev,
//                 [e.target.name]: e.target.value,
//             }));
//         },
//         [setError],
//     );
//
//     const handleSubmit = useCallback(
//         async (e) => {
//             e.preventDefault();
//             setError("");
//
//             try {
//                 const success = await login(formData.email, formData.password);
//                 if (success) {
//                     onClose();
//                     setFormData({ email: "", password: "" });
//                 }
//             } catch (err) {
//                 console.error("Login error:", err);
//             }
//         },
//         [formData, login, onClose, setError],
//     );
//
//     return (
//         <ModalLayout isOpen={isOpen} onClose={onClose} title="로그인">
//             <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
//                 {/* space-y-3으로 간격을 살짝 좁혀 더 촘촘하고 세련되게 조정 */}
//                 <div className="space-y-3 mb-2">
//                     <FormInput
//                         type="email"
//                         name="email"
//                         value={formData.email}
//                         onChange={handleChange}
//                         placeholder="이메일 주소"
//                     />
//
//                     <FormInput
//                         type="password"
//                         name="password"
//                         value={formData.password}
//                         onChange={handleChange}
//                         placeholder="비밀번호"
//                     />
//                 </div>
//
//                 {error && <ErrorMessage error={error} />}
//
//                 <FormButton disabled={isLoading}>
//                     {isLoading ? "로그인 중..." : "로그인"}
//                 </FormButton>
//             </form>
//
//             <AuthLink
//                 message="계정이 없으신가요?"
//                 buttonText="회원가입"
//                 onClick={onSignupClick}
//             />
//         </ModalLayout>
//     );
// };
//
// export default LoginModal;