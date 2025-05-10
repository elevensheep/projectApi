import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./Component/Header";
import MainPage from "./MainPage/MainPage";
import ListPage from "./ListPage/ListPage";
import LoginPage from "./LoginPage/LoginPage";
import MyPage from "./MyPage/MyPage";
import RecommendPage from "./RecommendPage/RecommendPage";
import RecommendBookList from "./RecommendPage/Component/RecommendBookList";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Header />
        <div>
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/list" element={<ListPage />} />
            <Route path="/books" element={<LoginPage />} />
            <Route path="/mypage" element={<MyPage />} />
            <Route path="/recommend/*" element={<RecommendPage />} />
          </Routes>
        </div>
      </BrowserRouter>
      
    </div>
  );
}

export default App;
