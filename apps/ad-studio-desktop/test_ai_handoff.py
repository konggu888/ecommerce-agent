import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md"
SESSION_HANDOFF = ROOT / "docs" / "SESSION_HANDOFF.md"
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
        session_handoff = SESSION_HANDOFF.read_text(encoding="utf-8")

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

        self.assertIn("已完成：A0–A33。", handoff)
        self.assertIn("B1–B3 真实投放相关阶段按用户要求暂缓", handoff)
        self.assertIn("docs/AI_AD_STUDIO_FUTURE_FEATURE_MEMO.md", handoff)
        for entry in ("AGENTS.md", "PROJECT_LOGIC.md", "HELP.md", "AD_STUDIO_ACCEPTANCE_PLAN.md", "AD_STUDIO_ACCEPTANCE_SOP.md", "SESSION_HANDOFF.md", "test_ai_handoff.py"):
            self.assertIn(entry, handoff)

        self.assertIn("LLM 负责思考和决策", agents)
        self.assertIn("当前已知限制", help_doc)
        self.assertIn("验收入口与 AI 接手地图", logic)
        self.assertIn("## A32 · AI接手能力", plan)
        self.assertIn("## A33 · 完整用户流程", plan)

        for section in ("## 当前任务", "## 最新已知基线", "## 已完成的最近工作", "## 下一步（按顺序执行，不要跳过）", "## 当前验收与真实性边界", "## 不可违反的项目规则", "## 换窗口接手步骤"):
            self.assertIn(section, session_handoff)
        self.assertIn("新窗口必须查询 PR 当前 head、最新 CI、最新 docs-sync", session_handoff)
        self.assertIn("用户只需在新窗口说“继续桌面项目”", session_handoff)
        self.assertTrue(SESSION_HANDOFF.exists())

        for required in (HANDOFF, SESSION_HANDOFF, AGENTS, LOGIC, HELP, PLAN):
            self.assertTrue(required.exists(), required)


if __name__ == "__main__":
    unittest.main()
