import React from "react";
import { Link } from "react-router-dom";


const Icons = ({ link, icon, text }) => {
    const styles = {
        wrapper: {
            backgroundImage: `url(${icon})`, // ✅ 이미지 경로 설정
            backgroundSize: "cover",        // ✅ 이미지 크기 조정
            backgroundPosition: "center",
            borderRadius: "20px",
            alignItems: "center",
            justifyContent: "center",
            display: "flex",
            width: "250px",
            height: "250px",
            textColor: "white",
            textRendering: "optimizeLegibility",
            border: "2px solid black",
        },
        text: {
            color: "white",
            fontSize: "36px",
            textAlign: "center",
            textShadow: "2px 2px 4px rgba(0, 0, 0, 0.5)",
        },
    };

    return (
        <div style={styles.wrapper}>
            <Link to={link}>
                {text && <h2 style={styles.text}>{text}</h2>}
            </Link>
        </div>
    );
};

export default Icons;
