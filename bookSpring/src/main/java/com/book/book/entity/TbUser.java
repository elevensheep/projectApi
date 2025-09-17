package com.book.book.entity;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.security.core.GrantedAuthority;

import java.util.List;

@Entity
@Setter
@Getter
@ToString
@AllArgsConstructor
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL) // null 값이면 JSON 응답에서 제외
@Table(name = "tb_users")
public class TbUser {

    @Id
    @Column(name = "users_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Schema(description = "사용자 ID (자동 생성, 입력 불필요)", accessMode = Schema.AccessMode.READ_ONLY) // Swagger 기본값 null
    private Long userId;

    @Column(name ="user_uuid", unique = true, nullable = false)
    private String userUuid; // 아이디

    @Column(name = "users_nickname", unique = true, nullable = false)
    private String userNickname;  // 별명

    @Column(name ="users_password", nullable = false)
    private String userPassword;

//    @OneToMany(mappedBy = "user")
//    private List<TbBookmark> bookmarks;  // 사용자가 만든 모든 북마크를 가져오기 위한 리스트
}
