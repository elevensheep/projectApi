import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./Component/Header";
import MainPage from "./MainPage/MainPage";
import ListPage from "./ListPage/ListPage";
import LoginPage from "./LoginPage/LoginPage";
import MyPage from "./MyPage/MyPage";
import RecommendPage from "./RecommendPage/RecommendPage";
import RecommendBookList from "./RecommendPage/Component/RecommendBookList";
import BookDetail from "./Component/BookDetail";

function App() {
    return (
        <div className="App">
            <BrowserRouter>
                <Header />
                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route path="/list" element={<ListPage />} />
                    <Route path="/books" element={<LoginPage />} />
                    <Route path="/mypage" element={<MyPage />} >
                        <Route path=":isbn" element={<BookDetail />} />
                    </Route>
                    <Route path="/recommend" element={<RecommendPage />}>
                        <Route path=":category" element={<RecommendBookList />} >
                            <Route path=":isbn" element={<BookDetail />} />
                        </Route>
                    </Route>
                </Routes>
            </BrowserRouter>
        </div>
    );
}

export default App;
