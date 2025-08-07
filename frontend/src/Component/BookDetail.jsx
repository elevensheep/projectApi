import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { fetchBookDetail, getBookStoresByIsbn } from "../service/bookService";
import Aladin from "./Aladin";

const BookDetail = ({ isbn, onClose }) => {
    const [book, setBook] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showStores, setShowStores] = useState(false);
    const [storeList, setStoreList] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            if (!isbn) {
                setError("ISBN이 제공되지 않았습니다.");
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                console.log("📚 BookDetail - ISBN으로 도서 정보 요청:", isbn);
                
                const data = await fetchBookDetail(isbn);
                console.log("✅ BookDetail - 도서 정보 수신:", data);
                setBook(data);
            } catch (err) {
                console.error("❌ BookDetail - 도서 상세 정보 불러오기 실패:", err);
                setError(err.message || "도서 정보를 불러오는데 실패했습니다.");
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
                setError("지점 정보를 불러오는데 실패했습니다.");
                return;
            }
        }
        setShowStores(!showStores);
    };

    // Spring Boot API 응답의 필드명을 FastAPI 구조와 맞춰서 사용
    const getBookImage = () => {
        return book?.bookImg || book?.books_img || "https://via.placeholder.com/300x400?text=No+Image";
    };

    const getBookTitle = () => {
        return book?.bookTitle || book?.books_title || "제목 없음";
    };

    const getBookDescription = () => {
        return book?.bookDescription || book?.books_description || "도서 설명이 없습니다.";
    };

    if (loading) {
        return (
            <motion.div
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
                    justifyContent: "center",
                    alignItems: "center",
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
            >
                <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "24px", marginBottom: "10px" }}>📚</div>
                    <p style={{ fontSize: "18px", color: "#666" }}>도서 정보를 불러오는 중...</p>
                </div>
            </motion.div>
        );
    }

    if (error) {
        return (
            <motion.div
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
                    justifyContent: "center",
                    alignItems: "center",
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
            >
                <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "24px", marginBottom: "10px" }}>❌</div>
                    <p style={{ fontSize: "18px", color: "#e74c3c" }}>{error}</p>
                    <button
                        onClick={onClose}
                        style={{
                            marginTop: "20px",
                            padding: "10px 20px",
                            border: "none",
                            borderRadius: "8px",
                            backgroundColor: "#7b68ee",
                            color: "white",
                            cursor: "pointer",
                        }}
                    >
                        닫기
                    </button>
                </div>
            </motion.div>
        );
    }

    if (!book) {
        return (
            <motion.div
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
                    justifyContent: "center",
                    alignItems: "center",
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
            >
                <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "24px", marginBottom: "10px" }}>🔍</div>
                    <p style={{ fontSize: "18px", color: "#666" }}>책 정보를 찾을 수 없습니다.</p>
                    <button
                        onClick={onClose}
                        style={{
                            marginTop: "20px",
                            padding: "10px 20px",
                            border: "none",
                            borderRadius: "8px",
                            backgroundColor: "#7b68ee",
                            color: "white",
                            cursor: "pointer",
                        }}
                    >
                        닫기
                    </button>
                </div>
            </motion.div>
        );
    }

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
                    src={getBookImage()}
                    alt={getBookTitle()}
                    style={{
                        width: "100%",
                        height: "80%",
                        objectFit: "contain",
                        borderRadius: "12px",
                    }}
                    onError={(e) => {
                        e.target.src = "https://via.placeholder.com/300x400?text=No+Image";
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
                    {getBookTitle()}
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
                        getBookDescription()
                    ) : (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                            {storeList && storeList.length > 0 ? (
                                storeList.map((store, index) => (
                                    <Aladin key={index} offName={store.offName} link={store.link} />
                                ))
                            ) : (
                                <p style={{ color: "#666" }}>재고 정보가 없습니다.</p>
                            )}
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
