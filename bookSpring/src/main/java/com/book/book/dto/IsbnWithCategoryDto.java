package com.book.book.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class IsbnWithCategoryDto {
    private String recomIsbn;  // ISBN
    private String drCodeName; // 카테고리 (drCodeName)
}
