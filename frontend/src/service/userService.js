import { apiGet, apiPost } from "./request";

// 로그인 상태 확인
export const checkLoginStatus = () => apiPost("/user/status");

// 마이페이지 조회
export const getMyPage = () => apiGet("/user/mypage");

// 로그인
export const login = (userUuid, userPassword) =>
    apiPost("/user/login", { userUuid, userPassword });

// 로그아웃
export const logout = () => apiPost("/user/logout");

// 회원가입
export const signup = (userData) => apiPost("/user/signup", userData);
