import React from "react";
import { Link } from "react-router-dom";

const styles = {
    link: {
        width: "100%",
        height: "100%",
        display: "block",  // 크기 조정이 가능하도록 설정
        textDecoration: "none",
    },
    container: {
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        overflow: "hidden",
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

const Book = ({ bookIsbn, bookImg, bookAlt, bookTitle, onClick, styles: customStyles }) => {
    return (
        <div
            style={{ ...styles.container, ...customStyles }}
            onClick={() => onClick && onClick(bookIsbn)}
        >
            <img src={bookImg} alt={bookAlt || "Book Image"} style={styles.img} />
            <h3 style={styles.text}>{bookTitle}</h3>
        </div>
    );
};



export default Book;
