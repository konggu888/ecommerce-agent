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
        with patch("ad_studio.product_parser.urlopen", side_effect=OSError("network disabled")):
            info = parse_product_url("https://item.jd.com/123.html")
        self.assertEqual(info.platform, "京东")
        self.assertFalse(info.fetched)

    def test_product_info_persists(self):
        with tempfile.TemporaryDirectory() as td:
            info = parse_product_url("https://item.jd.com/123.html")
            path = save_product(info, Path(td), "project-test")
            self.assertTrue(path.exists())
            self.assertIn("project-test.json", str(path))


if __name__ == "__main__":
    unittest.main()
