// import React, { useCallback, useState } from "react";
// import {
//     ModalLayout,
//     FormButton,
//     FormInput,
//     ErrorMessage,
//     AuthLink,
// } from "../FormUi";
// import { useAuth } from "@/hooks/useAuth.jsx";
//
// const SignupModal = ({ isOpen, onClose, onLoginClick }) => {
//
//     // 사용자 입력값 받는 input 모음
//     const [formData, setFormData] = useState({
//         email: "",
//         username: "",
//         password: "",
//         confirmPassword: "",
//     });
//
//     // useAuth로부터 상태 공유받기
//     const { error, signup, setError } = useAuth();
//
//     const handleChange = useCallback((e) => {
//         setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
//     }, []);
//
//     const handleSubmit = useCallback(
//         async (e) => {
//             e.preventDefault();
//
//             setError("");
//
//             const { email, username, password, confirmPassword } = formData;
//
//             if (username.length < 2) {
//                 setError("닉네임은 최소 2글자 이상이어야한다");
//                 return;
//             }
//             if (password.length < 6) {
//                 setError("비번은 최소 6글자 이상이어야한다");
//                 return;
//             }
//
//             if (password !== confirmPassword) {
//                 setError("비밀번호가 일치하지 않는다");
//                 return;
//             }
//
//             try {
//                 const success = await signup(formData);
//                 if (success) {
//                     setFormData({
//                         email: "",
//                         username: "",
//                         password: "",
//                         confirmPassword: "",
//                     });
//                     onLoginClick();
//                 }
//             } catch (err) {
//                 console.error("Signup error:", err);
//             }
//         },
//         [formData, signup, setError, onLoginClick],
//     );
//
//     return (
//         <ModalLayout isOpen={isOpen} onClose={onClose} title="회원가입">
//             <form className="space-y-4" onSubmit={handleSubmit}>
//                 <FormInput
//                     type="email"
//                     name="email"
//                     value={formData.email}
//                     onChange={handleChange}
//                     placeholder="이메일"
//                 />
//                 <FormInput
//                     type="text"
//                     name="username"
//                     value={formData.username}
//                     onChange={handleChange}
//                     placeholder="닉네임"
//                 />
//                 <FormInput
//                     type="password"
//                     name="password"
//                     value={formData.password}
//                     onChange={handleChange}
//                     placeholder="비밀번호"
//                 />
//                 <FormInput
//                     type="password"
//                     name="confirmPassword"
//                     value={formData.confirmPassword}
//                     onChange={handleChange}
//                     placeholder="비밀번호 확인"
//                 />
//
//                 <ErrorMessage error={error} />
//
//                 <FormButton>가입하기</FormButton>
//             </form>
//
//             <AuthLink
//                 message="이미 계정이 있으신가요?"
//                 buttonText="로그인"
//                 onClick={onLoginClick}
//             />
//         </ModalLayout>
//     );
// };
//
// export default SignupModal;