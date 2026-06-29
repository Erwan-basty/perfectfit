package com.perfectfit.api

import org.springframework.data.jpa.repository.JpaRepository

interface ProfileRepository : JpaRepository<Profile, Long> {
    fun findByShareCode(shareCode: String): Profile?
}
