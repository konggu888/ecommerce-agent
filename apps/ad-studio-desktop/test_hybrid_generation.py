import json
import tempfile
import unittest
from pathlib import Path

from ad_studio.hybrid_generation import execute_configured_video_gap_generation


class HybridGenerationBridgeTests(unittest.TestCase):
    def test_unconfigured_video_provider_never_claims_generation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = execute_configured_video_gap_generation(
                [{"task_id": "GAP-1", "recommended_resolution": "AI补镜头", "generation_allowed": True}],
                config_root=root,
                output_root=root / "out",
                budget_remaining_rmb=10,
            )
            self.assertEqual(result["generated"], 0)
            self.assertIn("不可用", result["provider"])
            self.assertEqual(result["tasks"][0]["status"], "未执行：视频生成能力不可用")

    def test_product_evidence_is_blocked_before_provider_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "video-provider.json").write_text(json.dumps({
                "video_provider": {
                    "endpoint": "https://example.invalid/video",
                    "api_key": "test-key",
                    "cost_per_shot_rmb": 1,
                }
            }), encoding="utf-8")
            # 路由执行层本身先拦截商品证据，因此不会发出网络请求。
            result = execute_configured_video_gap_generation(
                [{
                    "task_id": "GAP-2",
                    "need": "商品特写",
                    "recommended_resolution": "AI补镜头",
                    "generation_allowed": True,
                }],
                config_root=root,
                output_root=root / "out",
                budget_remaining_rmb=10,
            )
            self.assertEqual(result["blocked"], 1)
            self.assertEqual(result["generated"], 0)
            self.assertIn("真实商品证据", result["tasks"][0]["status"])


if __name__ == "__main__":
    unittest.main()
