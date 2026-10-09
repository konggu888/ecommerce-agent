from __future__ import annotations

import json
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
