import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ad_studio.product_parser import parse_product_url, save_product


class ProductParserTests(unittest.TestCase):
    def test_invalid_url_is_safe(self):
        info = parse_product_url("not-a-url")
        self.assertFalse(info.fetched)
        self.assertIn("有效", info.error)

    def test_platform_detection_without_network(self):
        with patch("ad_studio.product_parser.urlopen", side_effect=OSError("network disabled")), \
             patch(
                 "ad_studio.product_parser.fetch_with_browser_skill",
                 return_value={"ok": False, "error": "browser disabled"},
             ):
            info = parse_product_url("https://item.jd.com/123.html")
        self.assertEqual(info.platform, "京东")
        self.assertFalse(info.fetched)

    def test_browser_skill_fallback(self):
        with patch("ad_studio.product_parser.urlopen", side_effect=OSError("blocked")), \
             patch(
                 "ad_studio.product_parser.fetch_with_browser_skill",
                 return_value={
                     "ok": True,
                     "name": "测试商品",
                     "description": "动态页面商品描述",
                     "price": "39.9",
                     "images": ["https://example.com/a.jpg"],
                 },
             ):
            info = parse_product_url("https://item.jd.com/123.html")
        self.assertTrue(info.fetched)
        self.assertEqual(info.source, "browser_skill")
        self.assertEqual(info.name, "测试商品")
        self.assertEqual(info.price, "39.9")

    def test_product_info_persists_without_network(self):
        with tempfile.TemporaryDirectory() as td, \
             patch("ad_studio.product_parser.urlopen", side_effect=OSError("network disabled")), \
             patch(
                 "ad_studio.product_parser.fetch_with_browser_skill",
                 return_value={"ok": False, "error": "browser disabled"},
             ):
            info = parse_product_url("https://item.jd.com/123.html")
            path = save_product(info, Path(td), "project-test")
            self.assertTrue(path.exists())
            self.assertIn("project-test.json", str(path))


if __name__ == "__main__":
    unittest.main()
