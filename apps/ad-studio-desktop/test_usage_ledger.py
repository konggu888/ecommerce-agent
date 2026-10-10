from __future__ import annotations

import ast
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from ad_studio.usage_ledger import UsageLedger


class UsageLedgerRetentionTests(unittest.TestCase):
    def test_keeps_history_beyond_2000_rows_and_summarizes_all_project_costs(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "usage-ledger.json"
            existing = [
                {
                    "id": f"historical-{index}",
                    "project_id": "project-a",
                    "status": "success",
                    "estimated_cost_rmb": 0.01,
                    "category": "video",
                    "total_tokens": 0,
                }
                for index in range(2000)
            ]
            ledger_path.write_text(json.dumps(existing), encoding="utf-8")
            ledger = UsageLedger(ledger_path)

            ledger.record(
                function="video generation",
                model_id="",
                model_name="test provider",
                provider="test provider",
                model="",
                status="success",
                estimated_cost_rmb=0.02,
                project_id="project-a",
                category="video",
            )

            saved = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved), 2001)
            self.assertEqual(saved[0]["id"], "historical-0")
            self.assertEqual(saved[-1]["estimated_cost_rmb"], 0.02)

            summary = ledger.project_summary("project-a")
            self.assertEqual(summary["entries"], 2001)
            self.assertEqual(summary["success"], 2001)
            self.assertAlmostEqual(summary["actual_cost_rmb"], 20.02, places=6)
            self.assertAlmostEqual(summary["by_category"]["video"], 20.02, places=6)

    def test_all_entries_returns_full_history_newest_first(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "usage-ledger.json"
            ledger_path.write_text(json.dumps([
                {"id": f"row-{index}", "project_id": "p", "status": "success"}
                for index in range(2001)
            ]), encoding="utf-8")
            ledger = UsageLedger(ledger_path)
            entries = ledger.all_entries()
            self.assertEqual(len(entries), 2001)
            self.assertEqual(entries[0]["id"], "row-2000")
            self.assertEqual(entries[-1]["id"], "row-0")

    def test_cost_ledger_ui_shows_full_model_and_production_histories_separately(self):
        app_path = Path(__file__).parent / "ad_studio" / "app.py"
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        app_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App")
        method = next(node for node in app_class.body if isinstance(node, ast.FunctionDef) and node.name == "usage_view")
        method_source = ast.get_source_segment(source, method)
        self.assertIn("self.model_router.ledger.all_entries()", method_source)
        self.assertIn("self.store.ledger.all_entries()", method_source)
        self.assertIn("模型调用记录", method_source)
        self.assertIn("视频/素材生产费用", method_source)
        self.assertIn("当前项目已记录", method_source)
        self.assertIn("不等于供应商最终账单", method_source)


    def test_corrupt_ledger_is_quarantined_instead_of_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "usage-ledger.json"
            damaged_bytes = b'[{broken-json'
            ledger_path.write_bytes(damaged_bytes)
            ledger = UsageLedger(ledger_path)

            ledger.record(
                function="video generation",
                model_id="",
                model_name="test provider",
                provider="test provider",
                model="",
                status="success",
                estimated_cost_rmb=0.03,
                project_id="project-a",
                category="video",
            )

            backups = list(Path(directory).glob("usage-ledger.json.corrupt-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), damaged_bytes)
            self.assertEqual(json.loads(ledger_path.read_text(encoding="utf-8"))[0]["estimated_cost_rmb"], 0.03)
            self.assertIn("原文件已保留", ledger.last_load_warning)

    def test_invalid_ledger_shape_is_preserved_before_new_history_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "usage-ledger.json"
            original = json.dumps({"not": "a list"}, ensure_ascii=False).encode("utf-8")
            ledger_path.write_bytes(original)
            ledger = UsageLedger(ledger_path)

            self.assertEqual(ledger.all_entries(), [])
            backups = list(Path(directory).glob("usage-ledger.json.corrupt-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), original)
            self.assertIn("结构异常", ledger.last_load_warning)

    def test_atomic_write_failure_preserves_existing_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "usage-ledger.json"
            original = json.dumps([{"id": "old", "status": "success"}]).encode("utf-8")
            ledger_path.write_bytes(original)
            ledger = UsageLedger(ledger_path)

            with patch("ad_studio.usage_ledger.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    ledger.record(
                        function="video generation",
                        model_id="",
                        model_name="test provider",
                        provider="test provider",
                        model="",
                        status="success",
                        estimated_cost_rmb=0.03,
                        project_id="project-a",
                        category="video",
                    )

            self.assertEqual(ledger_path.read_bytes(), original)
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
