import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useBoard } from "../../hooks/useBoard";
import Swal from "sweetalert2";
import FormField from "../Layout/FormField";
import SubmitButton from "../Layout/SubmitButton";

const CreateBoard = () => {
    const { addBoard } = useBoard();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        title: "",
        category: "",
        description: "",
    });

    const onChange = useCallback((e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    }, []);

    const onSubmit = useCallback(
        async (e) => {
            e.preventDefault();
            if (!formData.title.trim()) {
                Swal.fire({
                    icon: "warning",
                    title: "입력 오류",
                    text: "제목을 입력해주세요.",
                    confirmButtonColor: "#0f172a", // 버튼 색상도 블랙으로 통일
                });
                return;
            }
            if (!formData.category.trim()) {
                Swal.fire({
                    icon: "warning",
                    title: "입력 오류",
                    text: "카테고리를 입력해주세요.",
                    confirmButtonColor: "#0f172a",
                });
                return;
            }

            try {
                const result = await addBoard(formData);
                if (result) {
                    navigate("/", { replace: true });
                }
            } catch (error) {
                console.error("Error creating Board:", error);
            }
        },
        [formData, addBoard, navigate],
    );

    return (
        <div className="min-h-screen bg-slate-50 flex items-start justify-center px-4 py-16">
            <div className="max-w-2xl w-full bg-white border border-slate-200 rounded-xl overflow-hidden">
                <div className="px-8 py-6 border-b border-slate-100">
                    <h2 className="text-xl font-black text-slate-900 tracking-tight">
                        새 글 생성
                    </h2>
                    <p className="text-sm text-slate-500 mt-1">새 글 작성하십시오.</p>
                </div>

                {/* 분석 품질 안내 배너 */}
                <div className="mx-8 mt-6 flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3">
                    <span className="mt-0.5 text-amber-500 text-base leading-none">💡</span>
                    <p className="text-sm text-amber-800 leading-snug">
                        <span className="font-semibold">정밀한 AI 분석을 위해</span> TODO를 구체적으로 작성해 주세요.{" "}
                        <span className="text-amber-600">예) "운동하기" → "저녁 7시 30분 러닝머신"</span>
                    </p>
                </div>

                {/* 폼 부분 */}
                <form onSubmit={onSubmit} className="p-8 space-y-8">
                    <div className="space-y-6">
                        <FormField
                            label="제목"
                            name="title"
                            value={formData.title}
                            onChange={onChange}
                            placeholder="제목을 입력하세요"
                        />

                        <FormField
                            label="설명"
                            name="description"
                            type="textarea"
                            value={formData.description}
                            onChange={onChange}
                            placeholder="상세 내용을 입력하세요"
                        />
                        <FormField
                            label="카테고리"
                            name="category"
                            value={formData.category}
                            onChange={onChange}
                            placeholder="카테고리를 입력하세요"
                        />
                    </div>


                    <div className="pt-4 border-t border-slate-50 flex justify-end">
                        <SubmitButton label="새 글 생성하기" />
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateBoard;
