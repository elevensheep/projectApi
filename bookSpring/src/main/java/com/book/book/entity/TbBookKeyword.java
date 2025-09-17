package com.book.book.entity;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.*;
import com.book.book.entity.*;

@Entity
@Setter
@Getter
@ToString(exclude = "book")
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "tb_booksKeyword")
public class TbBookKeyword {
    @Id
    @Column(name = "booksKeyword_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long bookKeywordId;

    @Column(name = "booksKeyword_keyword")
    private String bookKeyword;

    // 각 키워드는 하나의 책에만 속하지만, 하나의 책은 여러 개의 키워드를 가질 수 있는 구조
    @ManyToOne
    @JoinColumn(name = "books_isbn")
    @JsonBackReference  // 직렬화 시 제외
    private TbBook book; // isbn
}
