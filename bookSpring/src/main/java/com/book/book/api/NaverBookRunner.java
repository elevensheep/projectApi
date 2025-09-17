package com.book.book.api;

import com.book.book.dto.IsbnWithCategoryDto;
import com.book.book.dto.NaverApiDto;
import com.book.book.entity.TbBook;
import com.book.book.repository.TbBookRepository;
import com.book.book.service.LibraryApiService;
import com.book.book.service.NaverBookService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Component
public class NaverBookRunner implements CommandLineRunner {

    private final LibraryApiService libraryApiService;
    private final NaverBookService naverBookService;
    private final TbBookRepository tbBookRepository;

    @Autowired
    public NaverBookRunner(NaverBookService naverBookService, TbBookRepository tbBookRepository, LibraryApiService libraryApiService) {
        this.naverBookService = naverBookService;
        this.tbBookRepository = tbBookRepository;
        this.libraryApiService = libraryApiService;
    }

    @Override
    public void run(String... args) {
        // Library API에서 recomisbn 목록을 동기적으로 가져옴
        List<IsbnWithCategoryDto> isbnWithCategoryDtoList = libraryApiService.getRecomisbn().block();

        if (isbnWithCategoryDtoList != null && !isbnWithCategoryDtoList.isEmpty()) {
            System.out.println("📚 추천된 ISBN 목록:");
            isbnWithCategoryDtoList.forEach(dto ->
                    System.out.println(" - ISBN: " + dto.getRecomIsbn() + ", 카테고리: " + dto.getDrCodeName()));
        } else {
            System.out.println("❌ 추천된 ISBN이 없습니다.");
            return;
        }

        // 각 ISBN이 13자 이상이면 13자리로 자르기
        List<IsbnWithCategoryDto> processedDtoList = isbnWithCategoryDtoList.stream()
                .flatMap(dto -> Arrays.stream(dto.getRecomIsbn().split("\\s+"))
                        .map(String::trim)
                        .filter(isbn -> isbn.length() == 13)  // 정확히 13자리인 경우만 사용
                        .map(isbn -> new IsbnWithCategoryDto(isbn, dto.getDrCodeName()))
                )
                .collect(Collectors.toList());

        // 처리된 ISBN 목록 출력
        List<String> processedIsbnList = processedDtoList.stream()
                .map(IsbnWithCategoryDto::getRecomIsbn)
                .collect(Collectors.toList());
        System.out.println("📚 NaverBookRunner 처리된 ISBN 목록: " + processedIsbnList);

        if (!processedDtoList.isEmpty()) {
            for (IsbnWithCategoryDto processedDto : processedDtoList) {
                String recomisbn = processedDto.getRecomIsbn();

                // ⭐ ISBN이 이미 존재하는지 확인
                boolean exists = tbBookRepository.existsByBookIsbn(recomisbn);

                if (exists) {
                    System.out.println("🔄 이미 존재하는 책 (ISBN: " + recomisbn + "), 스킵합니다.");
                    continue; // 이미 존재하면 다음 ISBN 처리
                }

                // 각 recomisbn을 이용해 Naver API에서 책 정보를 가져옴
                NaverApiDto naverApiDto = naverBookService.searchBooks(recomisbn).block();

                if (naverApiDto != null
                        && naverApiDto.getChannel() != null
                        && naverApiDto.getChannel().getItems() != null) {

                    // API 결과가 있으면 처리 ： Naver API 결과에서 책 정보를 순회하며 TbBook 엔티티 생성 후 저장
                    naverApiDto.getChannel().getItems().forEach(naverBook -> {
                        String bookCategory = processedDto.getDrCodeName();

                        TbBook book = new TbBook(
                                naverBook.getTitle(),
                                naverBook.getImage(),
                                naverBook.getAuthor(),
                                naverBook.getPublisher(),
                                naverBook.getIsbn(),
                                naverBook.getDescription(),
                                bookCategory  // drCodeName을 bookCategory로 저장
                        );

                        tbBookRepository.save(book);
                        System.out.println("✅ 저장된 책: [" + recomisbn + "] - " + book.getBookTitle());
                    });
                } else {
                    System.out.println("⚠️ Naver API에서 검색된 결과가 없습니다: " + recomisbn);
                }
            }
        } else {
            System.err.println("⚠️ Library API에서 검색된 결과가 없습니다.");
        }
    }
}
