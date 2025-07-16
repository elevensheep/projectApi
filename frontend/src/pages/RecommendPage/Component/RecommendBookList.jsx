import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchRecommendedBooks } from "../../../service/recommendService";
import Book from "../../../Component/Book";
import BookDetail from "../../../Component/BookDetail";

const RecommendBookList = () => {
    const { category } = useParams();
    const [searchParams, setSearchParams] = useSearchParams();
    const [books, setBooks] = useState([]);
    const [selectedBookIsbn, setSelectedBookIsbn] = useState(null);
    const [totalPages, setTotalPages] = useState(1);

    const today = new Date().toISOString().split("T")[0];
    const currentDate = searchParams.get("news_date") || today;
    const currentPage = parseInt(searchParams.get("page") || "1", 10);
    const limit = 15;
    const maxButtons = 10;

    const handleDateChange = (e) => {
        const newDate = e.target.value;
        setSearchParams({ news_date: newDate, page: "1" });
    };

    const handlePageChange = (page) => {
        setSearchParams({ news_date: currentDate, page: page.toString() });
    };

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                const data = await fetchRecommendedBooks({
                    newsCategory: category,
                    newsDate: currentDate,
                    page: currentPage,
                    limit,
                });
                setBooks(data.books || []);
                setTotalPages(Math.ceil((data.total || 0) / limit));
            } catch (err) {
                console.error("❌ 추천 도서 조회 실패:", err);
            }
        };

        fetchBooks();
    }, [category, currentDate, currentPage]);

    // 📌 페이지 그룹 계산
    const currentGroup = Math.floor((currentPage - 1) / maxButtons);
    const startPage = currentGroup * maxButtons + 1;
    const endPage = Math.min(startPage + maxButtons - 1, totalPages);
    const pageNumbers = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

    return (
        <div style={{ textAlign: "center", margin: "40px auto", maxWidth: "1380px" }}>
            {/* 날짜 선택 */}
            <div style={{ textAlign: "right", marginBottom: "20px" }}>
                <input
                    type="date"
                    value={currentDate}
                    onChange={handleDateChange}
                    style={{
                        padding: "10px 20px",
                        fontSize: "16px",
                        borderRadius: "8px",
                        border: "1px solid #ccc",
                    }}
                />
            </div>

            {/* 도서 리스트 */}
            {books.length > 0 ? (
                <ul
                    style={{
                        listStyle: "none",
                        padding: 0,
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "center",
                        gap: "30px",

                    }}
                >
                    {books.map((book) => (
                        <li
                            key={book.books_isbn}
                            style={{
                                width: "250px",
                                height: "300px",
                                borderRadius: "10px",
                                boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                                overflow: "hidden",
                                cursor: "pointer",
                                backgroundColor: '#F5F5EB'
                            }}
                            onClick={() => setSelectedBookIsbn(book.books_isbn)}
                        >
                            <Book
                                bookIsbn={book.books_isbn}
                                bookImg={book.books_img}
                                bookAlt={book.books_title}
                                bookTitle={book.books_title}
                                styles={{ height: "100%" }}
                            />
                        </li>
                    ))}
                </ul>
            ) : (
                <p>도서가 없습니다.</p>
            )}

            {/* 페이지네이션 */}
            <div style={{ marginTop: "30px", display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
                {/* « 버튼 - 이전 그룹 */}
                {startPage > 1 && (
                    <button onClick={() => handlePageChange(startPage - 1)} style={buttonStyle()}>
                        «
                    </button>
                )}
                {/* 이전 페이지 */}
                <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    style={buttonStyle(currentPage === 1)}
                >
                    이전
                </button>

                {/* 숫자 페이지들 */}
                {pageNumbers.map((pageNum) => (
                    <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        style={buttonStyle(pageNum === currentPage, true)}
                    >
                        {pageNum}
                    </button>
                ))}

                {/* 다음 페이지 */}
                <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    style={buttonStyle(currentPage === totalPages)}
                >
                    다음
                </button>
                {/* » 버튼 - 다음 그룹 */}
                {endPage < totalPages && (
                    <button onClick={() => handlePageChange(endPage + 1)} style={buttonStyle()}>
                        »
                    </button>
                )}
            </div>

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
                    <BookDetail isbn={selectedBookIsbn} onClose={() => setSelectedBookIsbn(null)}/>
                </div>
            )}
        </div>
    );
};

// 버튼 스타일 함수
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

export default RecommendBookList;
