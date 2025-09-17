package com.book.book.config;


import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfiguration {

    @Bean
    public GroupedOpenApi publicApi() {
        return GroupedOpenApi.builder()
                .group("public")
                .packagesToScan("com.book.book")  // Swagger가 스캔할 패키지 설정
                .pathsToMatch("/**")  // 모든 경로에 대해 Swagger 문서화
                .build();
    }
}