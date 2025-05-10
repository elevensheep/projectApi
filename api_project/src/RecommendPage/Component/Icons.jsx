import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const Icons = ({ link, icon, text, width = "250px", height = "250px", onClick }) => {
    const styles = {
        wrapper: {
            backgroundImage: `url(${icon})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            borderRadius: "20px",
            border: "2px solid black",
            alignItems: "center",
            justifyContent: "center",
            display: "flex",
            width: width, // Dynamic width
            height: height, // Dynamic height
            color: "white",
            cursor: "pointer",
            overflow: "hidden",
        },
        text: {
            fontSize: "36px",
            textAlign: "center",
            textShadow: "2px 2px 4px rgba(0, 0, 0, 0.5)",
        },
    };

    return (
        <Link to={link} style={{ textDecoration: "none" }}>
            <motion.div
                style={styles.wrapper}
                onClick={onClick}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 1 }}
                initial={{ opacity: 1 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 1 }}
            >
                <h2 style={styles.text}>{text}</h2>
            </motion.div>
        </Link>
    );
};

export default Icons;
