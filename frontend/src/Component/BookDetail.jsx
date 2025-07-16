import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { fetchBookDetail, getBookStoresByIsbn } from "../service/bookService";
import Aladin from "./Aladin";

const BookDetail = ({ isbn, onClose }) => {
    const [book, setBook] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showStores, setShowStores] = useState(false);
    const [storeList, setStoreList] = useState([]);

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

    const handleToggleContent = async () => {
        if (!showStores) {
            try {
                const stores = await getBookStoresByIsbn(isbn);
                setStoreList(stores);
            } catch (err) {
                console.error("❌ 지점 정보 조회 실패:", err);
                return;
            }
        }
        setShowStores(!showStores);
    };

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
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
        >
            {/* 닫기 버튼 */}
            <button
                onClick={onClose}
                style={{
                    position: "absolute",
                    top: "10px",
                    right: "10px",
                    background: "transparent",
                    border: "none",
                    fontSize: "24px",
                    cursor: "pointer",
                }}
            >
                ×
            </button>

            {/* 이미지 + 제목 */}
            <div style={{ width: "50%", height: "100%", paddingTop: "50px" }}>
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
                <h1
                    style={{
                        fontSize: "24px",
                        fontWeight: "bold",
                        textAlign: "center",
                        marginTop: "10px",
                    }}
                >
                    {book.bookTitle}
                </h1>
            </div>

            {/* 오른쪽 정보 */}
            <div
                style={{
                    width: "50%",
                    height: "100%",
                    paddingTop: "50px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    paddingBottom: "50px",
                }}
            >
                {/* 설명 또는 알라딘 지점 */}
                <div
                    style={{
                        flex: 1,
                        overflowY: "auto",
                        paddingRight: "10px",
                        fontSize: "20px",
                        lineHeight: "1.6",
                        marginBottom: "10px",
                        marginTop: "20px",
                    }}
                >
                    {!showStores ? (
                        book.bookDescription || "도서 설명이 없습니다."
                    ) : (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                            {storeList.map((store, index) => (
                                <Aladin key={index} offName={store.offName} link={store.link} />
                            ))}
                        </div>
                    )}
                </div>

                {/* 토글 버튼 */}
                <button
                    style={{
                        width: "100%",
                        height: "40px",
                        border: "none",
                        borderRadius: "10px",
                        backgroundColor: "#7b68ee",
                        color: "white",
                        fontWeight: "bold",
                        marginTop: "10px",
                        cursor: "pointer",
                    }}
                    onClick={handleToggleContent}
                >
                    {showStores ? "책 정보 보기" : "알라딘 재고확인"}
                </button>
            </div>
        </motion.div>
    );
};

export default BookDetail;
