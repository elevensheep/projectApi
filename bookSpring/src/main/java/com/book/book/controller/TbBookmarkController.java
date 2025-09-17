package com.book.book.controller;

import com.book.book.dto.BookDto;
import com.book.book.entity.TbBook;
import com.book.book.entity.TbBookmark;
import com.book.book.entity.TbUser;
import com.book.book.repository.TbBookRepository;
import com.book.book.repository.TbBookmarkRepository;
import com.book.book.repository.TbUserRepository;
import com.book.book.service.TbBookService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/bookmarks")
public class TbBookmarkController {
    private final TbUserRepository tbUserRepository;
    private final TbBookRepository tbBookRepository;
    private final TbBookmarkRepository tbBookmarkRepository;
    private final TbBookService tbBookService;

    @Operation(
            summary = "ISBN으로 북마크 추가",
            description = "사용자가 특정 ISBN의 책을 북마크에 추가합니다. 요청 본문에 ISBN 문자열만 전달받습니다. (예: \"9788920930720\")",
            responses = {
                    @ApiResponse(responseCode = "200", description = "북마크 추가 성공"),
                    @ApiResponse(responseCode = "401", description = "로그인이 필요함"),
            }
    )
    @PostMapping("{isbn}")
    public ResponseEntity<?> addBookMark(
            @RequestBody String isbn,
            Authentication authentication
    ) {
        // 사용자 인증 정보 확인
        String userUuid = (String) authentication.getPrincipal();
        if (userUuid == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }

        // JSON 문자열로 들어온 ISBN에서 따옴표 제거
        final String cleanIsbn = isbn.replaceAll("\"", "").trim();

        // 도서 조회
        TbBook book = tbBookRepository.findByBookIsbn(cleanIsbn)
                .orElseThrow(() -> new RuntimeException(cleanIsbn + "에 해당하는 도서를 찾을 수 없습니다."));

        // 사용자 조회
        TbUser user = tbUserRepository.findByUserUuid(userUuid)
                .orElseThrow(() -> new RuntimeException("해당 사용자가 존재하지 않습니다."));

        Long userId = user.getUserId();

        // 중복 북마크 체크
        boolean isAlreadyBookmarked = tbBookmarkRepository.findByBookBookIsbnAndUserUserId(cleanIsbn, userId).isPresent();
        if (isAlreadyBookmarked) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body("이미 북마크된 책입니다.");
        }

        // 북마크 저장
        TbBookmark bookmark = new TbBookmark();
        bookmark.setBook(book);
        bookmark.setUser(user);
        tbBookmarkRepository.save(bookmark);

        return ResponseEntity.ok("북마크에 추가되었습니다.");
    }



    // 북마크 리스트
    @Operation(
            summary = "회원별 북마크 조회",
            description = "회원의 UUID를 기반으로 해당 회원이 추가한 북마크 목록을 전체 조회합니다.",
            responses = {
                    @ApiResponse(responseCode = "200", description = "회원 북마크 목록 반환"),
                    @ApiResponse(responseCode = "404", description = "해당 회원을 찾을 수 없음")
            }
    )
    @GetMapping("")
    public ResponseEntity<?> getBookmarks(Authentication authentication) {
        // 인증된 사용자 UUID 가져오기
        String userUuid = (String) authentication.getPrincipal();
        System.out.println("getBookmarks uuid: " + userUuid);

        Optional<TbUser> userOpt = tbUserRepository.findByUserUuid(userUuid);
        if (!userOpt.isPresent()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("해당 사용자를 찾을 수 없습니다.");
        }

        Long userId = userOpt.get().getUserId();

        // 전체 북마크 리스트 조회
        List<TbBookmark> bookmarks = tbBookmarkRepository.findAllByUserUserId(userId);
        if (bookmarks.isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }

        // 북마크에서 도서 목록 추출
        List<TbBook> books = bookmarks.stream()
                .map(TbBookmark::getBook)
                .distinct()
                .collect(Collectors.toList());

        // 도서를 BookDto로 변환
        List<BookDto> bookDtoList = tbBookService.getBookDto(books);

        return ResponseEntity.ok(bookDtoList);
    }



    // 북마크 삭제
    @Operation(
            summary = "회원별 북마크 삭제",
            description = "회원이 추가한 북마크 중 특정 ISBN의 도서를 삭제합니다. 요청 본문에 회원 UUID가 필요합니다.",
            responses = {
                    @ApiResponse(responseCode = "200", description = "북마크 삭제 성공"),
                    @ApiResponse(responseCode = "401", description = "로그인이 필요함"),
                    @ApiResponse(responseCode = "404", description = "삭제할 북마크가 존재하지 않음")
            }
    )
    @DeleteMapping("{isbn}")
    @Transactional
    public ResponseEntity<?> deleteBookMark(
            @RequestBody String isbn,
            Authentication authentication) {

        // JWT에서 인증된 사용자 정보 확인
        String userUuid = (String) authentication.getPrincipal();
        if (userUuid == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("로그인이 필요합니다.");
        }

        // 요청 본문에 들어온 ISBN 문자열에서 따옴표 제거
        final String cleanIsbn = isbn.replaceAll("\"", "").trim();

        TbBook book = tbBookRepository.findByBookIsbn(cleanIsbn)
                .orElseThrow(() -> new RuntimeException(cleanIsbn + "에 해당하는 도서를 찾을 수 없습니다."));

        Optional<TbUser> user = tbUserRepository.findByUserUuid(userUuid);
        if (user.isEmpty()) {
            return ResponseEntity.badRequest().body("해당 사용자가 존재하지 않습니다.");
        }

        Long userId = user.get().getUserId();

        Optional<TbBookmark> existingBookmark = tbBookmarkRepository.findByBookBookIsbnAndUserUserId(cleanIsbn, userId);
        if (existingBookmark.isPresent()) {
            tbBookmarkRepository.delete(existingBookmark.get());
            return ResponseEntity.ok("북마크가 삭제되었습니다.");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("북마크가 존재하지 않습니다.");
        }
    }


}
