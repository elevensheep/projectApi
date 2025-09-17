package com.book.book.entity;

import jakarta.persistence.*;
import lombok.*;

import java.util.Optional;

@Entity
@Setter
@Getter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@Table(name = "tb_booksmark")
public class TbBookmark {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long bookmarkId;

    @ManyToOne
    @JoinColumn(name = "books_isbn")
    private TbBook book;

    @ManyToOne
    @JoinColumn(name = "users_id")
    private TbUser user;

    public void setUser(TbUser user) {
        this.user = user;
    }
}
