// src/service/bookService.js
import { apiGet } from "./request";

export const fetchBookDetail = async (isbn) => {
    console.log("📚 [fetchBookDetail] 요청 시작:", isbn); // 요청 전 로그

    try {
        const data = await apiGet(`/books/book/${isbn}`);
        console.log("✅ [fetchBookDetail] 응답 데이터:", data); // 응답 성공 로그
        return data;
    } catch (error) {
        console.error("❌ [fetchBookDetail] 오류 발생:", error); // 에러 로그
        throw error;
    }
};

