package com.book.book.repository;

import com.book.book.entity.TbBookKeyword;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TbBookKeywordRepository extends JpaRepository<TbBookKeyword, Long> {
    List<TbBookKeyword> findByBookKeyword(String bookKeyword);

    List<TbBookKeyword> findByBookKeywordIdIn(List<Long> bookKeywordIds);

    Page<TbBookKeyword> findByBookKeyword(String keyword, Pageable pageable);


}
