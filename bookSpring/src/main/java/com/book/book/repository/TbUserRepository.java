package com.book.book.repository;

import com.book.book.entity.TbUser;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TbUserRepository extends JpaRepository<TbUser, Integer> {

    Optional<TbUser> findByUserUuid(String userUuid);
}
