package com.book.book.jwt;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class JwtFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        Cookie[] cookies = request.getCookies();
        if (cookies == null){
            filterChain.doFilter(request, response);
            return;
        }

        // 이름이 "jwt"인 쿠키를 발견한 경우, 변수에 저장
        var jwtCookie = "";
        for (int i = 0; i < cookies.length; i++){
            if (cookies[i].getName().equals("jwt")){
                jwtCookie = cookies[i].getValue();
            }
        }
        if (jwtCookie == null) {
            System.out.println("❌ JWT 쿠키 없음");
            filterChain.doFilter(request, response);
            return;
        }
        System.out.println("JwtFilter jwtCookie: " + jwtCookie);

        // 쿠키에서 꺼낸 JWT 유효한지 확인
        Claims claim;
        try {
            // extractToken() 안에 JWT를 입력하면 자동으로 까주는데 유효기간이 만료되거나 이상한 경우엔 에러를 내줄
            claim = JwtUtil.extractToken(jwtCookie);
        } catch (Exception e) {
            System.out.println("유효기간 만료되거나 이상함");
            filterChain.doFilter(request, response);
            return;
        }
        System.out.println("✅ JWT Payload: " + claim);

        // JWT 안에 있는 내용 꺼내기 -> claim.get("displayName").toString()

        // JWT에서 유저 권한 정보 가져오기
        String authoritiesString = claim.get("roles", String.class);
        List<GrantedAuthority> authorities = Arrays.stream(authoritiesString.split(","))
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());

        String userUuid = claim.get("userUuid", String.class);
        if (userUuid == null) {
            System.out.println("❌ userUuid가 JWT에서 없음");
            filterChain.doFilter(request, response);
            return;
        }
        System.out.println("✅ JWT에서 추출한 userUuid: " + userUuid);

        // JWT 문제 없으면 auth 변수에 유저정보 추가
        var authToken = new UsernamePasswordAuthenticationToken(
                userUuid, // 1. Principal (사용자 ID)
                null, // 2. Credentials (비밀번호)
                authorities // 3. 권한 목록
        );

        SecurityContextHolder.getContext().setAuthentication(authToken);

        filterChain.doFilter(request, response);
    }

}