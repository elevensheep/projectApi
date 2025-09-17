package com.book.book.entity;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.*;

import java.util.List;

@Entity
@Setter
@Getter
@ToString(exclude = {"keywords", "recommendations"}) // 순환 참조 가능 필드 제외
@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode(onlyExplicitlyIncluded = true) // 키워드랑 매핑할 때 중복제거 하려고 넣은 거임
@Table(name = "tb_books")
public class TbBook {
    @Id
    @Column(name = "books_isbn")
    @EqualsAndHashCode.Include
    private String bookIsbn; // ISBN

    @Column(name="books_title")
    private String bookTitle;

    @Column(name = "books_publisher")
    private String bookPublisher;

    @Column(name = "books_author")
    private String bookAuthor;

    @Column(name = "books_img")
    private String bookImg;


    @Column(name = "books_description", columnDefinition = "TEXT")
    @Lob // 대용량 텍스트 데이터임을 명시
    private String bookDescription;

    @Column(name = "books_category")
    private String bookCategory;

    // 책은 여러 키워드를 가질 수 있음. 데이터를 조회할 때, @OneToMany : TbBook을 조회하고 해당 책의 키워드를 함께 포함시키는 방법
    @OneToMany(mappedBy = "book", fetch = FetchType.LAZY)  // Lazy loading 적용
    @JsonManagedReference  // 직렬화의 주체로 설정
    private List<TbBookKeyword> keywords;

    // TbBook과 TbRecommend(중간 엔티티) 간의 1:N 관계
    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL)
    private List<TbRecommend> recommendations;


    public TbBook(String title, String image, String author, String publisher, String isbn, String description, String bookCategory) {
        this.bookTitle = title;
        this.bookImg = image;
        this.bookAuthor = author;
        this.bookPublisher = publisher;
        this.bookIsbn = isbn;
        this.bookDescription = description;
        this.bookCategory = bookCategory;
    }

}
