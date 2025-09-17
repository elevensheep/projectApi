package com.book.book.controller;

import com.book.book.dto.BookDetailDto;
import com.book.book.dto.BookDto;
import com.book.book.service.PaginationService;
import com.book.book.service.TbBookService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/books")
public class TbBookController {
    private final TbBookService tbBookService;
    private final PaginationService paginationService;

    @Operation(summary = "도서 목록 조회", description = "페이징을 지원하는 도서 목록 조회")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "도서 목록 반환"),
        @ApiResponse(responseCode = "204", description = "도서가 없음")
    })
    @GetMapping("")
    public ResponseEntity<Map<String, Object>> bookList(
            @Parameter(description = "페이지 번호 (0부터 시작)", example = "0") 
            @RequestParam(name = "page", defaultValue = "0") int page,
            @Parameter(description = "페이지 크기", example = "20") 
            @RequestParam(name = "size", defaultValue = "20") int size) {

        try {
            log.info("도서 목록 조회 요청 - page: {}, size: {}", page, size);
            
            Pageable pageable = PageRequest.of(page, size);
            Page<BookDto> bookDtoPage = tbBookService.getAllBooks(pageable);

            if (bookDtoPage.isEmpty()) {
                log.info("도서 목록이 비어있음");
                return ResponseEntity.noContent().build();
            }

            Map<String, Object> response = paginationService.createPaginatedResponse(bookDtoPage);
            log.info("도서 목록 조회 완료 - 총 {}개 도서", bookDtoPage.getTotalElements());
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", response));
                
        } catch (Exception e) {
            log.error("도서 목록 조회 중 오류 발생: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of(
                    "success", false,
                    "error", "도서 목록 조회 중 오류가 발생했습니다."));
        }
    }

    @Operation(summary = "도서 검색", description = "제목으로 도서 검색")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "검색 결과 반환"),
        @ApiResponse(responseCode = "404", description = "검색 결과 없음")
    })
    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> search(
            @Parameter(description = "검색할 도서 제목", example = "그림") 
            @RequestParam(name = "search") String search,
            @Parameter(description = "페이지 번호", example = "0") 
            @RequestParam(name = "page", defaultValue = "0") int page,
            @Parameter(description = "페이지 크기", example = "20") 
            @RequestParam(name = "size", defaultValue = "20") int size) {
        
        try {
            log.info("도서 검색 요청 - 검색어: {}, page: {}, size: {}", search, page, size);
            
            Pageable pageable = PageRequest.of(page, size);
            Page<BookDto> bookList = tbBookService.searchBooksByTitle(search, pageable);

            if (bookList.isEmpty()) {
                log.info("검색 결과 없음 - 검색어: {}", search);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of(
                        "success", false,
                        "error", "해당 검색어에 해당하는 도서가 없습니다."));
            }

            Map<String, Object> response = paginationService.createPaginatedResponse(bookList);
            log.info("도서 검색 완료 - 검색어: {}, 결과: {}개", search, bookList.getTotalElements());
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", response));
                
        } catch (Exception e) {
            log.error("도서 검색 중 오류 발생 - 검색어: {}, 오류: {}", search, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of(
                    "success", false,
                    "error", "도서 검색 중 오류가 발생했습니다."));
        }
    }

    @Operation(summary = "카테고리별 도서 조회", description = "특정 카테고리의 도서 목록 조회")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "카테고리별 도서 목록 반환"),
        @ApiResponse(responseCode = "404", description = "해당 카테고리의 도서 없음")
    })
    @GetMapping("/category/{category}")
    public ResponseEntity<Map<String, Object>> searchByCategory(
            @Parameter(description = "조회할 도서 카테고리", example = "인문과학") 
            @PathVariable(name = "category") String category,
            @Parameter(description = "페이지 번호", example = "0") 
            @RequestParam(name = "page", defaultValue = "0") int page,
            @Parameter(description = "페이지 크기", example = "20") 
            @RequestParam(name = "size", defaultValue = "20") int size) {

        try {
            log.info("카테고리별 도서 조회 요청 - 카테고리: {}, page: {}, size: {}", category, page, size);
            
            Pageable pageable = PageRequest.of(page, size);
            Page<BookDto> bookList = tbBookService.getBooksByCategory(category, pageable);

            if (bookList.isEmpty()) {
                log.info("카테고리별 도서 없음 - 카테고리: {}", category);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of(
                        "success", false,
                        "error", "해당 카테고리에 해당하는 도서가 없습니다."));
            }

            Map<String, Object> response = paginationService.createPaginatedResponse(bookList);
            log.info("카테고리별 도서 조회 완료 - 카테고리: {}, 결과: {}개", category, bookList.getTotalElements());
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", response));
                
        } catch (Exception e) {
            log.error("카테고리별 도서 조회 중 오류 발생 - 카테고리: {}, 오류: {}", category, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of(
                    "success", false,
                    "error", "카테고리별 도서 조회 중 오류가 발생했습니다."));
        }
    }

    @Operation(summary = "도서 상세 정보 조회", description = "ISBN으로 도서의 상세 정보 조회")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "도서 상세 정보 반환"),
        @ApiResponse(responseCode = "404", description = "해당 ISBN의 도서가 없음")
    })
    @GetMapping("book/{isbn}")
    public ResponseEntity<Map<String, Object>> getBookDetailsByIsbn(
            @Parameter(description = "검색할 도서의 ISBN 번호", example = "9791188366170") 
            @PathVariable(name = "isbn") String isbn) {

        try {
            log.info("도서 상세 정보 조회 요청 - ISBN: {}", isbn);
            
            ResponseEntity<BookDetailDto> responseEntity = tbBookService.getBookDetailDtoByIsbn(isbn).block();
            
            if (responseEntity == null || responseEntity.getBody() == null) {
                log.warn("도서 상세 정보 없음 - ISBN: {}", isbn);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of(
                        "success", false,
                        "error", "해당 ISBN의 도서를 찾을 수 없습니다."));
            }

            log.info("도서 상세 정보 조회 완료 - ISBN: {}", isbn);
            return ResponseEntity.ok(Map.of(
                "success", true,
                "data", responseEntity.getBody()));
                
        } catch (Exception e) {
            log.error("도서 상세 정보 조회 중 오류 발생 - ISBN: {}, 오류: {}", isbn, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of(
                    "success", false,
                    "error", "도서 상세 정보 조회 중 오류가 발생했습니다."));
        }
    }
}
