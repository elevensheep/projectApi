package com.book.book.dto;

import com.book.book.entity.TbBook;
import com.book.book.entity.TbUser;

import java.util.List;

public class MyPageResponseDto {
    private TbUser user;
    private List<BookDto> books;

    public MyPageResponseDto(TbUser user, List<BookDto> books) {
        this.user = user;
        this.books = books;
    }

    public TbUser getUser() {
        return user;
    }

    public void setUser(TbUser user) {
        this.user = user;
    }

    public List<BookDto> getBooks() {
        return books;
    }

    public void setBooks(List<BookDto> books) {
        this.books = books;
    }
}
