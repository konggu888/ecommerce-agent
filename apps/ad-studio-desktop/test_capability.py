"""本地/云端能力调度（CapabilityRouter）单元测试。

全部通过临时目录 + 注入 fake probe 完成，不发起真实网络请求。
"""
import json
import tempfile
import unittest
from pathlib import Path

from ad_studio.capability import CapabilityRouter, ExecutionDecision, is_local_endpoint, probe_http
from ad_studio.hardware import GPUDevice, HardwareProfile


def make_hardware(execution_mode: str = "local_first") -> HardwareProfile:
    return HardwareProfile(
        platform="Linux",
        cpu="test-cpu",
        cpu_cores=8,
        ram_gb=16.0,
        gpus=[GPUDevice(name="Test GPU", vendor="test", vram_mb=4096)],
        accelerator="test",
        encoders=["h264_nvenc"],
        local_ai_level="medium",
        execution_mode=execution_mode,
    )


def make_root() -> Path:
    return Path(tempfile.mkdtemp(prefix="cap-test-"))


def write_json(root: Path, name: str, data: dict):
    (root / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class CapabilityRouterTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()

    def router(self, mode="local_first", probe=None, hardware=None):
        return CapabilityRouter(self.root, hardware=hardware or make_hardware(mode), probe=(probe or (lambda url: False)))

    # ---- LLM ----
    def test_llm_prefers_local_model(self):
        write_json(self.root, "model-config.json", {"models": [
            {"id": "local1", "provider": "local_openai", "enabled": True},
            {"id": "cloud1", "provider": "openai_compatible", "api_key": "sk-x"},
        ]})
        d = self.router().decide_llm()
        self.assertEqual(d.target, "local")
        self.assertIn("local1", d.reason)

    def test_llm_falls_back_to_cloud(self):
        write_json(self.root, "model-config.json", {"models": [
            {"id": "cloud1", "provider": "openai_compatible", "api_key": "sk-x"},
        ]})
        d = self.router().decide_llm()
        self.assertEqual(d.target, "cloud")

    def test_llm_cloud_first_prefers_cloud_when_ready(self):
        write_json(self.root, "model-config.json", {"models": [
            {"id": "local1", "provider": "local_openai", "enabled": True},
            {"id": "cloud1", "provider": "openai_compatible", "api_key": "sk-x"},
        ]})
        d = self.router(mode="cloud_first").decide_llm()
        self.assertEqual(d.target, "cloud")

    def test_llm_unavailable(self):
        d = self.router().decide_llm()
        self.assertEqual(d.target, "unavailable")

    # ---- Asset ----
    def test_asset_local_when_reachable(self):
        write_json(self.root, "asset-generation.json", {"演员": {"endpoint": "http://127.0.0.1:7860/sdapi/v1/txt2img"}})
        d = self.router(probe=lambda url: url.startswith("http://127.0.0.1:7860")).decide_asset("演员")
        self.assertEqual(d.target, "local")
        self.assertIn("127.0.0.1:7860", d.endpoint)

    def test_asset_cloud_when_local_unreachable(self):
        write_json(self.root, "asset-generation.json", {"演员": {"endpoint": "https://api.cloud.example/gen", "api_key": "ak-x"}})
        d = self.router().decide_asset("演员")
        self.assertEqual(d.target, "cloud")

    def test_asset_unavailable(self):
        d = self.router().decide_asset("场景")
        self.assertEqual(d.target, "unavailable")

    def test_asset_nonlocal_endpoint_not_trusted_as_local(self):
        write_json(self.root, "asset-generation.json", {"商品素材": {"endpoint": "https://api.example.com/gen"}})
        d = self.router(probe=lambda url: True).decide_asset("商品素材")
        self.assertEqual(d.target, "unavailable")

    def test_asset_cloud_first_ignores_local(self):
        write_json(self.root, "asset-generation.json", {"演员": {"endpoint": "http://127.0.0.1:7860/sdapi/v1/txt2img"}})
        write_json(self.root, "asset-generation.json", {"演员": {"endpoint": "https://api.cloud.example/gen", "api_key": "ak-x"}})
        d = self.router(mode="cloud_first", probe=lambda url: True).decide_asset("演员")
        self.assertEqual(d.target, "cloud")

    # ---- Video ----
    def test_video_local_when_reachable(self):
        write_json(self.root, "video-provider.json", {"video_provider": {"endpoint": "http://127.0.0.1:8188/"}})
        d = self.router(probe=lambda url: url.startswith("http://127.0.0.1:8188")).decide_video()
        self.assertEqual(d.target, "local")

    def test_video_cloud_when_local_unreachable(self):
        write_json(self.root, "video-provider.json", {"video_provider": {"endpoint": "https://api.video.example/generate", "api_key": "vk-x"}})
        d = self.router().decide_video()
        self.assertEqual(d.target, "cloud")

    def test_video_unavailable(self):
        d = self.router().decide_video()
        self.assertEqual(d.target, "unavailable")

    # ---- hint from config.json local_capability ----
    def test_asset_uses_local_capability_hint(self):
        write_json(self.root, "config.json", {"local_capability": {"asset_endpoint": "http://127.0.0.1:7860/sdapi/v1/txt2img"}})
        d = self.router(probe=lambda url: "127.0.0.1:7860" in url).decide_asset("演员")
        self.assertEqual(d.target, "local")

    # ---- helpers ----
    def test_is_local_endpoint(self):
        self.assertTrue(is_local_endpoint("http://127.0.0.1:7860"))
        self.assertTrue(is_local_endpoint("http://localhost:8188"))
        self.assertTrue(is_local_endpoint("local:pipe"))
        self.assertFalse(is_local_endpoint("https://api.example.com"))
        self.assertFalse(is_local_endpoint(""))

    def test_probe_http(self):
        self.assertFalse(probe_http(""))
        self.assertFalse(probe_http("http://127.0.0.1:1/"))  # 端口1几乎必然失败

    def test_snapshot_shape(self):
        write_json(self.root, "model-config.json", {"models": [{"id": "cloud1", "provider": "openai_compatible", "api_key": "sk-x"}]})
        snap = self.router().snapshot()
        self.assertEqual(len(snap), 3)
        for row in snap:
            self.assertIn(row["task"], ("llm", "asset", "video"))
            self.assertIn(row["target"], ("local", "cloud", "unavailable"))


if __name__ == "__main__":
    unittest.main()
