package com.book.book.dto;

import com.book.book.entity.TbBook;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;
import java.util.stream.Collectors;

@Getter
@Setter
@ToString
public class TbBookDto {
    private int total;  // 📌 API 응답에 있는 total 필드 추가
    private List<Item> items;  // 책 정보 리스트

    // Item 클래스는 API 응답에서 하나의 책 정보를 나타냄
    @Getter
    @Setter
    public static class Item {
        private String title;
        private String link;
        private String author;
        private String publisher;
        private String image;
        private String description;
        private String isbn;
    }

    public List<TbBook> toEntityList() {
        return items.stream()
                .map(item -> {
                    TbBook tbBook = new TbBook();
                    tbBook.setBookTitle(item.getTitle());
                    tbBook.setBookAuthor(item.getAuthor());
                    tbBook.setBookPublisher(item.getPublisher());
                    tbBook.setBookImg(item.getImage());
                    tbBook.setBookDescription(item.getDescription());
                    tbBook.setBookIsbn(item.getIsbn());
                    return tbBook;
                })
                .collect(Collectors.toList());
    }


}