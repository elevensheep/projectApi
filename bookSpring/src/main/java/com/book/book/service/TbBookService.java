package com.book.book.service;

import com.book.book.dto.BookDetailDto;
import com.book.book.dto.BookDto;
import com.book.book.dto.TbBookStoreResponseDto;
import com.book.book.entity.TbBook;
import com.book.book.entity.TbBookKeyword;
import com.book.book.entity.TbNewsKeyword;
import com.book.book.repository.TbBookRepository;
import com.book.book.repository.TbNewsKeywordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class TbBookService {
    private final TbBookRepository tbBookRepository;
    private final TbBookStoreService tbBookStoreService;
    private final TbNewsKeywordRepository tbNewsKeywordRepository;

    /**
     * 제목으로 도서 검색 (페이징 포함)
     */
    public Page<BookDto> searchBooksByTitle(String search, Pageable pageable) {
        log.debug("제목으로 도서 검색 - 검색어: {}, 페이지: {}", search, pageable);
        Page<TbBook> books = tbBookRepository.findByBookTitleContainingIgnoreCase(search, pageable);
        return books.map(BookDto::new);
    }

    /**
     * 카테고리별 도서 조회
     */
    public Page<BookDto> getBooksByCategory(String category, Pageable pageable) {
        log.debug("카테고리별 도서 조회 - 카테고리: {}, 페이지: {}", category, pageable);
        Page<TbBook> books = tbBookRepository.findAllByBookCategory(category, pageable);
        return books.map(BookDto::new);
    }

    /**
     * ISBN으로 도서 상세 정보 조회 (비동기 처리)
     */
    public Mono<ResponseEntity<BookDetailDto>> getBookDetailDtoByIsbn(String isbn) {
        log.debug("ISBN으로 도서 상세 정보 조회 시작 - ISBN: {}", isbn);
        
        return Mono.justOrEmpty(tbBookRepository.findByBookIsbn(isbn))
                .switchIfEmpty(Mono.error(new RuntimeException("ISBN " + isbn + "에 해당하는 도서를 찾을 수 없습니다.")))
                .flatMap(tbBook -> {
                    log.debug("도서 정보 조회 완료 - ISBN: {}, 제목: {}", isbn, tbBook.getBookTitle());
                    
                    // BookDetailDto 생성
                    BookDetailDto bookDetailDto = BookDetailDto.builder()
                            .bookIsbn(tbBook.getBookIsbn())
                            .bookTitle(tbBook.getBookTitle())
                            .bookPublisher(tbBook.getBookPublisher())
                            .bookAuthor(tbBook.getBookAuthor())
                            .bookImg(tbBook.getBookImg())
                            .bookDescription(tbBook.getBookDescription())
                            .bookCategory(tbBook.getBookCategory())
                            .build();

                    // 비동기적으로 서점 정보 가져오기
                    Mono<TbBookStoreResponseDto> bookStoreMono = tbBookStoreService.fetchBookStores(isbn)
                            .doOnNext(bookStoreResponse -> 
                                log.debug("서점 정보 조회 완료 - ISBN: {}, 서점 수: {}", 
                                    isbn, 
                                    bookStoreResponse.getItemOffStoreList() != null ? 
                                        bookStoreResponse.getItemOffStoreList().size() : 0))
                            .doOnError(error -> 
                                log.error("서점 정보 조회 실패 - ISBN: {}, 오류: {}", isbn, error.getMessage()));

                    // 동기적으로 반환되는 뉴스 데이터를 Mono로 감싸기
                    Mono<List<TbNewsKeyword>> newsMono = Mono.fromCallable(() -> 
                            tbNewsKeywordRepository.findAllByBooksIsbn(isbn))
                            .subscribeOn(Schedulers.boundedElastic())
                            .doOnNext(newsList -> 
                                log.debug("뉴스 키워드 조회 완료 - ISBN: {}, 키워드 수: {}", isbn, newsList.size()))
                            .doOnError(error -> 
                                log.error("뉴스 키워드 조회 실패 - ISBN: {}, 오류: {}", isbn, error.getMessage()));

                    // 두 Mono를 병합하여 DTO 생성
                    return Mono.zip(bookStoreMono, newsMono)
                            .map(tuple -> {
                                TbBookStoreResponseDto bookStoreResponse = tuple.getT1();
                                List<TbNewsKeyword> newsList = tuple.getT2();

                                if (bookStoreResponse.getItemOffStoreList() != null) {
                                    bookDetailDto.setBookStores(bookStoreResponse.getItemOffStoreList());
                                } else {
                                    log.warn("서점 정보가 null입니다 - ISBN: {}", isbn);
                                }
                                bookDetailDto.setNewsList(newsList);
                                
                                log.info("도서 상세 정보 생성 완료 - ISBN: {}", isbn);
                                return ResponseEntity.ok(bookDetailDto);
                            })
                            .onErrorResume(error -> {
                                log.error("도서 상세 정보 생성 중 오류 발생 - ISBN: {}, 오류: {}", isbn, error.getMessage());
                                return Mono.just(ResponseEntity.status(500).build());
                            });
                });
    }

    /**
     * Page<TbBook>을 Page<BookDto>로 변환
     */
    public Page<BookDto> getBookDto(Page<TbBook> bookPage) {
        return bookPage.map(tb -> new BookDto(
                tb.getBookIsbn(),
                tb.getBookTitle(),
                tb.getBookPublisher(),
                tb.getBookAuthor(),
                tb.getBookImg(),
                tb.getBookDescription(),
                tb.getBookCategory()
        ));
    }

    /**
     * List<TbBook>을 List<BookDto>로 변환
     */
    public List<BookDto> getBookDto(List<TbBook> bookList) {
        return bookList.stream()
                .map(tb -> new BookDto(
                        tb.getBookIsbn(),
                        tb.getBookTitle(),
                        tb.getBookPublisher(),
                        tb.getBookAuthor(),
                        tb.getBookImg(),
                        tb.getBookDescription(),
                        tb.getBookCategory()
                ))
                .collect(Collectors.toList());
    }

    /**
     * ISBN으로 도서와 키워드 정보 조회
     */
    public TbBook getBookWithKeywords(String isbn) {
        log.debug("도서와 키워드 정보 조회 - ISBN: {}", isbn);
        Optional<TbBook> bookOpt = tbBookRepository.findByBookIsbn(isbn);
        
        if (bookOpt.isEmpty()) {
            log.warn("도서를 찾을 수 없음 - ISBN: {}", isbn);
            throw new RuntimeException("ISBN " + isbn + "에 해당하는 도서를 찾을 수 없습니다.");
        }
        
        TbBook book = bookOpt.get();
        log.debug("도서와 키워드 정보 조회 완료 - ISBN: {}, 키워드 수: {}", 
            isbn, book.getKeywords() != null ? book.getKeywords().size() : 0);
        
        return book;
    }

    /**
     * ISBN 리스트로 도서 목록 조회
     */
    public Page<BookDto> getBooksByIsbnList(List<String> isbnList, Pageable pageable) {
        log.debug("ISBN 리스트로 도서 조회 - ISBN 개수: {}, 페이지: {}", isbnList.size(), pageable);
        Page<TbBook> books = tbBookRepository.findByBookIsbnIn(isbnList, pageable);
        return books.map(BookDto::new);
    }

    /**
     * 모든 도서 조회 (페이징 포함)
     */
    public Page<BookDto> getAllBooks(Pageable pageable) {
        log.debug("전체 도서 조회 - 페이지: {}", pageable);
        Page<TbBook> books = tbBookRepository.findAll(pageable);
        return books.map(BookDto::new);
    }
}
