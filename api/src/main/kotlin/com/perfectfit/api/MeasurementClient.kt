package com.perfectfit.api

import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.ByteArrayResource
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.util.LinkedMultiValueMap
import org.springframework.web.client.RestClient
import org.springframework.web.multipart.MultipartFile

data class Measurements(
    val shoulder_width_cm: Double? = null,
    val arm_length_cm: Double? = null,
    val inside_leg_cm: Double? = null,
    val waist_circ_cm: Double? = null,
    val chest_circ_cm: Double? = null,
)

@Component
class MeasurementClient(
    @Value("\${measurement.service-url}") private val serviceUrl: String,
) {
    private val client = RestClient.create()

    fun measure(frontImage: MultipartFile, sideImage: MultipartFile, heightCm: Double): Measurements {
        val body = LinkedMultiValueMap<String, Any>().apply {
            add("front_image", namedResource(frontImage))
            add("side_image", namedResource(sideImage))
            add("height_cm", heightCm.toString())
        }

        return client.post()
            .uri("$serviceUrl/measure")
            .contentType(MediaType.MULTIPART_FORM_DATA)
            .body(body)
            .retrieve()
            .body(Measurements::class.java)
            ?: throw IllegalStateException("Measurement service returned an empty response")
    }

    private fun namedResource(file: MultipartFile) = object : ByteArrayResource(file.bytes) {
        override fun getFilename() = file.originalFilename ?: "image.jpg"
    }
}
