package com.perfectfit.api

import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile

data class ScanResponse(
    val shareCode: String,
    val measurements: MeasurementsResponse,
)

data class MeasurementsResponse(
    val shoulderWidthCm: Double?,
    val armLengthCm: Double?,
    val insideLegCm: Double?,
    val waistCircCm: Double?,
    val chestCircCm: Double?,
)

@RestController
class ScanController(
    private val measurementClient: MeasurementClient,
    private val profileRepository: ProfileRepository,
    private val shareCodeGenerator: ShareCodeGenerator,
) {
    @PostMapping("/scans", consumes = ["multipart/form-data"])
    fun scan(
        @RequestParam frontImage: MultipartFile,
        @RequestParam sideImage: MultipartFile,
        @RequestParam heightCm: Double,
    ): ResponseEntity<ScanResponse> {
        val measurements = measurementClient.measure(frontImage, sideImage, heightCm)

        val shareCode = generateUniqueCode()

        val profile = profileRepository.save(
            Profile(
                shareCode = shareCode,
                heightCm = heightCm,
                shoulderWidthCm = measurements.shoulder_width_cm,
                armLengthCm = measurements.arm_length_cm,
                insideLegCm = measurements.inside_leg_cm,
                waistCircCm = measurements.waist_circ_cm,
                chestCircCm = measurements.chest_circ_cm,
            )
        )

        return ResponseEntity.ok(
            ScanResponse(
                shareCode = profile.shareCode,
                measurements = MeasurementsResponse(
                    shoulderWidthCm = profile.shoulderWidthCm,
                    armLengthCm = profile.armLengthCm,
                    insideLegCm = profile.insideLegCm,
                    waistCircCm = profile.waistCircCm,
                    chestCircCm = profile.chestCircCm,
                ),
            )
        )
    }

    private fun generateUniqueCode(): String {
        repeat(10) {
            val code = shareCodeGenerator.generate()
            if (profileRepository.findByShareCode(code) == null) return code
        }
        throw IllegalStateException("Could not generate a unique share code after 10 attempts")
    }
}
