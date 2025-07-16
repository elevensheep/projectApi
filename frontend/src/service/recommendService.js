import axios from "axios";

// FastAPI 전용 axios 인스턴스
const fastApi = axios.create({
    baseURL: "http://localhost:8000", // ✅ FastAPI 포트
    withCredentials: false,
});

// ✅ 추천 도서 전체 조회 (페이징, 날짜 포함)
export const fetchRecommendedBooks = ({
    newsCategory = "",
    newsDate = "",
    page = 1,
    limit = 15,
} = {}) => {
    const params = new URLSearchParams();
    if (newsCategory) params.append("news_category", newsDate);
    if (newsDate) params.append("news_date", newsDate);
    params.append("page", page);
    params.append("limit", limit);

    return fastApi
        .get(`/api/recommend/${newsCategory}?${params.toString()}`)
        .then((res) => {
            console.log("✅ 추천 도서 조회 성공:", res.data);
            return res.data;
        });
};

// ✅ 카테고리별 도서 조회 (기본 news_date 포함)
export const fetchBooksByCategory = async (category, limit = 5, date = null) => {
    const today = new Date().toISOString().split("T")[0];
    const newsDate = date || today;

    const params = new URLSearchParams({
        page: "1",
        limit: limit.toString(),
        news_date: newsDate,
    });

    try {
        const res = await fastApi.get(`/api/recommend/${encodeURIComponent(category)}?${params.toString()}`);
        console.log(`📚 ${category} 도서 조회 성공`, res.data);
        return res.data.books || res.data;
    } catch (error) {
        console.error(`❌ ${category} 도서 조회 실패:`, error);
        throw error.response?.data || { error: "요청 실패" };
    }
};
