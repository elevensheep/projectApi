import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import Icons from "./Component/Icons";
import Economy from "./image/economy.png";
import Politics from "./image/politics.png";
import Society from "./image/society.png";
import Sports from "./image/sports.png";
import World from "./image/world.png";

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        alignItems: "center",
    },
    icons: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        gap: "20px",
    },
};

const iconData = [
    { link: "economy", icon: Economy, text: "경제" },
    { link: "politics", icon: Politics, text: "정치" },
    { link: "sports", icon: Sports, text: "스포츠" },
    { link: "society", icon: Society, text: "사회" },
    { link: "world", icon: World, text: "세계" },
];

const RecommendPage = () => {
    const [selected, setSelected] = useState(null);

    const handleClick = (index) => {
        setSelected(selected === index ? null : index);
    };

    return (
        <div style={styles.wrapper}>
            <h1>추천 도서</h1>
            <div style={styles.icons}>
                {iconData.map(({ link, icon, text }, index) => (
                    <motion.div
                        key={index}
                        layout
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 20,
                        }}
                        style={{
                            width: selected === index ? "500px" : "250px",
                            height: "250px",
                            cursor: "pointer",
                            overflow: "hidden",
                            borderRadius: "12px",
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                        }}
                        onClick={() => handleClick(index)}
                    >
                        <Icons
                            link={`/recommend/${link}`}
                            icon={icon}
                            text={text}
                            width={selected === index ? "500px" : "250px"}
                            height={"250px"}
                        />
                    </motion.div>
                ))}
            </div>

            {/* Outlet을 사용하여 RecommendBookList를 렌더링 */}
            <div style={{ marginTop: "20px", width: "100%" }}>
                <Outlet />
            </div>
        </div>
    );
};

export default RecommendPage;
