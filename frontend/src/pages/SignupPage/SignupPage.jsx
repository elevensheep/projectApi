import React, { useState } from 'react';
import "./SignupPage.css";

function SignupPage() {
  const [formData, setFormData] = useState({
    id: "",
    nickname: "",
    password: "",
    confirmPassword: "",
    agree: false,
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
    console.log("가입 정보:", formData);
  };

  return (
    <div className="signup-container">
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>
          회원 가입을 위해<br />
          정보를 입력해주세요
        </h2>

        <label>* ID</label>
        <input type="text" name="id" value={formData.id} onChange={handleChange} required />
        
        <label>* 닉네임</label>
        <input type="text" name="nickname" value={formData.nickname} onChange={handleChange} required />

        <label>* 비밀번호</label>
        <input type="password" name="password" value={formData.password} onChange={handleChange} required />

        <label>* 비밀번호 확인</label>
        <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} required />

        <div className="agree-checkbox">
          <input type="checkbox" name="agree" checked={formData.agree} onChange={handleChange} />
          <span>이용약관 개인정보 수집 및 이용, 마케팅 활용 선택에 모두 동의합니다.</span>
        </div>

        <button type="submit" className="signup-btn">가입하기</button>
      </form>
    </div>
  );
}

export default SignupPage
