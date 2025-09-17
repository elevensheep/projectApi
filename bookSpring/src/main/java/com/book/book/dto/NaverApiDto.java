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
@XmlRootElement(name = "rss")
@XmlAccessorType(XmlAccessType.FIELD)
public class NaverApiDto {

    @XmlElement(name = "channel")
    private Channel channel;

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @XmlAccessorType(XmlAccessType.FIELD)
    public static class Channel {

        @XmlElement(name = "item")
        private List<Item> items;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @XmlAccessorType(XmlAccessType.FIELD)
    public static class Item {

        @XmlElement(name = "title")
        private String title;

        @XmlElement(name = "image")
        private String image;

        @XmlElement(name = "author")
        private String author;

        @XmlElement(name = "publisher")
        private String publisher;

        @XmlElement(name = "isbn")
        private String isbn;

        @XmlElement(name = "description")
        private String description;
    }
}
