package com.book.book.service;

import com.book.book.dto.IsbnWithCategoryDto;
import com.book.book.dto.LibraryApiDto;
import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Unmarshaller;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;

import java.io.StringReader;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class LibraryApiService {

    private final WebClient webClient;

    @Value("${openapi.key}")
    private String apiKey;

    public LibraryApiService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
                .baseUrl("https://nl.go.kr/NL/search/openApi")
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create()
                        .responseTimeout(Duration.ofSeconds(60))))
                .exchangeStrategies(ExchangeStrategies.builder()
                        .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(20 * 1024 * 1024)) // 20MB 설정
                        .build())
                .build();
    }

    // IsbnWithCategoryDto를 반환하는 방식으로
    public Mono<List<IsbnWithCategoryDto>> getRecomisbn() {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/saseoApi.do")
                        .queryParam("key", apiKey)
                        .queryParam("startRowNumApi", "1")
                        .queryParam("endRowNumApi", "1300")
                        .build())
                .accept(MediaType.APPLICATION_XML)
                .retrieve()
                .bodyToMono(String.class)  // XML을 String으로 받음
//                .doOnNext(xmlResponse -> System.out.println("응답 받은 XML:\n" + xmlResponse))
                .flatMap(xmlResponse -> {
                    try {
                        LibraryApiDto parsedResponse = parseXml(xmlResponse);
                        // listElements가 null이면 빈 리스트 반환
                        List<IsbnWithCategoryDto> isbnAndDrCodeNames = Optional.ofNullable(parsedResponse.getListElements())
                                .orElse(List.of())
                                .stream()
                                // 각 ListElement의 items를 평탄화
                                .flatMap(listElem -> Optional.ofNullable(listElem.getItems())
                                        .orElse(List.of())
                                        .stream())
                                // 🔥 ISBN이 없으면 제외
                                .filter(item -> item.getRecomIsbn() != null && !item.getRecomIsbn().isBlank())
                                // IsbnWithCategoryDto로 매핑
                                .map(item -> new IsbnWithCategoryDto(
                                        item.getRecomIsbn(),
                                        (item.getDrCodeName() == null || item.getDrCodeName().isBlank()) ? "미분류" : item.getDrCodeName()))
                                .collect(Collectors.toList());

                        return Mono.just(isbnAndDrCodeNames);
                    } catch (JAXBException e) {
                        e.printStackTrace();
                        return Mono.error(e);
                    }
                });
    }

    private LibraryApiDto parseXml(String xmlResponse) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(LibraryApiDto.class);
        Unmarshaller unmarshaller = context.createUnmarshaller();
        return (LibraryApiDto) unmarshaller.unmarshal(new StringReader(xmlResponse));
    }
}
