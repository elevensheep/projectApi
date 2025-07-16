import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./Component/Header";
import MainPage from "./pages/MainPage/MainPage";
import ListPage from "./pages/ListPage/ListPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import MyPage from "./pages/MyPage/MyPage";
import RecommendPage from "./pages/RecommendPage/RecommendPage";
import RecommendBookList from "./pages/RecommendPage/Component/RecommendBookList";
import BookDetail from "./Component/BookDetail";
import SignupPage from "./pages/SignupPage/SignupPage";

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
                    <Route path="/sign" element={<SignupPage />} />
                    <Route path="/login" element={<LoginPage />} />

                </Routes>
            </BrowserRouter>
        </div>
    );
}

export default App;
