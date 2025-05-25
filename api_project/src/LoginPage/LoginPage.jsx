import React, { useState } from 'react';
import "./LoginPage.css";

const LoginPage = () => {
  const [formData, setFormData] = useState({
    id: "",
    password: "",
    remember: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("로그인 정보:", formData);
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>
          로그인하기 위해<br />
          정보를 입력해주세요
        </h2>

        <label>* ID</label>
        <input
          type="text"
          name="id"
          value={formData.id}
          onChange={handleChange}
          required
        />

        <label>* 비밀번호</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
        />

        <div className="remember-checkbox">
          <input
            type="checkbox"
            name="remember"
            checked={formData.remember}
            onChange={handleChange}
          />
          <span>로그인 상태 유지</span>
        </div>

        <button type="submit" className="login-btn">
          로그인
        </button>
      </form>
    </div>
  );
};

export default LoginPage;