import React, { useState } from "react";
import { Link } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";

const styles = {
  wrapper: {
    background: "black",
    height: "350px",
    borderRadius: "20px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "20px",
    overflow: "hidden",
    position: "relative",
  },

  container: {
    width: "100%",
    height: "80%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: "20px",
  },

  bannerInfo: {
    alignItems: "center",
    justifyContent: "center",
    display: "flex",
    flexDirection: "column",
    textAlign: "center",
    color: "white",
  },

  img: {
    width: "150px",
    height: "auto",
    borderRadius: "8px",
    objectFit: "contain",
  },

  navBtn: {
    fontSize: "24px",
    backgroundColor: "transparent",
    color: "white",
    border: "none",
    cursor: "pointer",
    width: "30px",
    zIndex: 10,
  },
};

const books = [
  {
    title: "소년이로 <br />(편혜영 소설집)",
    img: "https://shopping-phinf.pstatic.net/main_3243615/32436154262.20221019142158.jpg",
    styles: { backgroundColor: "#222" },
    isbn: "9788932035338",
  },
  {
    title: "82년생 김지영",
    img: "https://shopping-phinf.pstatic.net/main_3246707/32467074651.20231003084626.jpg?type=w300",
    styles: { backgroundColor: "#333" },
    isbn: "9788937473135",
  },
  {
    title: "작별하지 않는다",
    img: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300",
    styles: { backgroundColor: "#444" },
    isbn: "9788954682152",
  },
];

const formatTitle = (title) => {
  return title.split("<br />").map((line, index) => (
    <React.Fragment key={index}>
      {line}
      {index !== title.split("<br />").length - 1 && <br />}
    </React.Fragment>
  ));
};

function Banner() {
  const [index, setIndex] = useState(0);
  const current = books[index];

  const prev = () => setIndex((index - 1 + books.length) % books.length);
  const next = () => setIndex((index + 1) % books.length);

  return (
    <div style={{ ...styles.wrapper, ...current.styles }}>
      <button onClick={prev} style={styles.navBtn}>{"<"}</button>

      <AnimatePresence mode="wait">
        <motion.div
          key={current.isbn}
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.5 }}
          style={styles.container}
        >
          <div style={styles.bannerInfo}>
            <h2>{formatTitle(current.title)}</h2>
            <Link to={`/book/${current.isbn}`} style={{ color: "skyblue" }}>
              책 보러가기
            </Link>
          </div>
          <img src={current.img} alt={current.title} style={styles.img} />
        </motion.div>
      </AnimatePresence>

      <button onClick={next} style={styles.navBtn}>{">"}</button>
    </div>
  );
}

export default Banner;
