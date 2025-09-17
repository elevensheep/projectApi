package com.book.book.repository;

import com.book.book.entity.TbBookmark;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface TbBookmarkRepository extends JpaRepository<TbBookmark, Long> {

    Optional<TbBookmark> findByBookBookIsbnAndUserUserId(String bookIsbn, Long userId);

    Page<TbBookmark> findAllByUserUserId(Long userId, Pageable pageable);

    List<TbBookmark> findAllByUserUserId(Long userId);
}
