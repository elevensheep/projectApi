package com.book.book.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import com.book.book.entity.TbBook;
import java.util.List;
// 추천 할 때 보낼 데이터

@Data
@AllArgsConstructor
@NoArgsConstructor
public class BookDto {
    private String bookIsbn;
    private String bookTitle;
    private String bookPublisher;
    private String bookAuthor;
    private String bookImg;
    private String bookDescription;
    private String bookCategory;

    // TbBook을 받아서 BookDto로 변환하는 생성자 추가
    public BookDto(TbBook tbBook) {
        this.bookIsbn = tbBook.getBookIsbn();
        this.bookTitle = tbBook.getBookTitle();
        this.bookPublisher = tbBook.getBookPublisher();
        this.bookAuthor = tbBook.getBookAuthor();
        this.bookImg = tbBook.getBookImg();
        this.bookDescription = tbBook.getBookDescription();
        this.bookCategory = tbBook.getBookCategory();
    }
}
