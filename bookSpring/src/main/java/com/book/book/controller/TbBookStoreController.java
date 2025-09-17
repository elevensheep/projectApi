package com.book.book.controller;

import com.book.book.dto.BookIsbnRequest;
import com.book.book.dto.TbBookStoreResponseDto;
import com.book.book.service.TbBookStoreService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/bookstores")
@RequiredArgsConstructor
public class TbBookStoreController {

    private final TbBookStoreService bookStoreService;

    // POST /api/bookstores
    @PostMapping
    public Mono<TbBookStoreResponseDto> getBookStoresByIsbn(@RequestBody BookIsbnRequest request) {
        return bookStoreService.fetchBookStores(request.getIsbn());
    }
}
