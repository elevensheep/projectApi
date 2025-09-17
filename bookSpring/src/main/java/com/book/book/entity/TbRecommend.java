package com.book.book.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Setter
@Getter
@ToString(exclude = "books")
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "tb_recommend")
public class TbRecommend {

    // 뉴스 키워드랑 책 키워드 매핑용
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long recommendId;

    // TbRecommend와 TbBook 간의 다대일 관계 (여러 추천이 하나의 책에 연결)
    @ManyToOne
    @JoinColumn(name = "books_isbn")
    private TbBook book;

    // TbRecommend와 TbNewsKeyword 간의 다대일 관계 (여러 추천이 하나의 뉴스 키워드에 연결)
    @ManyToOne
    @JoinColumn(name = "news_id")
    private TbNewsKeyword newsKeyword;

    // 유사도 점수 필드 추가
    @Column(name = "similarity_score")
    private Double similarityScore;

}
