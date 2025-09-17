package com.book.book.dto;

import jakarta.xml.bind.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@XmlRootElement(name = "channel") // XML 최상위 요소
@XmlAccessorType(XmlAccessType.FIELD)
public class LibraryApiDto {

    @XmlElement(name = "totalCount")
    private int totalCount;  // 전체 도서 수

    // XML의 <list> 태그가 여러 번 등장하므로 별도의 ListElement 클래스로 매핑합니다.
    @XmlElement(name = "list")
    private List<ListElement> listElements;

    // drCodeName 매핑 추가

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @XmlAccessorType(XmlAccessType.FIELD)
    public static class ListElement {
        // 각 <list> 내부의 <item> 태그를 List<Item>으로 매핑
        @XmlElement(name = "item")
        private List<Item> items;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @XmlAccessorType(XmlAccessType.FIELD)
    public static class Item {
        // <item> 내부의 <recomisbn> 태그 매핑
        @XmlElement(name = "recomisbn")
        private String recomIsbn;

        // <item> 내부의 <drCodeName> 태그 매핑. 카테고리임
        @XmlElement(name = "drCodeName")
        private String drCodeName;
    }
}
