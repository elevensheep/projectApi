import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
    const styles = {
        wrapper: {
            width: "1440px",
            height: "100px",
            margin: "0 auto",
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
            gap: "20px"
        },
        searchArea: {
            display: "flex",
            alignItems: "center",
            border: "1px solid black",
            borderRadius: "10px",
            height: "30px",
            width: "300px",
            overflow: "hidden",
            padding: "4px"
        },
        input: {
            flex: 1,
            border: 'none',
            outline: 'none',
            padding: '8px',
        },
        button: {
            padding: "8px 16px",
            fontSize: "10px",
            border: "none",
            backgroundColor: "#fff",
            cursor: "pointer",
        },
        textColor: {
            color : "#d3d3d3"
        }
    };

    return (
        <div style={styles.wrapper}>
            <div style={styles.leftGroup}>
                <h1>Title</h1>
                <nav style={styles.nav}>
                    <Link to="/recommend">도서 추천</Link>
                    <Link to="/list">도서 목록</Link>
                </nav>
            </div>  

            <div style={styles.authLinks}>
                <div style={styles.searchArea}>
                    <input type="text" placeholder="검색어 입력" style={styles.input} />    
                    <button style={styles.button}><span className="material-symbols-outlined">search</span></button>
                </div>
                
                <Link to="/login" style={styles.textColor}>로그인</Link>
                <Link to="/sign" style={styles.textColor}>회원가입</Link>
            </div>
        </div>
    );
};

export default Header;
