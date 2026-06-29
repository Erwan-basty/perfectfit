package com.perfectfit.api

import org.springframework.stereotype.Component

private val CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" // no I/O/1/0 to avoid confusion

@Component
class ShareCodeGenerator {
    fun generate(): String {
        fun segment() = (1..4).map { CHARS.random() }.joinToString("")
        return "PF-${segment()}-${segment()}"
    }
}
