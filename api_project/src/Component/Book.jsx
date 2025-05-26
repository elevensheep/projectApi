import React, { useState } from "react";
import BookDetail from "./BookDetail";

const styles = {
    container: {
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        overflow: "hidden",
        cursor: "pointer",
    },
    img: {
        width: "100%",
        height: "75%",
        objectFit: "contain",
    },
    text: {
        margin: "10px 0",
        whiteSpace: "nowrap",
        overflow: "hidden",
        textOverflow: "ellipsis",
        textAlign: "center",
    },
};

const Book = ({ bookIsbn, bookImg, bookAlt, bookTitle, styles: customStyles }) => {
    const [isDetailOpen, setIsDetailOpen] = useState(false);

    const handleClick = () => {
        setIsDetailOpen(true);
    };

    const handleClose = () => {
        setIsDetailOpen(false);
    };

    return (
        <>
            <div style={{ ...styles.container, ...customStyles }} onClick={handleClick}>
                <img src={bookImg} alt={bookAlt || "Book Image"} style={styles.img} />
                <h3 style={styles.text}>{bookTitle}</h3>
            </div>

            {isDetailOpen && (
                <BookDetail 
                    isbn={bookIsbn}
                    title={bookTitle}
                    img={bookImg}
                    description={`${bookTitle}의 상세 정보입니다.`}
                    onClose={handleClose}
                />
            )}
        </>
    );
};

export default Book;
