package com.book.book.dto;

import jakarta.xml.bind.annotation.XmlAccessType;
import jakarta.xml.bind.annotation.XmlAccessorType;
import jakarta.xml.bind.annotation.XmlElement;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

@ToString
@Data
@NoArgsConstructor
@AllArgsConstructor
@XmlAccessorType(XmlAccessType.FIELD)

public class TbBookStoreDto {
    @XmlElement(name = "offName", namespace = "http://www.aladin.co.kr/ttb/apiguide.aspx")
    private String offName;

    @XmlElement(name = "link", namespace = "http://www.aladin.co.kr/ttb/apiguide.aspx")
    private String link;
}
