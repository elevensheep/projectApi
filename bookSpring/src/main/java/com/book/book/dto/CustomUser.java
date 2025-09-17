package com.book.book.dto;

import lombok.Getter;
import lombok.Setter;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.User;

import java.util.Collection;

// 유저정보 커스터마이징
@Getter
@Setter
public class CustomUser extends User {
    private String userUuid;
    private String userNickname;

    public CustomUser(String userUuid, String password, Collection<? extends GrantedAuthority> authorities) {
        super(userUuid, password, authorities);
        this.userUuid = userUuid;
    }

}