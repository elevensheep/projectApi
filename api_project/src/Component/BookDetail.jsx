import React from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import books from "./BookDump";

const styles = {
    detailContainer: {
        position: "fixed",
        width: "60%",
        maxWidth: "1440px",
        height: "600px",
        backgroundColor: "#fff",
        borderRadius: "16px",
        boxShadow: "0px 12px 24px rgba(0, 0, 0, 0.15)",
        padding: "20px",
        zIndex: 100,
        cursor: "pointer",
        transform: "translate(-50%, -50%)",
        overflow: "hidden",
        display: "flex",
        gap: "20px",
        alignItems: "center",
        margin: "0",
    },
    imgContainer: {
        width: "50%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",  // 왼쪽 정렬
        alignItems: "center",
        padding: "0",
    },
    img: {
        width: "100%",
        height: "70%",
        maxHeight: "500px",
        objectFit: "contain",
        borderRadius: "12px",
    },
    contentContainer: {
        width: "50%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start", // 위에서부터 시작
        alignItems: "flex-start",     // 왼쪽 정렬
        padding: "0",
        gap: "10px",
        marginTop: "20px",
    },
    title: {
        fontSize: "24px",
        fontWeight: "bold",
        marginBottom: "10px",
        textAlign: "left",
    },
    heading: {
        fontSize: "20px",
        fontWeight: "bold",
        marginBottom: "5px",
        textAlign: "left",
    },
    description: {
        textAlign: "left",
        fontSize: "16px",
        lineHeight: "1.5",
        marginTop: "0",
    },
};

const BookDetail = () => {
    const { isbn } = useParams();
    const navigate = useNavigate();
    const book = books.find((b) => b.isbn === isbn);

    if (!book) return null;

    return (
        <motion.div
            layoutId={isbn}
            onClick={() => navigate(-1)}
            style={styles.detailContainer}
            initial={{ opacity: 0, scale: 1.2 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.2 }}
            transition={{
                duration: 0.3,
                ease: "easeInOut",
            }}
        >
            {/* 왼쪽 이미지 영역 */}
            <div style={styles.imgContainer}>
                <img src={book.img} alt={book.title} style={styles.img} />
                <h1 style={styles.title}>{book.title}</h1>
            </div>

            {/* 오른쪽 텍스트 영역 */}
            <div style={styles.contentContainer}>
                <h1 style={styles.heading}>책 소개</h1>
                <p style={styles.description}>
                    {book.title}의 상세 정보입니다. Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                    Aenean sit amet urna at elit efficitur tincidunt. Sed euismod tortor ac tincidunt convallis.
                </p>
            </div>
        </motion.div>
    );
};

export default BookDetail;
