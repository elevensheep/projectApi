package com.book.book.service;

import com.book.book.dto.BookDto;
import com.book.book.entity.TbBook;
import com.book.book.entity.TbBookKeyword;
import com.book.book.entity.TbNewsKeyword;
import com.book.book.entity.TbRecommend;
import com.book.book.repository.TbBookKeywordRepository;
import com.book.book.repository.TbNewsKeywordRepository;
import com.book.book.repository.TbRecommendRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

@RequiredArgsConstructor
@Service
public class TbRecommendService {
    private final TbRecommendRepository tbRecommendRepository;
    private final TbNewsKeywordRepository tbNewsKeywordRepository;
    private final TbBookService tbBookService;

    public Page<BookDto> getRecommendedBooksByDate(LocalDate date, Pageable pageable) {
        // 1. 해당 날짜의 뉴스 키워드 조회
        List<TbNewsKeyword> newsList = tbNewsKeywordRepository.findAllByNewsDate(date);
        if (newsList == null || newsList.isEmpty()) {
            return Page.empty(pageable);
        }

        // 2. 뉴스 키워드를 기준으로 TbRecommend을 페이지 단위로 조회
        Page<TbRecommend> recommendationsPage = tbRecommendRepository.findByNewsKeywordIn(newsList, pageable);
        if (recommendationsPage == null || recommendationsPage.isEmpty()) {
            return Page.empty(pageable);
        }

        // 3. TbRecommend에서 연결된 TbBook을 추출, 중복 제거 후 Page<TbBook>로 변환
        List<TbBook> bookList = recommendationsPage.getContent().stream()
                .map(TbRecommend::getBook)
                .distinct()  // TbBook의 equals/hashCode가 ISBN 등으로 구현되어 있어야 함
                .collect(Collectors.toList());

        Page<TbBook> bookPage = new PageImpl<>(bookList, pageable, recommendationsPage.getTotalElements());

        // 4. Page<TbBook>를 Page<BookDto>로 변환하여 반환 (이미 페이지 정보 유지됨)
        return tbBookService.getBookDto(bookPage);


//                recommendationsPage.getContent().stream()
//                .map(TbRecommend::getBook)
//                .distinct()  // TbBook의 equals/hashCode가 ISBN 등으로 구현되어 있어야 함
//                .map(book -> new BookDto(
//                        book.getBookIsbn(),
//                        book.getBookTitle(),
//                        book.getBookPublisher(),
//                        book.getBookAuthor(),
//                        book.getBookImg(),
//                        book.getBookDescription(),
//                        book.getBookCategory()
//                ))
//                .collect(Collectors.toList());

        // 4. 변환된 List를 PageImpl으로 감싸 페이지네이션 정보를 포함하여 반환
//        return new PageImpl<>(bookDtos, pageable, recommendationsPage.getTotalElements());
        // 1. 해당 날짜 뉴스 키워드 조회
//        List<TbNewsKeyword> newsList = tbNewsKeywordRepository.findAllByNewsDate(date);
//        if (newsList == null || newsList.isEmpty()) {
//            return List.of();
//        }
//
//        // 2. 조회된 뉴스 키워드들을 기준으로 TbRecommend 조회
//        // tbRecommendRepository에 아래와 같이 메서드 정의
//        // List<TbRecommend> findByNewsKeywordIn(List<TbNewsKeyword> newsKeywords);
//        List<TbRecommend> recommendations = tbRecommendRepository.findByNewsKeywordIn(newsList);
//        if (recommendations == null || recommendations.isEmpty()) {
//            return List.of();
//        }
//
//        // 3. TbRecommend 에서 연결된 TbBook 추출 -> 중복 제거 -> DTO 변환
//        List<BookDto> books = recommendations.stream()
//                .map(TbRecommend::getBook)
//                .distinct()  // TbBook의 equals/hashCode가 ISBN 기준으로 구현되어 있어야 함
//                .map(book -> {
////                    List<String> keywords = book.getKeywords().stream()
////                            .map(TbBookKeyword::getBookKeyword)
////                            .collect(Collectors.toList());
//                    return new BookDto(
//                            book.getBookIsbn(),
//                            book.getBookTitle(),
//                            book.getBookPublisher(),
//                            book.getBookAuthor(),
//                            book.getBookImg(),
//                            book.getBookDescription(),
//                            book.getBookCategory()
////                            keywords
//                    );
//                })
//                .collect(Collectors.toList());
//
//        return books;
    }

    public Page<BookDto> getRecommendedBooksByNewsCategory(String category, Pageable pageable) {
        // 1. 뉴스 키워드 조회
        List<TbNewsKeyword> newsKeywords = tbNewsKeywordRepository.findByNewsCategory(category);
        if (newsKeywords.isEmpty()) return Page.empty();

        // 2. 추천 도서 조회
        List<TbRecommend> recommends = tbRecommendRepository.findByNewsKeywordIn(newsKeywords);
        if (recommends.isEmpty()) return Page.empty();

        // 3. 도서 중복 제거
        List<TbBook> books = recommends.stream()
                .map(TbRecommend::getBook)
                .distinct()
                .toList();

        // 4. 수동 페이징 처리
        int start = (int) pageable.getOffset();
        int end = Math.min(start + pageable.getPageSize(), books.size());
        List<TbBook> pageContent = books.subList(start, end);
        Page<TbBook> bookPage = new PageImpl<>(pageContent, pageable, books.size());

        // 5. DTO 변환
        return tbBookService.getBookDto(bookPage);
    }

    public List<BookDto> getRecommendedBooksInMain(LocalDate date) {
        // 1. 해당 날짜의 뉴스 키워드 조회
        List<TbNewsKeyword> newsList = tbNewsKeywordRepository.findAllByNewsDate(date);
        if (newsList == null || newsList.isEmpty()) {
            return Collections.emptyList();
        }

        // 2. 뉴스 키워드를 기준으로 추천 도서 조회 (페이징 없이 전체 조회로 변경)
        List<TbRecommend> recommendations = tbRecommendRepository.findAllByNewsKeywordIn(newsList);
        if (recommendations == null || recommendations.isEmpty()) {
            return Collections.emptyList();
        }

        // 3. 추천 항목에서 책 추출하고 중복 제거
        List<TbBook> bookList = recommendations.stream()
                .map(TbRecommend::getBook)
                .filter(Objects::nonNull)
                .distinct()
                .collect(Collectors.toList());

        // 4. TbBook → BookDto 변환
        return tbBookService.getBookDto(bookList);
    }


}
