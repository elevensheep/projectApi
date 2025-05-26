import React from "react";
import { motion } from "framer-motion";

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
        zIndex: 1000,
        cursor: "pointer",
        transform: "translate(-50%, -50%)",
        overflow: "hidden",
        display: "flex",
        gap: "20px",
        alignItems: "center",
    },
    overlay: {
        position: "fixed",
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        top: 0,
        left: 0,
        zIndex: 999,
    },
    imgContainer: {
        width: "50%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start", 
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
        justifyContent: "flex-start", 
        alignItems: "flex-start",   
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
    closeButton: {
        position: "absolute",
        top: "10px",
        right: "10px",
        backgroundColor: "#f5f5f5",
        border: "none",
        cursor: "pointer",
        padding: "5px 10px",
        borderRadius: "8px",
    },
};

const BookDetail = ({ isbn, title, img, description, onClose }) => {
    return (
        <>
            {/* Overlay */}
            <div style={styles.overlay} onClick={onClose} />

            <motion.div
                layoutId={isbn}
                style={styles.detailContainer}
                initial={{ opacity: 0, scale: 1.2 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.2 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
            >
                {/* Close Button */}
                <button style={styles.closeButton} onClick={onClose}>X</button>

                {/* Left Image Section */}
                <div style={styles.imgContainer}>
                    <img src={img} alt={title} style={styles.img} />
                    <h1 style={styles.title}>{title}</h1>
                </div>

                {/* Right Text Section */}
                <div style={styles.contentContainer}>
                    <h1 style={styles.heading}>책 소개</h1>
                    <p style={styles.description}>{description}</p>
                </div>
            </motion.div>
        </>
    );
};

export default BookDetail;
