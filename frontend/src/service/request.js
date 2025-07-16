// src/api/request.js
import axios from "axios";

// 공통 axios 인스턴스
const api = axios.create({
    baseURL: "http://localhost:8080/api/",
    withCredentials: true,
});

// 공통 GET
export const apiGet = async (url, config = {}) => {
    try {
        const res = await api.get(url, config);
        return res.data;
    } catch (error) {
        throw error.response?.data || { error: "요청 실패 (GET)" };
    }
};
 
// 공통 POST
export const apiPost = async (url, body = {}, config = {}) => {
    try {
        const res = await api.post(url, body, config);
        return res.data;
    } catch (error) {
        throw error.response?.data || { error: "요청 실패 (POST)" };
    }
};
