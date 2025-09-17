package com.book.book.controller;
// 책 추천 및 조회

import com.book.book.dto.BookDto;
import com.book.book.entity.TbBook;
import com.book.book.entity.TbBookKeyword;
import com.book.book.repository.TbBookKeywordRepository;
import com.book.book.repository.TbNewsKeywordRepository;
import com.book.book.service.PaginationService;
import com.book.book.service.TbBookService;
import com.book.book.service.TbRecommendService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/recommend")
@RequiredArgsConstructor
public class TbRecommendController {

        private final TbRecommendService tbRecommendService;
        private final TbBookKeywordRepository tbBookKeywordRepository;
        private final TbBookService tbBookService;
        private final PaginationService paginationService;

        // 뉴스 키워드 기반 도서 추천
        @Operation(summary = "뉴스 키워드 기반 도서 추천", description = "사용자가 선택한 뉴스 키워드를 기반으로 관련 도서를 추천합니다.\n"
                        + "검색어는 도서 키워드와 매핑되어 있으며, 관련 도서의 제목, 이미지, 저자, 출판사, 출판일, ISBN, 설명 및 추천 키워드가 반환됩니다.", responses = {
                                        @ApiResponse(responseCode = "200", description = "추천 도서 목록 반환"),
                                        @ApiResponse(responseCode = "404", description = "해당 키워드에 해당하는 도서가 없음")
                        })
        @GetMapping("/keyword/{keyword}")
        public ResponseEntity<?> recommendBooksByKeyword(
                        @Parameter(description = "검색할 뉴스 키워드", example = "정치") @PathVariable String keyword,
                        @RequestParam(defaultValue = "0") int page, // 기본 0페이지 (첫 번째 페이지)
                        @RequestParam(defaultValue = "20") int size) {

                // Pageable 객체 생성
                Pageable pageable = PageRequest.of(page, size);
                // repository 메서드를 페이지네이션 버전으로 호출
                Page<TbBookKeyword> bookKeywordsPage = tbBookKeywordRepository.findByBookKeyword(keyword, pageable);

                // TbBookKeyword → TbBook 추출 (중복 제거)
                List<TbBook> books = bookKeywordsPage.getContent().stream()
                                .map(TbBookKeyword::getBook)
                                .distinct()
                                .collect(Collectors.toList());

                // List<TbBook>를 Page<TbBook>로 변환 (페이지 정보 유지)
                Page<TbBook> bookPage = new PageImpl<>(books, pageable, bookKeywordsPage.getTotalElements());

                // Page<TbBook>를 Page<BookDto>로 변환 (페이지 정보 유지)
                Page<BookDto> bookDtoPage = tbBookService.getBookDto(bookPage);

                // PaginationService를 통해 페이징 정보를 포함한 응답 Map 구성
                Map<String, Object> response = paginationService.createPaginatedResponse(bookDtoPage);

                return ResponseEntity.ok(response);
        }

        // /books/recommend/news/date/{date}, ISO 표준 형식(예: "YYYY-MM-DD")으로 파싱되거나 포맷팅
        // 특정 날짜의 뉴스 키워드 기반 도서 추천
        @Operation(summary = "해당 날짜에 등록된 뉴스 키워드 기반 도서 추천", description = "입력된 날짜에 등록된 뉴스 키워드를 기반으로 도서를 추천합니다.", responses = {
                        @ApiResponse(responseCode = "200", description = "추천 도서 목록 반환"),
                        @ApiResponse(responseCode = "404", description = "해당 날짜에 등록된 뉴스 키워드가 없거나 추천 도서가 없음")
        })
        @GetMapping("/news/date/{date}")
        public ResponseEntity<?> recommendBooksByDate(
                        @Parameter(description = "검색할 날짜 (YYYY-MM-DD 형식)", example = "2025-03-17") @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
                        @RequestParam(defaultValue = "0") int page, // 기본 0페이지 (첫 번째 페이지)
                        @RequestParam(defaultValue = "20") int size) {

                // Pageable 객체 생성
                Pageable pageable = PageRequest.of(page, size);

                // 서비스 메서드를 Pageable 인자를 사용하도록 호출하여 Page<BookDto>를 반환받음
                Page<BookDto> bookDtoPage = tbRecommendService.getRecommendedBooksByDate(date, pageable);

                if (bookDtoPage.isEmpty()) {
                        return ResponseEntity.notFound().build();
                }

                // PaginationService를 통해 페이징 정보를 포함한 응답 Map 생성
                Map<String, Object> response = paginationService.createPaginatedResponse(bookDtoPage);

                return ResponseEntity.ok(response);

        }

        @Operation(summary = "뉴스 카테고리 기반 도서 추천", description = "뉴스 카테고리에 해당하는 키워드 기반 추천 도서를 페이징 형태로 반환합니다.", responses = {
                        @ApiResponse(responseCode = "200", description = "추천 도서 반환"),
                        @ApiResponse(responseCode = "404", description = "추천 도서 없음")
        })
        @GetMapping("/category/{category}")
        public ResponseEntity<?> recommendBooksByCategory(
                        @PathVariable String category,
                        @RequestParam(defaultValue = "0") int page,
                        @RequestParam(defaultValue = "20") int size) {
                Pageable pageable = PageRequest.of(page, size);
                Page<BookDto> bookDtoPage = tbRecommendService.getRecommendedBooksByNewsCategory(category, pageable);

                if (bookDtoPage.isEmpty()) {
                        return ResponseEntity.status(404).body("추천 도서가 없습니다.");
                }

                Map<String, Object> response = paginationService.createPaginatedResponse(bookDtoPage);
                return ResponseEntity.ok(response);
        }

}
