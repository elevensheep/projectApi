package com.book.book.jwt;

import com.book.book.dto.CustomUser;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.stream.Collectors;

@Component
public class JwtUtil {

    static final SecretKey key =
            Keys.hmacShaKeyFor(Decoders.BASE64.decode(
                    "jwtpassword123jwtpassword123jwtpassword123jwtpassword123jwtpassword"));

    // ✅ JWT 생성
    public static String createToken(Authentication auth){
        CustomUser customUser = (CustomUser) auth.getPrincipal();
        System.out.println("createToken customUser.getUserUuid(): " + customUser.getUserUuid());

        var authorities = auth.getAuthorities().stream()
                .map(a -> a.getAuthority())
                .collect(Collectors.joining(","));

        String jwt = Jwts.builder()
                .subject(customUser.getUserUuid())
                .claim("userUuid", customUser.getUserUuid())
                .claim("userNickname", customUser.getUserNickname())
                .claim("roles", authorities)
                .issuedAt(new Date(System.currentTimeMillis()))
                .expiration(new Date(System.currentTimeMillis() + 3600000))  // 1시간 유효
                .signWith(key)
                .compact();

        return jwt;
    }

    // ✅ 전체 Claims 추출
    public static Claims extractToken(String token){
        Claims claims = Jwts.parser().verifyWith(key).build()
                .parseClaimsJws(token).getPayload();
        return claims;
    }

    // ✅ UUID 추출만
    public static String getUserUuidFromToken(String token) {
        try {
            Claims claims = Jwts.parser()
                    .setSigningKey(key)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();

            return claims.getSubject();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    // ✅ 로그인 상태 확인용 (UUID + 만료 체크 포함)
    public static String validateAndGetUserUuid(String token) {
        try {
            Claims claims = Jwts.parser()
                    .setSigningKey(key)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();

            if (claims.getExpiration().before(new Date())) {
                return null;
            }

            return claims.getSubject();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    // ✅ 유효성만 검사
    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .setSigningKey(key)
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
