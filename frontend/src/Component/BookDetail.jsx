import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { fetchBookDetail } from "../service/bookService";
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
const BookDetail = ({ isbn }) => {
    const [book, setBook] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await fetchBookDetail(isbn);
                setBook(data);
            } catch (err) {
                console.error("❌ 도서 상세 정보 불러오기 실패:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isbn]);

    if (loading) return <p style={{ color: "white" }}>불러오는 중...</p>;
    if (!book) return <p style={{ color: "white" }}>책 정보를 찾을 수 없습니다.</p>;

    return (
        <motion.div
            layoutId={isbn}
            style={{
                position: "relative",
                width: "60%",
                height: "600px",
                backgroundColor: "#fff",
                borderRadius: "16px",
                boxShadow: "0px 12px 24px rgba(0, 0, 0, 0.15)",
                padding: "20px",
                zIndex: 1000,
                display: "flex",
                gap: "20px",
                alignItems: "center",
            }}
            initial={{ opacity: 0, scale: 0.9 }}  // 👈 작게 시작
            animate={{ opacity: 1, scale: 1 }}    // 👈 자연스럽게 커짐
            exit={{ opacity: 0, scale: 0.9 }}     // 👈 작게 사라짐
            transition={{ duration: 0.3, ease: "easeInOut" }}
        >

            <div style={{ width: "50%", height: "100%", paddingTop: "70px" }}>
                <img
                    src={book.bookImg}
                    alt={book.bookTitle}
                    style={{
                        width: "100%",
                        height: "80%",
                        objectFit: "contain",
                        borderRadius: "12px",
                    }}
                />
                <h1 style={{ fontSize: "24px", fontWeight: "bold", textAlign: "center" }}>
                    {book.bookTitle}
                </h1>

            </div>
            <div style={{ width: "50%", overflowY: "auto", height: "100%", paddingTop: "70px" }}>
                <button style={{
                    width: "100%",
                    height: "40px",
                    border: "none",
                    borderRadius: "10px",
                    backgroundColor: "#7b68ee",
                    color: "white",
                    fontWeight: "bold"
                }}>
                    알라딘 재고확인
                </button>
            </div>
        </motion.div>
    );
};

export default BookDetail;
