package com.book.book.repository;

import com.book.book.entity.TbNewsKeyword;
import io.micrometer.common.KeyValues;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import reactor.core.publisher.Flux;

import java.time.LocalDate;
import java.util.List;

public interface TbNewsKeywordRepository extends JpaRepository<TbNewsKeyword, Integer> {
    // newsDate 컬럼에 맞게 날짜로 조회 (예: LocalDate 변환 또는 DATE 타입 컬럼)
    List<TbNewsKeyword> findAllByNewsDate(LocalDate newsDate);

    // 3) 특정 isbn에 해당하는 뉴스만 조회 (tb_recommend 조인)
    @Query("SELECT r.newsKeyword FROM TbRecommend r WHERE r.book.bookIsbn = :isbn")
    List<TbNewsKeyword> findAllByBooksIsbn(@Param("isbn") String isbn);

    List<TbNewsKeyword> findByNewsCategory(String newsCategory);
}
