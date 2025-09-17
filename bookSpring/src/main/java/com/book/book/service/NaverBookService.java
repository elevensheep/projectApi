package com.book.book.service;

import com.book.book.dto.NaverApiDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

import java.time.Duration;

@Service
public class NaverBookService {

    private final WebClient webClient;

    @Value("${naver.client.id}")
    private String naverClientId;

    @Value("${naver.client.secret}")
    private String naverClientSecret;

    public NaverBookService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("https://openapi.naver.com/v1/search").build();
    }

    public Mono<NaverApiDto> searchBooks(String query) {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/book_adv.xml")
                        .queryParam("d_isbn", query)
                        .queryParam("display", 10)
                        .queryParam("start", 1)
                        .queryParam("sort", "sim")
                        .build())
                .header("X-Naver-Client-Id", naverClientId)
                .header("X-Naver-Client-Secret", naverClientSecret)
                .accept(MediaType.APPLICATION_XML)  // XML 데이터 요청
                .retrieve()
                .bodyToMono(NaverApiDto.class) // XML 응답을 NaverApiDto로 변환하여 Mono로 반환
                .retryWhen(Retry.backoff(3, Duration.ofSeconds(2)) // 2초 간격으로 최대 3번 재시도
                        .filter(throwable -> throwable instanceof WebClientResponseException.TooManyRequests))
                .onErrorResume(error -> {
                    System.err.println("네이버 API 호출 실패: " + error.getMessage());
                    return Mono.empty(); // 실패 시 빈 Mono 반환
                });
    }

}

