package com.book.book.service;

import com.book.book.dto.TbBookStoreResponseDto;
import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Unmarshaller;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.StringReader;

@Service
@RequiredArgsConstructor
public class TbBookStoreService {

    private final WebClient.Builder webClientBuilder;

    @Value("${ttb.key}")
    private String ttbKey;

    public Mono<TbBookStoreResponseDto> fetchBookStores(String isbn) {
        String url = "http://www.aladin.co.kr/ttb/api/ItemOffStoreList.aspx"
                + "?TTBKey=" + ttbKey
                + "&itemIdType=ISBN13"
                + "&ItemId=" + isbn
                + "&output=xml";

        return webClientBuilder.build()
                .get()
                .uri(url)
                .retrieve()
                .bodyToMono(String.class)
                .flatMap(xmlResponse -> {
                    if (xmlResponse != null) {
                        System.out.println("API 응답 XML:");
                        System.out.println(xmlResponse);
                        try {
                            System.out.println("Mono.just(parseXml(xmlResponse)) : "+Mono.just(parseXml(xmlResponse)));
                            return Mono.just(parseXml(xmlResponse));
                        } catch (JAXBException e) {
                            return Mono.error(e);
                        }
                    }
                    return Mono.empty();
                });
    }

    // JAXB를 이용해 XML을 DTO로 변환
    private TbBookStoreResponseDto parseXml(String xmlResponse) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(TbBookStoreResponseDto.class);
        Unmarshaller unmarshaller = context.createUnmarshaller();

        // XML 파싱 전 로그 출력
        System.out.println("Parsing XML: " + xmlResponse);
        return (TbBookStoreResponseDto) unmarshaller.unmarshal(new StringReader(xmlResponse));
    }
}
