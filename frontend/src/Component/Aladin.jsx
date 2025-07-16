import React from 'react';

const Aladin = ({ offName, link }) => {
    const styles = {
        wrapper: {
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            width: "95px",
            height: "70px",
            fontSize: "10px",
            textAlign: "center",
            backgroundColor: "#f0f0f0",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            cursor: "pointer",
            transition: "transform 0.2s ease, box-shadow 0.2s ease"
        }
    };

    return (
        <div style={styles.wrapper}>
            <h3 style={{ marginTop: "0px" }}>{offName}</h3>
            <a href={link} target="_blank" rel="noopener noreferrer" style={{ marginTop: "3px" }}>
                바로가기
            </a>
        </div>
    );
};

export default Aladin;
