import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
    const styles = {
        wrapper: {
            width: "100%",
            height: "100px",
            position: "fixed",
            top: 0,
            left: 0,
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            backdropFilter: "blur(5px)",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
            zIndex: 1000,
            display: "flex",
            justifyContent: "center", // 컨텐츠를 중앙 정렬
        },
        content: {
            width: "100%",
            maxWidth: "1440px",  // 최대 너비
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 20px",
            boxSizing: "border-box",
        },
        leftGroup: {
            display: "flex",
            alignItems: "center",
            gap: "50px",
        },
        nav: {
            display: "flex",
            gap: "20px",
        },
        authLinks: {
            display: "flex",
            alignItems: "center",
            gap: "20px",
        },
        searchArea: {
            display: "flex",
            alignItems: "center",
            border: "1px solid #ccc",
            borderRadius: "10px",
            height: "30px",
            width: "300px",
            overflow: "hidden",
            padding: "4px",
            backgroundColor: "#fff",
        },
        input: {
            flex: 1,
            border: "none",
            outline: "none",
            padding: "8px",
        },
        button: {
            padding: "8px 16px",
            fontSize: "12px",
            border: "none",
            backgroundColor: "transparent",
            cursor: "pointer",
        },
        textColor: {
            color: "#D3D3D3",
            textDecoration: "none",
        },
    };

    return (
        <div style={styles.wrapper}>
            <div style={styles.content}>
                <div style={styles.leftGroup}>
                    <Link to="/"><h1>북트렌드</h1></Link>
                    <nav style={styles.nav}>
                        <Link to="/recommend">도서 추천</Link>
                        <Link to="/list">도서 목록</Link>
                    </nav>
                </div>

                <div style={styles.authLinks}>
                    <div style={styles.searchArea}>
                        <input type="text" placeholder="검색어 입력" style={styles.input} />
                        <button style={styles.button}>
                            <span className="material-symbols-outlined">search</span>
                        </button>
                    </div>
                    <Link to="/login" style={styles.textColor}>로그인</Link>
                    <Link to="/sign" style={styles.textColor}>회원가입</Link>
                </div>
            </div>
        </div>
    );
};

export default Header;
