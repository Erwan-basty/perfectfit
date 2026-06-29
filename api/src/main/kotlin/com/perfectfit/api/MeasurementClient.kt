package com.perfectfit.api

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
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
    private val http = OkHttpClient()
    private val json = jacksonObjectMapper()

    fun measure(frontImage: MultipartFile, sideImage: MultipartFile, heightCm: Double): Measurements {
        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "front_image",
                frontImage.originalFilename ?: "front.jpg",
                frontImage.bytes.toRequestBody("image/jpeg".toMediaType()),
            )
            .addFormDataPart(
                "side_image",
                sideImage.originalFilename ?: "side.jpg",
                sideImage.bytes.toRequestBody("image/jpeg".toMediaType()),
            )
            .addFormDataPart("height_cm", heightCm.toString())
            .build()

        val request = Request.Builder()
            .url("$serviceUrl/measure")
            .post(body)
            .build()

        val response = http.newCall(request).execute()
        val responseBody = response.body?.string()
            ?: throw IllegalStateException("Measurement service returned an empty response")

        if (!response.isSuccessful) {
            throw IllegalStateException("Measurement service error ${response.code}: $responseBody")
        }

        return json.readValue(responseBody)
    }
}
