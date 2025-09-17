package com.book.book.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

@Entity
@Setter
@Getter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "tb_newsKeyword")
public class TbNewsKeyword {

    @Id
    @Column(name = "news_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long newsId;

    private LocalDate newsDate;  // 업데이트한 시간

    private String newsKeyword;

    private String newsCategory;
}
