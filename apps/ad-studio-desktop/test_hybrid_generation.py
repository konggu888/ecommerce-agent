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



    def test_unknown_video_price_blocks_provider_call_without_confirmation(self):
        from unittest.mock import Mock, patch
        from ad_studio.providers import GenericVideoProvider

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "video-provider.json").write_text(json.dumps({
                "video_provider": {
                    "endpoint": "https://example.invalid/video",
                    "api_key": "test-key",
                }
            }), encoding="utf-8")
            provider = GenericVideoProvider(
                endpoint="https://example.invalid/video",
                api_key="test-key",
                cost_price_configured=False,
            )
            provider.generate = Mock(side_effect=AssertionError("provider must not be called"))
            with patch("ad_studio.hybrid_generation._video_provider", return_value=provider):
                result = execute_configured_video_gap_generation(
                    [{"task_id": "UNKNOWN-1", "recommended_resolution": "AI补镜头", "generation_allowed": True}],
                    config_root=root,
                    output_root=root / "out",
                    project_id="p1",
                    budget_remaining_rmb=100,
                )
            self.assertEqual(provider.generate.call_count, 0)
            self.assertEqual(result["generated"], 0)
            self.assertEqual(result["blocked"], 1)
            self.assertIsNone(result["estimated_additional_cost_rmb"])
            self.assertEqual(result["tasks"][0]["cost_status"], "price_missing")

    def test_unknown_video_price_after_confirmation_is_still_recorded_as_unknown(self):
        from unittest.mock import Mock, patch
        from ad_studio.providers import GenericVideoProvider
        from ad_studio.usage_ledger import UsageLedger

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "video-provider.json").write_text(json.dumps({
                "video_provider": {
                    "endpoint": "https://example.invalid/video",
                    "api_key": "test-key",
                }
            }), encoding="utf-8")
            provider = GenericVideoProvider(
                endpoint="https://example.invalid/video",
                api_key="test-key",
                cost_price_configured=False,
            )
            def fake_generate(request):
                request.output.parent.mkdir(parents=True, exist_ok=True)
                request.output.write_bytes(b"fake-video")
                return request.output
            provider.generate = Mock(side_effect=fake_generate)
            with patch("ad_studio.hybrid_generation._video_provider", return_value=provider):
                result = execute_configured_video_gap_generation(
                    [{"task_id": "UNKNOWN-2", "recommended_resolution": "AI补镜头", "generation_allowed": True, "cost_price_confirmed": True}],
                    config_root=root,
                    output_root=root / "out",
                    project_id="p2",
                    budget_remaining_rmb=100,
                )
            self.assertEqual(provider.generate.call_count, 1)
            self.assertEqual(result["generated"], 1)
            self.assertIsNone(result["estimated_additional_cost_rmb"])
            row = UsageLedger(root / "usage-ledger.json").recent(1)[0]
            self.assertEqual(row["cost_status"], "price_missing")
            self.assertEqual(row["estimated_cost_rmb"], 0.0)
            self.assertTrue(UsageLedger(root / "usage-ledger.json").summary()["has_unknown_cost"])



    def test_video_provider_price_configuration_is_fail_safe(self):
        from ad_studio.hybrid_generation import _video_provider

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = {"video_provider": {"endpoint": "https://example.invalid/video", "api_key": "test-key"}}
            (root / "video-provider.json").write_text(json.dumps(config), encoding="utf-8")
            provider = _video_provider(root)
            self.assertFalse(provider.cost_price_configured)

            for invalid_price in (-1, "nan", "inf", "not-a-number"):
                config["video_provider"]["cost_per_shot_rmb"] = invalid_price
                (root / "video-provider.json").write_text(json.dumps(config), encoding="utf-8")
                provider = _video_provider(root)
                self.assertFalse(provider.cost_price_configured, invalid_price)

    def test_explicit_zero_video_price_remains_configured(self):
        from ad_studio.hybrid_generation import _video_provider

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "video-provider.json").write_text(json.dumps({
                "video_provider": {
                    "endpoint": "https://example.invalid/video",
                    "api_key": "test-key",
                    "cost_per_shot_rmb": 0,
                }
            }), encoding="utf-8")
            provider = _video_provider(root)
            self.assertTrue(provider.cost_price_configured)
            self.assertEqual(provider.cost_per_shot_rmb, 0.0)

if __name__ == "__main__":
    unittest.main()
