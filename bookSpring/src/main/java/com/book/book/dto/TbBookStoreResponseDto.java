package com.book.book.dto;

import jakarta.xml.bind.annotation.XmlElement;
import jakarta.xml.bind.annotation.XmlElementWrapper;
import jakarta.xml.bind.annotation.XmlRootElement;

import java.util.List;

@XmlRootElement(name = "object", namespace = "http://www.aladin.co.kr/ttb/apiguide.aspx")
public class TbBookStoreResponseDto {

    private List<TbBookStoreDto> itemOffStoreList;

    @XmlElementWrapper(name = "itemOffStoreList", namespace = "http://www.aladin.co.kr/ttb/apiguide.aspx")
    @XmlElement(name = "offStoreInfo", namespace = "http://www.aladin.co.kr/ttb/apiguide.aspx")  // 개별 <offStoreInfo> 요소들을 리스트로 변환해 줌
    public List<TbBookStoreDto> getItemOffStoreList() {
        return itemOffStoreList;
    }

    public void setItemOffStoreList(List<TbBookStoreDto> itemOffStoreList) {
        this.itemOffStoreList = itemOffStoreList;
    }

    @Override
    public String toString() {
        return "TbBookStoreResponseDto{" +
                "itemOffStoreList=" + itemOffStoreList +
                '}';
    }
}
