package com.book.book.controller;

import com.book.book.entity.TbNewsKeyword;
import com.book.book.repository.TbNewsKeywordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequiredArgsConstructor
public class KeywordController {
    private final TbNewsKeywordRepository tbNewsKeywordRepository;

    @GetMapping("/api/keywords/news")
    public ResponseEntity<List<TbNewsKeyword>> news() {
        LocalDate today = LocalDate.now();
        List<TbNewsKeyword> newsList = tbNewsKeywordRepository.findAllByNewsDate(today);

        System.out.println("KeywordController newsList: " + newsList);
        return ResponseEntity.ok(newsList);
    }
}
