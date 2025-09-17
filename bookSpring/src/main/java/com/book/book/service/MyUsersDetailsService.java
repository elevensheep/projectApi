package com.book.book.service;

import com.book.book.dto.CustomUser;
import com.book.book.entity.TbUser;
import com.book.book.repository.TbUserRepository;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.context.annotation.Bean;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

// DB 유저 정보 꺼내기
// DB에서 동일 아이디의 유저 정보 꺼냄 -> 유저가 제출한 비번과 DB 비번 비교해줌 -> 일치하면 쿠키 생성해서 유저한테 보내줌. 세션도 보내줌
// 스프링 시큐리티는 DB 비번 어딨는지 몰라서 찾아서 줘야됨
@Service
@RequiredArgsConstructor
public class MyUsersDetailsService implements UserDetailsService {

    private final TbUserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String userUuid) throws UsernameNotFoundException {
        System.out.println("받은 userUuid: " + userUuid);  // userUuid 값 확인

        var result = userRepository.findByUserUuid(userUuid);
        if(result.isEmpty()){
            throw new UsernameNotFoundException(userUuid + "라는 아이디를 찾을 수 없습니다.");
        }
        var user = result.get();
        System.out.println("✅ DB에서 찾은 사용자: " + user);

        // 입력한 비밀번호와 DB의 암호화된 비밀번호 비교 테스트

        // 직접 BCryptPasswordEncoder 객체를 생성
        BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();


        String 입력된_비밀번호 = "1234"; // 테스트용으로 로그인할 때 입력한 값 직접 넣기
        System.out.println("입력된 비밀번호: " + 입력된_비밀번호);
        System.out.println("DB에 저장된 암호화된 비밀번호: " + user.getUserPassword());

        boolean isMatched = passwordEncoder.matches(입력된_비밀번호, user.getUserPassword());
        System.out.println("비밀번호 일치 여부: " + isMatched);

        // 권한 추가 (Spring Security는 "ROLE_" 접두사를 권장)
        List<GrantedAuthority> authorities = new ArrayList<>();
        authorities.add(new SimpleGrantedAuthority("ROLE_USER"));  // 일반 회원 권한

        CustomUser customUser = new CustomUser(user.getUserUuid(), user.getUserPassword(), authorities);
        customUser.setUserNickname(user.getUserNickname());
        System.out.println("✅ 생성된 CustomUser: " + customUser.getUserUuid());

        return customUser;
    }

}
