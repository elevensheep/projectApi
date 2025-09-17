package com.book.book.controller;

import com.book.book.dto.BookDto;
import com.book.book.dto.LoginRequestDto;
import com.book.book.dto.MyPageResponseDto;
import com.book.book.entity.TbBook;
import com.book.book.entity.TbBookmark;
import com.book.book.entity.TbUser;
import com.book.book.jwt.JwtUtil;
import com.book.book.repository.TbBookmarkRepository;
import com.book.book.repository.TbUserRepository;
import com.book.book.service.TbBookService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/user")
public class TbUserController {
    private final TbUserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManagerBuilder authenticationManagerBuilder;
    private final TbBookmarkRepository tbBookmarkRepository;
    private final TbBookService tbBookService;

    @Operation(summary = "로그인", description = "사용자 로그인 처리")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "로그인 성공"),
        @ApiResponse(responseCode = "401", description = "인증 실패")
    })
    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequestDto request,
            HttpServletResponse response) {
        try {
            log.info("로그인 시도: {}", request.getUserUuid());
            
            // 아이디/비밀번호로 인증 객체 생성
            var authToken = new UsernamePasswordAuthenticationToken(
                    request.getUserUuid(), request.getUserPassword());

            // 아이디/비밀번호를 DB와 비교하여 로그인
            var auth = authenticationManagerBuilder.getObject().authenticate(authToken);

            // 인증 정보 저장
            SecurityContextHolder.getContext().setAuthentication(auth);

            var jwt = JwtUtil.createToken(SecurityContextHolder.getContext().getAuthentication());
            log.debug("JWT 토큰 생성 완료");

            // JWT를 쿠키에 저장
            Cookie jwtCookie = new Cookie("jwt", jwt);
            jwtCookie.setHttpOnly(true);
            jwtCookie.setPath("/");
            jwtCookie.setSecure(false);
            jwtCookie.setMaxAge(60 * 60 * 24); // 1일
            response.addCookie(jwtCookie);

            response.setHeader("Set-Cookie", "jwt=" + jwt + "; Path=/; HttpOnly; SameSite=Lax; Secure=false");

            log.info("로그인 성공: {}", request.getUserUuid());
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "로그인 성공",
                    "token", jwt,
                    "userUuid", request.getUserUuid()));
                    
        } catch (AuthenticationException e) {
            log.warn("로그인 실패: {} - {}", request.getUserUuid(), e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                        "success", false,
                        "error", "아이디 또는 비밀번호가 잘못되었습니다."));
        }
    }

    @Operation(summary = "로그아웃", description = "사용자 로그아웃 처리")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "로그아웃 성공")
    })
    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(HttpServletResponse response) {
        log.info("로그아웃 요청");
        
        // JWT 쿠키 삭제
        Cookie jwtCookie = new Cookie("jwt", null);
        jwtCookie.setPath("/");
        jwtCookie.setHttpOnly(true);
        jwtCookie.setMaxAge(0);
        response.addCookie(jwtCookie);

        return ResponseEntity.ok(Map.of(
            "success", true,
            "message", "로그아웃 성공"));
    }

    @Operation(summary = "회원가입", description = "새로운 사용자 회원가입")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "회원가입 성공"),
        @ApiResponse(responseCode = "400", description = "잘못된 요청")
    })
    @PostMapping("/signup")
    public ResponseEntity<Map<String, Object>> signup(@RequestBody TbUser tbUser) {
        try {
            log.info("회원가입 시도: {}", tbUser.getUserUuid());
            
            // 중복 사용자 확인
            if (userRepository.findByUserUuid(tbUser.getUserUuid()).isPresent()) {
                log.warn("중복 사용자 회원가입 시도: {}", tbUser.getUserUuid());
                return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", "이미 존재하는 사용자입니다."));
            }

            var hashPassword = passwordEncoder.encode(tbUser.getUserPassword());
            tbUser.setUserPassword(hashPassword);

            userRepository.save(tbUser);
            log.info("회원가입 성공: {}", tbUser.getUserUuid());

            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "회원가입이 완료되었습니다."));
                
        } catch (Exception e) {
            log.error("회원가입 중 오류 발생: {}", e.getMessage(), e);
            return ResponseEntity.badRequest().body(Map.of(
                "success", false,
                "error", "회원가입 중 오류가 발생했습니다."));
        }
    }

    @Operation(summary = "로그인 상태 확인", description = "현재 사용자의 로그인 상태 확인")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "로그인 상태"),
        @ApiResponse(responseCode = "401", description = "로그인되지 않음")
    })
    @PostMapping("/status")
    public ResponseEntity<Map<String, Object>> checkLoginStatus(
            @CookieValue(name = "jwt", required = false) String jwtToken) {
        
        if (jwtToken == null || jwtToken.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                        "success", false,
                        "error", "로그인되어 있지 않습니다."));
        }

        try {
            String userUuid = JwtUtil.getUserUuidFromToken(jwtToken);
            Optional<TbUser> userOpt = userRepository.findByUserUuid(userUuid);
            
            if (userOpt.isEmpty()) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of(
                            "success", false,
                            "error", "존재하지 않는 사용자입니다."));
            }

            return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "로그인 상태입니다.",
                "userUuid", userUuid));
                
        } catch (Exception e) {
            log.warn("토큰 검증 실패: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                        "success", false,
                        "error", "유효하지 않은 토큰입니다."));
        }
    }

    @Operation(summary = "마이페이지 조회", description = "사용자 정보와 북마크된 도서 목록 조회")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "마이페이지 정보 반환"),
        @ApiResponse(responseCode = "404", description = "사용자를 찾을 수 없음")
    })
    @GetMapping("/mypage")
    public ResponseEntity<Map<String, Object>> mypage(Authentication authentication) {
        try {
            String userUuid = (String) authentication.getPrincipal();
            log.info("마이페이지 조회: {}", userUuid);
            
            Optional<TbUser> userOpt = userRepository.findByUserUuid(userUuid);
            if (userOpt.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of(
                        "success", false,
                        "error", "해당 사용자를 찾을 수 없습니다."));
            }

            TbUser user = userOpt.get();
            Long userId = user.getUserId();

            // 북마크된 도서 조회
            List<TbBookmark> bookmarkedBooks = tbBookmarkRepository.findAllByUserUserId(userId);
            List<TbBook> books = bookmarkedBooks.stream()
                    .map(TbBookmark::getBook)
                    .distinct()
                    .collect(Collectors.toList());

            List<BookDto> bookDtoList = tbBookService.getBookDto(books);
            MyPageResponseDto responseDto = new MyPageResponseDto(user, bookDtoList);

            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", responseDto));
                
        } catch (Exception e) {
            log.error("마이페이지 조회 중 오류 발생: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of(
                    "success", false,
                    "error", "마이페이지 조회 중 오류가 발생했습니다."));
        }
    }
}
