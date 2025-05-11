import React from "react";
import { useParams, useNavigate, Outlet } from "react-router-dom";
import { motion, LayoutGroup, AnimatePresence } from "framer-motion";
import books from "../../Component/BookDump";
import Book from "../../Component/Book";

const styles = {
    wrapper: {
        display: "grid",
        gridTemplateColumns: "repeat(6, 1fr)",
        gap: "20px",
        padding: "20px",
        maxWidth: "1440px",
        width: "100%",
        margin: "0 auto",
    },
    bookContainer: {
        width: "200px",
        height: "300px",
        cursor: "pointer",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
    },
};

const RecommendBookList = () => {
    const { category } = useParams();
    const navigate = useNavigate();

    const filteredBooks = books.filter((book) => book.category === category);

    return (
        <LayoutGroup>
            <div style={styles.wrapper}>
                {filteredBooks.map((book) => (
                    <motion.div
                        key={book.isbn}
                        layoutId={book.isbn}
                        onClick={() => navigate(`${book.isbn}`)}
                        style={styles.bookContainer}
                    >
                        <Book 
                            bookImg={book.img} 
                            bookTitle={book.title} 
                            bookIsbn={book.isbn} 
                            bookCategory={book.category} 
                        />
                    </motion.div>
                ))}
            </div>

            {/* BookDetail이 애니메이션으로 나타나도록 설정 */}
            <AnimatePresence>
                <Outlet />
            </AnimatePresence>
        </LayoutGroup>
    );
};

export default RecommendBookList;
