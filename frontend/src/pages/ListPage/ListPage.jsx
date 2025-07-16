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

    const handleCategoryChange = (newCategory) => {
        setSearchParams({ category: newCategory, page: "1" });
    };

    const handlePageChange = (page) => {
        setSearchParams({ category, page: page.toString() });
    };

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                const res = category
                    ? await fetchBooksByCategory(category, currentPage - 1)
                    : await fetchAllBooks(currentPage - 1);

                setBooks(res.content || []);
                setTotalPages(res.totalPages || 1);
            } catch (err) {
                console.error("도서 조회 실패", err);
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
            {/* 카테고리 패널 */}
            <aside style={{ width: "200px", paddingRight: "20px" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => handleCategoryChange(cat)}
                            style={{
                                padding: "10px",
                                border: "none",
                                borderRadius: "6px",
                                backgroundColor: category === cat ? "#4f8cff" : "#f0f0f0",
                                color: category === cat ? "white" : "black",
                                fontWeight: "bold",
                                cursor: "pointer",
                            }}
                        >
                            {cat}
                        </button>
                    ))}
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
                                key={book.bookIsbn}
                                style={{
                                    width: "250px",
                                    height: "300px",
                                    borderRadius: "10px",
                                    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                                    backgroundColor: "#F5F5EB",
                                    cursor: "pointer",
                                    overflow: "hidden",
                                }}
                                onClick={() => setSelectedBookIsbn(book.bookIsbn)}
                            >
                                <Book
                                    bookIsbn={book.bookIsbn}
                                    bookImg={book.bookImg}
                                    bookAlt={book.bookTitle}
                                    bookTitle={book.bookTitle}
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
