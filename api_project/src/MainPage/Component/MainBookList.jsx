import React, { useRef } from "react";
import { motion, LayoutGroup, AnimatePresence } from "framer-motion";
import { Outlet, useNavigate } from "react-router-dom";
import Book from "../../Component/Book.jsx";
import books from "../../Component/BookDump.jsx";

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        overflow: "hidden",
        paddingBottom: "10px",
        width: "100%",
        maxWidth: "1440px",
        margin: "0 auto",
        position: "relative",
    },
    bookContainer: {
        width: "150px",
        cursor: "pointer",
        transition: "width 0.3s ease",
        flexShrink: 0,
    },
    scrollContainer: {
        display: "flex",
        gap: "20px",
        overflow: "hidden",
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
    const navigate = useNavigate();
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
        <LayoutGroup>
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
                    <div style={{ overflow: "hidden", width: "100%" }} ref={containerRef}>
                        <motion.div 
                            style={{
                                ...styles.scrollContainer,
                                width: `${(books.length * (ITEM_WIDTH + GAP)) - GAP}px`,
                            }}
                        >
                            {books.map((book) => (
                                <motion.div 
                                    key={book.isbn}
                                    layoutId={book.isbn}
                                    style={styles.bookContainer}
                                    onClick={() => navigate(`${book.isbn}`)}
                                >
                                    <Book 
                                        bookImg={book.img} 
                                        styles={{ width: "100%", height: "100%" }} 
                                        bookIsbn={book.isbn}
                                        bookTitle={book.title}
                                        bookAlt={book.title}
                                        
                                    />
                                </motion.div>
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

            {/* BookDetail이 애니메이션으로 나타나도록 설정 */}
            <AnimatePresence>
                <Outlet />
            </AnimatePresence>
        </LayoutGroup>
    );
};

export default MainBookList;
