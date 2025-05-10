import React from "react";
import { useLocation, useParams } from "react-router-dom";

const RecommendBookList = () => {
    const { state } = useLocation();
    const { categoryId } = useParams();

    const styles = {
        wrapper: {
        },
    };

    return (
        <div style={styles.wrapper}>
        <h1>{categoryId.toUpperCase()} - 추천 도서 목록</h1>
        </div>
    );
};

export default RecommendBookList;
