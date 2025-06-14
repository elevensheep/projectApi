import React from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import books from "./BookDump";
import Aladin from "./Aladin";

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
        width: "100%",
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
        height: "420px",
        overflowY: "scroll"
    },
    aladinBtn: {
        position: 'relative',
        border: 'none',
        padding: '15px 30px',
        borderRadius: '15px',
        fontFamily: '"paybooc-Light", sans-serif',
        boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2)',
        textDecoration: 'none',
        fontWeight: 600,
        transition: '0.25s',
        width: "100%",
        height: "40px",
        display: 'flex',               // ← 변경
        justifyContent: 'center',     // ← 글씨 가로 가운데
        alignItems: 'center',         // ← 글씨 세로 가운데
        marginRight: "0"
    }

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
            <div style={{...styles.contentContainer, paddingTop:"70px"}}>
                {/* 오른쪽 텍스트 영역 */}
                {/* <div style={styles.contentContainer}>
                    <h1 style={styles.heading}>책 소개</h1>
                    <p style={styles.description}>
                    환경경제학의 기본 이론을 체계적으로 정리한 대학교재 겸 이론서. 이 책은 환경과 경제에 대한 기초적인 지식을 시작으로 환경과 시장, 환경자원과 자연자원의 경제적 가치, 비용편익분석과 환경, 환경위험, 전략적 상호작용 등을 자세하게 정리하였다.
                    </p>
                </div> */}
                <button style={styles.aladinBtn}>알라딘 재고확인</button>
                <div>
                    <Aladin />
                </div>
            </div>

        </motion.div>
    );
};

export default BookDetail;
