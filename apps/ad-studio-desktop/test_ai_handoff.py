import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md"
AGENTS = ROOT / "AGENTS.md"
LOGIC = ROOT / "apps" / "ad-studio-desktop" / "PROJECT_LOGIC.md"
HELP = ROOT / "apps" / "ad-studio-desktop" / "HELP.md"
PLAN = ROOT / "docs" / "AD_STUDIO_ACCEPTANCE_PLAN.md"


class AIHandoffTests(unittest.TestCase):
    def test_a32_history_blind_ai_can_recover_required_project_context(self):
        handoff = HANDOFF.read_text(encoding="utf-8")
        agents = AGENTS.read_text(encoding="utf-8")
        logic = LOGIC.read_text(encoding="utf-8")
        help_doc = HELP.read_text(encoding="utf-8")
        plan = PLAN.read_text(encoding="utf-8")

        required_handoff_sections = (
            "## 1. 项目目标",
            "## 2. 架构与强制规则",
            "## 3. 当前验收进度",
            "## 4. 验收计划",
            "## 5. 测试入口",
            "## 6. 安全边界",
            "## 7. 新 AI 的固定接手顺序",
        )
        for section in required_handoff_sections:
            self.assertIn(section, handoff)

        self.assertIn("已完成：A0–A31；当前阶段：A32 · AI 接手能力；下一阶段：A33", handoff)
        for entry in ("AGENTS.md", "PROJECT_LOGIC.md", "HELP.md", "AD_STUDIO_ACCEPTANCE_PLAN.md", "test_ai_handoff.py"):
            self.assertIn(entry, handoff)

        self.assertIn("LLM 负责思考和决策", agents)
        self.assertIn("当前已知限制", help_doc)
        self.assertIn("验收入口与 AI 接手地图", logic)
        self.assertIn("## A32 · AI接手能力", plan)
        self.assertIn("## A33 · 完整用户流程", plan)

        for required in (HANDOFF, AGENTS, LOGIC, HELP, PLAN):
            self.assertTrue(required.exists(), required)


if __name__ == "__main__":
    unittest.main()