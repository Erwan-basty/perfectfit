package com.perfectfit.api

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import java.time.Instant

@Entity
data class Profile(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(unique = true, nullable = false)
    val shareCode: String,

    val heightCm: Double,

    // Measurements in cm — null if the service couldn't compute them
    val shoulderWidthCm: Double? = null,
    val armLengthCm: Double? = null,
    val insideLegCm: Double? = null,
    val waistCircCm: Double? = null,
    val chestCircCm: Double? = null,

    val createdAt: Instant = Instant.now(),
)
