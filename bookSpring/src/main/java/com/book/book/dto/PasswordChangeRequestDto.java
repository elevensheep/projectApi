package com.book.book.dto;

// 비밀번호 변경 요청 DTO (현재 비밀번호와 새 비밀번호)
public class PasswordChangeRequestDto {
    private String currentPassword;
    private String newPassword;

    public String getCurrentPassword() {
        return currentPassword;
    }
    public void setCurrentPassword(String currentPassword) {
        this.currentPassword = currentPassword;
    }
    public String getNewPassword() {
        return newPassword;
    }
    public void setNewPassword(String newPassword) {
        this.newPassword = newPassword;
    }
}