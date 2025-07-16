import React, { useState } from "react";
import { Outlet, useNavigate, useSearchParams } from "react-router-dom"; // ✅ 추가
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
        maxHeight: "2500px",
    },
    icons: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        gap: "20px",
    },
};

const iconData = [
    { link: "economic", icon: Economy, text: "경제" },
    { link: "politics", icon: Politics, text: "정치" },
    { link: "sports", icon: Sports, text: "스포츠" },
    { link: "society", icon: Society, text: "사회" },
    { link: "world", icon: World, text: "세계" },
];

const RecommendPage = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams(); // ✅ 현재 쿼리 추출
    const [selected, setSelected] = useState(null);

    const handleClick = (index, link) => {
        setSelected(selected === index ? null : index);

        const dateParam = searchParams.get("news_date");
        const query = dateParam ? `?news_date=${dateParam}` : "";

        navigate(`/recommend/${link}${query}`); // ✅ 날짜 유지하여 이동
    };

    return (
        <div style={styles.wrapper}>
            <h1>추천 도서</h1>

            <div style={styles.icons}>
                {iconData.map(({ link, icon, text }, index) => {
                    const isSelected = selected === index;
                    const width = isSelected ? "500px" : selected !== null ? "200px" : "250px";
                    const transition = {
                        type: "spring",
                        stiffness: 300,
                        damping: 20,
                    };

                    return (
                        <motion.div
                            key={index}
                            layout
                            transition={transition}
                            style={{
                                width,
                                height: "250px",
                                cursor: "pointer",
                                overflow: "hidden",
                                borderRadius: "12px",
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                            }}
                            onClick={() => handleClick(index, link)}
                        >
                            <Icons link={link} icon={icon} text={text} width={width} height={"250px"} />
                        </motion.div>
                    );
                })}
            </div>

            <Outlet />
        </div>
    );
};

export default RecommendPage;
