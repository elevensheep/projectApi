package com.book.book.dto;

import lombok.*;

import java.util.List;
// 상세 페이지에 보낼 데이터
@ToString
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class BookWithKeywordsDTO {
    private String bookIsbn;
    private String bookTitle;
    private String bookPublisher;
    private String bookAuthor;
    private String bookImg;
    private String bookDescription;
    private String bookCategory;
    private List<String> keywords; // 키워드를 리스트로 전달
    private List<TbBookStoreDto> bookStores; // 알라딘 매장 정보

    public BookWithKeywordsDTO(String isbn, String title, String publisher, String author,
                               String img, String description, String category, List<String> keywords) {
        this.bookIsbn = isbn;
        this.bookTitle = title;
        this.bookPublisher = publisher;
        this.bookAuthor = author;
        this.bookImg = img;
        this.bookDescription = description;
        this.bookCategory = category;
        this.keywords = keywords;
    }

}