// src/service/bookService.js
import { apiGet, apiPost } from "./request";

export const fetchBookDetail = async (isbn) => {
    console.log("📚 [fetchBookDetail] 요청 시작:", isbn); // 요청 전 로그

    try {
        const response = await apiGet(`/books/book/${isbn}`);
        console.log("✅ [fetchBookDetail] 응답 데이터:", response); // 응답 성공 로그
        
        // 새로운 API 응답 형식 처리
        if (response.success && response.data) {
            return response.data;
        } else {
            throw new Error(response.error || "도서 정보를 찾을 수 없습니다.");
        }
    } catch (error) {
        console.error("❌ [fetchBookDetail] 오류 발생:", error); // 에러 로그
        throw error;
    }
};

export const getBookStoresByIsbn = async (isbn) => {
    const res = await apiPost("/bookstores", { isbn });
    return res.itemOffStoreList;
};

export const fetchAllBooks = async (page = 0) => {
    const response = await apiGet(`/books?page=${page}&size=20`);
    
    // 새로운 API 응답 형식 처리
    if (response.success && response.data) {
        return response.data;
    } else {
        throw new Error(response.error || "도서 목록을 불러올 수 없습니다.");
    }
};

export const fetchBooksByCategory = async (category, page = 0) => {
    const response = await apiGet(`/books/category/${encodeURIComponent(category)}?page=${page}&size=20`);
    
    // 새로운 API 응답 형식 처리
    if (response.success && response.data) {
        return response.data; // PaginationService가 반환하는 구조: { content, currentPage, totalPages, totalElements, numberOfElements }
    } else {
        throw new Error(response.error || "카테고리별 도서를 불러올 수 없습니다.");
    }
};

export const searchBooks = async (searchTerm, page = 0) => {
    const response = await apiGet(`/books/search?search=${encodeURIComponent(searchTerm)}&page=${page}&size=20`);
    
    // 새로운 API 응답 형식 처리
    if (response.success && response.data) {
        return response.data; // PaginationService가 반환하는 구조: { content, currentPage, totalPages, totalElements, numberOfElements }
    } else {
        throw new Error(response.error || "검색 결과를 불러올 수 없습니다.");
    }
};