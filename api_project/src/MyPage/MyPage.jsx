import React, { useState } from "react";
import { Link } from "react-router-dom";
import Book from "../Component/Book.jsx";
import "./MyPage.css";

const mockUser = {
  id: "whffu",
  nickname: "졸려",
};

const mockBookmarks = [
  { isbn: "9788932035338", title: "Title", author: "저자", category: "경제", cover: "https://contents.kyobobook.co.kr/sih/fit-in/400x0/pdt/9788936480615.jpg" },
  { isbn: "2", title: "Title", author: "저자", category: "경제", cover: "https://contents.kyobobook.co.kr/sih/fit-in/400x0/pdt/9788936480615.jpg" },
  { isbn: "3", title: "Title", author: "저자", category: "스포츠", cover: "https://contents.kyobobook.co.kr/sih/fit-in/400x0/pdt/9788936480615.jpg" },
  { isbn: "4", title: "Title", author: "저자", category: "사회", cover: "https://contents.kyobobook.co.kr/sih/fit-in/400x0/pdt/9788936480615.jpg" },
  { isbn: "5", title: "Title", author: "저자", category: "세계", cover: "https://contents.kyobobook.co.kr/sih/fit-in/400x0/pdt/9788936480615.jpg" },
];

const categories = ["ALL", "경제", "스포츠", "사회", "세계"];

const MyPage = () => {
  const [selectedCategory, setSelectedCategory] = useState("ALL");

  const filteredBooks =
    selectedCategory === "ALL"
      ? mockBookmarks
      : mockBookmarks.filter((book) => book.category === selectedCategory);

  return (
    <div className="mypage">
      <div className="profile">
        <div className="profile-image" />
        <div>
          <p><strong>ID:</strong> {mockUser.id}</p>
          <p><strong>닉네임:</strong> {mockUser.nickname}</p>
        </div>
      </div>

      <div className="bookmark-section">
        <h2>북마크</h2>
        <div className="category-buttons">
          {categories.map((cat) => (
            <button
              key={cat}
              className={selectedCategory === cat ? "selected" : ""}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="bookmark-grid">
          {filteredBooks.map((book) => (
            <Link to={`/mypage/${book.isbn}`} key={book.isbn} className="bookmark-card">
              <Book
                bookIsbn={book.isbn}
                bookImg={book.cover}
                bookAlt={book.title}
                bookTitle={book.title}
              />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MyPage;
