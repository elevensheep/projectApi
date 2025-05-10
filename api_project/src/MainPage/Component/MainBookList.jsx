import React, { useRef } from "react";
import { motion, useAnimation } from "framer-motion";
import Book from "../../Component/Book.jsx";

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        overflow: "hidden",
        paddingBottom: "10px",
        width: "1440px",
        position: "relative",
    },
    scrollContainer: {
        display: "flex",
        gap: "20px",
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
        padding : "0px 0px 20px 5px",
        margin: "0",
    }
};

const books = [
    {
        title: "소년이로 (편혜영 소설집)",
        img: "https://shopping-phinf.pstatic.net/main_3243615/32436154262.20221019142158.jpg",
        styles: { backgroundColor: "#222" },
        isbn: "9788932035338",
    },
    {
        title: "82년생 김지영",
        img: "https://shopping-phinf.pstatic.net/main_3246707/32467074651.20231003084626.jpg?type=w300",
        styles: { backgroundColor: "#333" },
        isbn: "9788937473135",
    },
    {
        title: "작별하지 않는다",
        img: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300",
        styles: { backgroundColor: "#444" },
        isbn: "9788954682152",
    },
    {
        title: "소년이로 (편혜영 소설집)",
        img: "https://shopping-phinf.pstatic.net/main_3243615/32436154262.20221019142158.jpg",
        styles: { backgroundColor: "#222" },
        isbn: "9788932035338",
    },
    {
        title: "82년생 김지영",
        img: "https://shopping-phinf.pstatic.net/main_3246707/32467074651.20231003084626.jpg?type=w300",
        styles: { backgroundColor: "#333" },
        isbn: "9788937473135",
    },
    {
        title: "작별하지 않는다",
        img: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300",
        styles: { backgroundColor: "#444" },
        isbn: "9788954682152",
    },
        {
        title: "소년이로 (편혜영 소설집)",
        img: "https://shopping-phinf.pstatic.net/main_3243615/32436154262.20221019142158.jpg",
        styles: { backgroundColor: "#222" },
        isbn: "9788932035338",
    },
    {
        title: "82년생 김지영",
        img: "https://shopping-phinf.pstatic.net/main_3246707/32467074651.20231003084626.jpg?type=w300",
        styles: { backgroundColor: "#333" },
        isbn: "9788937473135",
    },
    {
        title: "작별하지 않는다",
        img: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300",
        styles: { backgroundColor: "#444" },
        isbn: "9788954682152",
    },
        {
        title: "소년이로 (편혜영 소설집)",
        img: "https://shopping-phinf.pstatic.net/main_3243615/32436154262.20221019142158.jpg",
        styles: { backgroundColor: "#222" },
        isbn: "9788932035338",
    },
    {
        title: "82년생 김지영",
        img: "https://shopping-phinf.pstatic.net/main_3246707/32467074651.20231003084626.jpg?type=w300",
        styles: { backgroundColor: "#333" },
        isbn: "9788937473135",
    },
    {
        title: "작별하지 않는다",
        img: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300",
        styles: { backgroundColor: "#444" },
        isbn: "9788954682152",
    },
];

const BookArrange = () => {
    const containerRef = useRef(null);
    const controls = useAnimation();
    const ITEM_WIDTH = 150;
    const GAP = 20;
    const MOVE_DISTANCE = ITEM_WIDTH + GAP;

    const handleLeftClick = () => {
        const container = containerRef.current;
        const maxScrollLeft = 0;
        let newScrollLeft = container.scrollLeft - MOVE_DISTANCE;

        if (newScrollLeft < maxScrollLeft) {
        newScrollLeft = maxScrollLeft;
        }

        container.scrollTo({
            left: newScrollLeft,
            behavior: "smooth",
        });
    };

    const handleRightClick = () => {
        const container = containerRef.current;
        const maxScrollLeft = container.scrollWidth - container.clientWidth;
        let newScrollLeft = container.scrollLeft + MOVE_DISTANCE;

        if (newScrollLeft > maxScrollLeft) {
        newScrollLeft = maxScrollLeft;
        }

        container.scrollTo({
            left: newScrollLeft,
            behavior: "smooth",
        });
    };

    return (
        <div>
            <h2 style={styles.title}>추천 도서</h2>
            <div style={styles.wrapper}>
                <button
                    style={{ ...styles.button, ...styles.leftButton }}
                    onClick={handleLeftClick}
                >
                    {"<"}
                </button>

                <div style={{ overflow: "hidden", width: "100%" }} ref={containerRef}>
                    <motion.div style={styles.scrollContainer}>
                    {books.map((book, index) => (
                        <div key={`${book.isbn}-${index}`} style={{ minWidth: ITEM_WIDTH, flexShrink: 0 }}>
                        <Book bookImg={book.img} styles={book.styles} />
                        </div>
                    ))}
                    </motion.div>
                </div>

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

export default BookArrange;
