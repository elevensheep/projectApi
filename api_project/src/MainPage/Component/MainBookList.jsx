import React, { useRef } from "react";
import { motion } from "framer-motion";
import Book from "../../Component/Book.jsx";
import books from "../../Component/BookDump.jsx";
import { Link } from "react-router-dom";

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        overflow: "hidden",  // 전체적으로 스크롤바를 완전히 숨김
        paddingBottom: "10px",
        width: "100%",
        maxWidth: "1440px",
        margin: "0 auto",
        position: "relative",
    },
    bookContainer: {
        width: "150px", // 너비 조정
        cursor: "pointer",
        transition: "width 0.3s ease",
        flexShrink: 0,  // 책들이 줄어들지 않도록 설정
    },
    scrollContainer: {
        display: "flex",
        gap: "20px",
        overflow: "hidden",  // X, Y축 모두 스크롤바 제거
    },
    button: {
        position: "absolute",
        top: "50%",
        transform: "translateY(-50%)",
        backgroundColor: "transparent",
        color: "#000",
        border: "none",
        padding: "10px",
        cursor: "pointer",
        zIndex: 1,
    },
    leftButton: {
        left: "10px",
        fontSize: "24px",
    },
    rightButton: {
        right: "10px",
        fontSize: "24px",
    },
    title: {
        textAlign: "left",
        padding: "0px 0px 0px 5px",
        margin: "0 5px",
    },
};

const MainBookList = () => {
    const containerRef = useRef(null);
    const ITEM_WIDTH = 250;
    const GAP = 20;
    const MOVE_DISTANCE = ITEM_WIDTH + GAP;

    const handleLeftClick = () => {
        const container = containerRef.current;
        let newScrollLeft = container.scrollLeft - MOVE_DISTANCE;

        container.scrollTo({
            left: newScrollLeft,
            behavior: "smooth",
        });
    };

    const handleRightClick = () => {
        const container = containerRef.current;
        let newScrollLeft = container.scrollLeft + MOVE_DISTANCE;

        container.scrollTo({
            left: newScrollLeft,
            behavior: "smooth",
        });
    };

    return (
        <div>
            <h2 style={styles.title}>추천 도서</h2>
            <div style={styles.wrapper}>
                {/* 왼쪽 버튼 */}
                <button
                    style={{ ...styles.button, ...styles.leftButton }}
                    onClick={handleLeftClick}
                >
                    {"<"}
                </button>

                {/* 스크롤 컨테이너 */}
                <div 
                    style={{ overflow: "hidden", width: "100%" }} 
                    ref={containerRef}
                >
                    <motion.div 
                        style={{
                            ...styles.scrollContainer,
                            width: `${(books.length * (ITEM_WIDTH + GAP)) - GAP - 2000}px`, // 전체 너비 조정
                        }}
                    >
                        {books.map((book, index) => (
                            <div 
                                key={`${book.isbn}`} 
                                style={styles.bookContainer}
                            >
                                <Link to={`${book.isbn}`}>
                                    <Book 
                                        bookImg={book.img} 
                                        styles={{ width: "100%", height: "100%", marginTop: "0px" }} 
                                        bookIsbn={book.isbn}
                                    />
                                </Link>
                            </div>
                        ))}
                    </motion.div>
                </div>

                {/* 오른쪽 버튼 */}
                <button
                    style={{ ...styles.button, ...styles.rightButton }}
                    onClick={handleRightClick}
                >
                    {">"}
                </button>
            </div>
        </div>
    );
};

export default MainBookList;
