package com.book.book.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Schema(description = "로그인 요청 정보")
public class LoginRequestDto {
    @Schema(description = "사용자 UUID", example = "user1")
    private String userUuid;

    @Schema(description = "사용자 비밀번호", example = "password1")
    private String userPassword;
}
