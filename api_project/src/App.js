import './App.css';
import Header from './Component/Header'
import MyPage from './MyPage/MyPage';
import ListPage from './ListPage/ListPage';
import LoginPage from './LoginPage/LoginPage';
import MainPage from './MainPage/MainPage';
import RecommendPage from './RecommendPage/RecommendPage';
function App() {
  return (
    <div className="App">
      <Router>
        <Header/>
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/list" element={<ListPage />} />
          <Route path="/books" element={<LoginPage />} />
          <Route path='/mypage' element={<MyPage />} />
          <Route path='/Recommend' element={<RecommendPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
