import React, { useRef, useState, useEffect } from "react";
import { motion } from "framer-motion";
import Book from "../../../Component/Book.jsx";
import BookDetail from "../../../Component/BookDetail.jsx";
import { fetchBooksByCategory } from "../../../service/recommendService.js";

const CATEGORIES = ["ecomonic", "society", "sports", "politics", "world"];
const ITEM_WIDTH = 150;
const GAP = 20;
const MAX_BOOKS = 20;

const MainBookList = () => {
    const containerRef = useRef(null);
    const [books, setBooks] = useState([]);
    const [selectedIsbn, setSelectedIsbn] = useState(null);
    const [canScrollLeft, setCanScrollLeft] = useState(false);
    const [canScrollRight, setCanScrollRight] = useState(true);

    const updateScrollButtons = () => {
        const container = containerRef.current;
        if (!container) return;
        const { scrollLeft, scrollWidth, clientWidth } = container;
        setCanScrollLeft(scrollLeft > 0);
        setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 1);
    };

    const handleLeftClick = () => {
        const container = containerRef.current;
        container.scrollBy({ left: -(ITEM_WIDTH + GAP), behavior: "smooth" });
    };

    const handleRightClick = () => {
        const container = containerRef.current;
        container.scrollBy({ left: ITEM_WIDTH + GAP, behavior: "smooth" });
    };

    useEffect(() => {
        const fetchAllBooks = async () => {
            try {
                const allBooks = [];
                for (const category of CATEGORIES) {
                    const data = await fetchBooksByCategory(category, 4);
                    allBooks.push(...data);
                }
                setBooks(allBooks.slice(0, MAX_BOOKS));
            } catch (err) {
                console.error("❌ 카테고리별 도서 조회 실패:", err);
            }
        };
        fetchAllBooks();
    }, []);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;
        updateScrollButtons();
        container.addEventListener("scroll", updateScrollButtons);
        return () => container.removeEventListener("scroll", updateScrollButtons);
    }, [books]);

    return (
        <div
            style={{
                backgroundColor: "#EEEEEE",
                padding: "30px 20px",
                borderRadius: "16px",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
                margin: "40px auto",
                maxWidth: "1440px",
            }}
        >
            <h2 style={{ textAlign: "left", padding: "0 0 10px 5px" }}>추천 도서</h2>

            <div
                style={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    overflow: "hidden",
                    paddingBottom: "10px",
                    width: "100%",
                    position: "relative",
                }}
            >
                {/* 왼쪽 버튼 */}
                <button
                    style={{
                        position: "absolute",
                        left: "10px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        zIndex: 1,
                        width: "40px",
                        height: "40px",
                        borderRadius: "50%",
                        border: "none",
                        backgroundColor: canScrollLeft ? "rgba(255, 255, 255, 0.9)" : "rgba(200, 200, 200, 0.4)",
                        boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
                        fontSize: "20px",
                        fontWeight: "bold",
                        color: "#333",
                        cursor: canScrollLeft ? "pointer" : "not-allowed",
                        opacity: canScrollLeft ? 1 : 0.4,
                        transition: "background-color 0.2s",
                    }}
                    onClick={handleLeftClick}
                    disabled={!canScrollLeft}
                >
                    {"<"}
                </button>

                {/* 스크롤 영역 */}
                <div
                    style={{
                        overflowX: "auto",
                        width: "100%",
                        scrollBehavior: "smooth",
                        maxWidth: "1400px",
                        margin: "0 auto",
                    }}
                    ref={containerRef}
                >
                    <motion.div
                        style={{
                            display: "flex",
                            gap: `${GAP}px`,
                            width: "fit-content", // 수정: 고정 너비 대신 콘텐츠 크기만큼만
                        }}
                    >
                        {books.map((book) => (
                            <div
                                key={book.books_isbn}
                                style={{
                                    width: `${ITEM_WIDTH}px`,
                                    cursor: "pointer",
                                    flexShrink: 0,
                                }}
                                onClick={() => setSelectedIsbn(book.books_isbn)}
                            >
                                <Book
                                    bookImg={book.books_img}
                                    bookTitle={book.books_title}
                                    bookIsbn={book.books_isbn}
                                    styles={{ width: "100%", height: "100%" }}
                                />
                            </div>
                        ))}
                    </motion.div>
                </div>

                {/* 오른쪽 버튼 */}
                <button
                    style={{
                        position: "absolute",
                        right: "10px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        zIndex: 1,
                        width: "40px",
                        height: "40px",
                        borderRadius: "50%",
                        border: "none",
                        backgroundColor: canScrollRight ? "rgba(255, 255, 255, 0.9)" : "rgba(200, 200, 200, 0.4)",
                        boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
                        fontSize: "20px",
                        fontWeight: "bold",
                        color: "#333",
                        cursor: canScrollRight ? "pointer" : "not-allowed",
                        opacity: canScrollRight ? 1 : 0.4,
                        transition: "background-color 0.2s",
                    }}
                    onClick={handleRightClick}
                    disabled={!canScrollRight}
                >
                    {">"}
                </button>
            </div>

            {selectedIsbn && (
                <div
                    onClick={() => setSelectedIsbn(null)}
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
                    <BookDetail isbn={selectedIsbn} />
                </div>
            )}
        </div>
    );
};

export default MainBookList;
