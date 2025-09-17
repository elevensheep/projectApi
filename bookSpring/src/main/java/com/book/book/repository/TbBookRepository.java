package com.book.book.repository;

import com.book.book.entity.TbBook;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.data.domain.Page; // ✅ Page도 함께 import

import java.util.List;
import java.util.Optional;

@Repository
public interface TbBookRepository extends JpaRepository<TbBook, String> {

    List<TbBook> findAllByBookCategory(String category);

    Optional<TbBook> findByBookIsbn(String isbn);

    boolean existsByBookIsbn(String isbn);
    // 책 제목에 검색어가 포함된 도서 찾기
    List<TbBook> findByBookTitleContainingIgnoreCase(String search);

    // 제목 검색 - 페이징 적용
    Page<TbBook> findByBookTitleContainingIgnoreCase(String title, Pageable pageable);

    // 카테고리별 조회 - 페이징 적용
    Page<TbBook> findAllByBookCategory(String category, Pageable pageable);

    Page<TbBook> findByBookIsbnIn(List<String> isbnList, Pageable pageable);
}
