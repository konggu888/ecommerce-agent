"""硬件能力检测回归测试。"""
import unittest
from unittest.mock import patch

from ad_studio import hardware


class HardwareDetectionTests(unittest.TestCase):
    def test_ffmpeg_encoder_detection_uses_word_boundaries(self):
        ffmpeg_output = """
 V..... h264_nvenc           NVIDIA NVENC H.264 encoder
 V..... hevc_nvenc           NVIDIA NVENC HEVC encoder
 V..... fake_h264_nvenc_extra
"""
        with patch.object(hardware.shutil, "which", return_value="/usr/bin/ffmpeg"),              patch.object(hardware, "_run", return_value=ffmpeg_output):
            encoders = hardware._detect_encoders()
        self.assertEqual(encoders, ["h264_nvenc", "hevc_nvenc"])

    def test_hardware_strategy_is_model_agnostic(self):
        profile = hardware.HardwareProfile(
            platform="test",
            cpu="test",
            cpu_cores=8,
            ram_gb=16,
            gpus=[hardware.GPUDevice("Any GPU", "Other", 0, "", "Unknown")],
            accelerator="CPU",
            encoders=[],
            local_ai_level="CPU/云端",
            execution_mode="cloud_first",
        )
        self.assertNotIn("4050", hardware.format_hardware(profile))
        self.assertNotIn("4050", profile.execution_mode)


if __name__ == "__main__":
    unittest.main()
