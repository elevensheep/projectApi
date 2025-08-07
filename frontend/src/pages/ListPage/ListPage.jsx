import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchAllBooks, fetchBooksByCategory } from "../../service/bookService";
import Book from "../../Component/Book";
import BookDetail from "../../Component/BookDetail";

const categories = [
    "인문과학", "사회과학", "자연과학", "어문학", "미분류", "문학", "한국소설"
];

const ListPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const category = searchParams.get("category") || "";
    const currentPage = parseInt(searchParams.get("page") || "1", 10);
    const [books, setBooks] = useState([]);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedBookIsbn, setSelectedBookIsbn] = useState(null);
    const limit = 20;
    const maxButtons = 10;

    // 파스텔톤 색상 팔레트
    const pastelColors = {
        "인문과학": "#FFB3BA", // 파스텔 핑크
        "사회과학": "#BAFFC9", // 파스텔 그린
        "자연과학": "#BAE1FF", // 파스텔 블루
        "어문학": "#FFFFBA", // 파스텔 옐로우
        "미분류": "#E8BAFF", // 파스텔 퍼플
        "문학": "#FFD4BA", // 파스텔 오렌지
        "한국소설": "#BAFFE8", // 파스텔 민트
    };

    const handleCategoryChange = (newCategory) => {
        setSearchParams({ category: newCategory, page: "1" });
    };

    const handlePageChange = (page) => {
        setSearchParams({ category, page: page.toString() });
    };

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                console.log("📚 ListPage - 도서 목록 요청:", { category, currentPage });
                
                const res = category
                    ? await fetchBooksByCategory(category, currentPage - 1)
                    : await fetchAllBooks(currentPage - 1);

                console.log("✅ ListPage - 도서 목록 응답:", res);
                
                // Spring Boot API 응답 구조에 맞게 처리
                if (res && res.content) {
                    setBooks(res.content || []);
                    setTotalPages(res.totalPages || 1);
                } else {
                    // FastAPI 응답 구조 (books 배열)
                    setBooks(res.books || res || []);
                    setTotalPages(res.totalPages || Math.ceil((res.total || 0) / limit) || 1);
                }
            } catch (err) {
                console.error("❌ ListPage - 도서 조회 실패:", err);
                setBooks([]);
                setTotalPages(1);
            }
        };

        fetchBooks();
    }, [category, currentPage]);

    // 페이지 버튼 그룹 계산
    const currentGroup = Math.floor((currentPage - 1) / maxButtons);
    const startPage = currentGroup * maxButtons + 1;
    const endPage = Math.min(startPage + maxButtons - 1, totalPages);
    const pageNumbers = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

    return (
        <div style={{ display: "flex", maxWidth: "1400px", margin: "0 auto", padding: "40px 0" }}>
            {/* 카테고리 패널 - 스크롤 고정 */}
            <aside style={{ 
                width: "200px", 
                paddingRight: "20px",
                position: "sticky",
                top: "205px",
                height: "fit-content",
                alignSelf: "flex-start"
            }}>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {categories.map((cat) => {
                        const isSelected = category === cat;
                        const pastelColor = pastelColors[cat] || "#F0F0F0";
                        
                        return (
                            <button
                                key={cat}
                                onClick={() => handleCategoryChange(cat)}
                                style={{
                                    padding: "12px 16px",
                                    border: "none",
                                    borderRadius: "8px",
                                    backgroundColor: isSelected ? pastelColor : "#ffffff",
                                    color: isSelected ? "#333333" : "#666666",
                                    fontWeight: "600",
                                    cursor: "pointer",
                                    fontSize: "14px",
                                    boxShadow: isSelected 
                                        ? `0 4px 12px ${pastelColor}80` 
                                        : "0 2px 8px rgba(0, 0, 0, 0.1)",
                                    transition: "all 0.2s ease-in-out",
                                    transform: isSelected ? "translateY(-1px)" : "translateY(0)",
                                    border: isSelected 
                                        ? `2px solid ${pastelColor}` 
                                        : "1px solid #e0e0e0",
                                    position: "relative",
                                    overflow: "hidden",
                                }}
                                onMouseEnter={(e) => {
                                    if (!isSelected) {
                                        e.target.style.backgroundColor = pastelColor + "20";
                                        e.target.style.boxShadow = `0 4px 12px ${pastelColor}40`;
                                        e.target.style.transform = "translateY(-1px)";
                                        e.target.style.color = "#333333";
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (!isSelected) {
                                        e.target.style.backgroundColor = "#ffffff";
                                        e.target.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.1)";
                                        e.target.style.transform = "translateY(0)";
                                        e.target.style.color = "#666666";
                                    }
                                }}
                            >
                                {cat}
                            </button>
                        );
                    })}
                </div>
            </aside>

            {/* 책 리스트 */}
            <main style={{ flex: 1 }}>
                {books.length > 0 ? (
                    <ul
                        style={{
                            listStyle: "none",
                            padding: 0,
                            display: "grid",
                            gridTemplateColumns: "repeat(4, 1fr)",
                            gap: "30px",
                        }}
                    >
                        {books.map((book) => (
                            <li
                                key={book.bookIsbn || book.books_isbn}
                                style={{
                                    width: "250px",
                                    height: "300px",
                                    borderRadius: "10px",
                                    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                                    backgroundColor: "#F5F5EB",
                                    cursor: "pointer",
                                    overflow: "hidden",
                                }}
                                onClick={() => setSelectedBookIsbn(book.bookIsbn || book.books_isbn)}
                            >
                                <Book
                                    bookIsbn={book.bookIsbn || book.books_isbn}
                                    bookImg={book.bookImg || book.books_img}
                                    bookAlt={book.bookTitle || book.books_title}
                                    bookTitle={book.bookTitle || book.books_title}
                                    styles={{ height: "100%" }}
                                />
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p style={{ textAlign: "center" }}>도서가 없습니다.</p>
                )}

                {/* 페이지네이션 */}
                <div style={{ marginTop: "30px", display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
                    {/* « 이전 그룹 */}
                    {startPage > 1 && (
                        <button onClick={() => handlePageChange(startPage - 1)} style={buttonStyle()}>
                            «
                        </button>
                    )}

                    {/* 이전 */}
                    <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        style={buttonStyle(currentPage === 1)}
                    >
                        이전
                    </button>

                    {/* 페이지 숫자 */}
                    {pageNumbers.map((pageNum) => (
                        <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            style={buttonStyle(false, pageNum === currentPage)}
                        >
                            {pageNum}
                        </button>
                    ))}

                    {/* 다음 */}
                    <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        style={buttonStyle(currentPage === totalPages)}
                    >
                        다음
                    </button>

                    {/* » 다음 그룹 */}
                    {endPage < totalPages && (
                        <button onClick={() => handlePageChange(endPage + 1)} style={buttonStyle()}>
                            »
                        </button>
                    )}
                </div>
            </main>

            {/* 상세 모달 */}
            {selectedBookIsbn && (
                <div
                    onClick={(e) => {
                        if (e.target === e.currentTarget) {
                            setSelectedBookIsbn(null);
                        }
                    }}
                    style={{
                        position: "fixed",
                        top: 0,
                        left: 0,
                        width: "100vw",
                        height: "100vh",
                        backgroundColor: "rgba(0, 0, 0, 0.5)",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        zIndex: 999,
                    }}
                >
                    <BookDetail isbn={selectedBookIsbn} onClose={() => setSelectedBookIsbn(null)} />
                </div>
            )}
        </div>
    );
};

// 페이지 버튼 스타일
const buttonStyle = (disabled = false, isActive = false) => ({
    padding: "8px 16px",
    fontSize: "14px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    backgroundColor: isActive ? "#3f75ff" : "#fff",
    color: isActive ? "#fff" : "#333",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    transition: "all 0.2s",
});

export default ListPage;
