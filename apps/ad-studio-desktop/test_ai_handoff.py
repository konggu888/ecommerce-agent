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

        self.assertIn("A34：AI 辅助商品画面对比（待最新 CI 验收）；A35：单镜头局部修复第一阶段已实现", handoff)
        for entry in ("AGENTS.md", "PROJECT_LOGIC.md", "HELP.md", "AD_STUDIO_ACCEPTANCE_PLAN.md", "test_ai_handoff.py"):
            self.assertIn(entry, handoff)

        self.assertIn("LLM 负责思考和决策", agents)
        self.assertIn("当前已知限制", help_doc)
        self.assertIn("验收入口与 AI 接手地图", logic)
        self.assertIn("## A32 · AI接手能力", plan)
        self.assertIn("## A33 · 完整用户流程", plan)
        self.assertIn("## A34 · AI辅助商品画面对比", plan)
        self.assertIn("## A35 · 问题镜头定位与仅重生成", plan)

        for required in (HANDOFF, AGENTS, LOGIC, HELP, PLAN):
            self.assertTrue(required.exists(), required)



    def test_handoff_mentions_a36_vision_guided_single_shot_repair(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A36", text)
        self.assertIn("可编辑修正草稿", text)
        self.assertIn("不得将仅有文档同步成功视为全量 CI 通过", text)

    def test_handoff_mentions_a37_draft_line_break_regression(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A37", text)
        self.assertIn("真实换行", text)

    def test_session_handoff_exists_and_warns_against_ci_overclaim(self):
        handoff = ROOT / "apps" / "ad-studio-desktop" / "SESSION_HANDOFF.md"
        self.assertTrue(handoff.is_file(), "SESSION_HANDOFF.md must exist for cross-session continuation")
        text = handoff.read_text(encoding="utf-8")
        self.assertIn("完整 CI", text)
        self.assertIn("不要把 docs-sync", text)
        self.assertIn("PR 保持 open/unmerged", text)

    def test_session_handoff_records_feature_branch_ci_requirement(self):
        handoff = (ROOT / "apps" / "ad-studio-desktop" / "SESSION_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A39", handoff)
        self.assertIn("所有分支", handoff)
        self.assertIn("完整 CI", handoff)

    def test_handoff_records_latest_successful_ci_baseline_sha(self):
        handoff = (ROOT / "apps" / "ad-studio-desktop" / "SESSION_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A42", handoff)
        self.assertIn("443f713cd3721eab528eb9bb17faf599d55ef3ce", handoff)
        self.assertIn("若当前 HEAD 与此 SHA 不同", handoff)

    def test_handoff_mentions_a43_regeneration_failure_recovery(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A43", text)
        self.assertIn("恢复旧视频", text)

    def test_handoff_mentions_a44_stable_short_drama_shot_mapping(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A44", text)
        self.assertIn("标题/集数回退", text)


    def test_handoff_mentions_a46_edit_path_preserves_previous_video(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A46", text)
        self.assertIn("编辑镜头", text)
        self.assertIn("旧版视频", text)

    def test_handoff_mentions_a50_prompt_line_break_regression(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A50", text)
        self.assertIn("真实换行", text)

    def test_handoff_mentions_a58_visual_comparison_input_validation(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A58", text)
        self.assertIn("空文件", text)
        self.assertIn("不支持的文件格式", text)

    def test_handoff_mentions_a52_failed_attempt_cost_accounting(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A52", text)
        self.assertIn("失败报价不计入实际花费", text)

    def test_handoff_mentions_a56_prompt_regression_fix(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A56", text)
        self.assertIn("真实换行", text)

    def test_handoff_mentions_a57_project_recovery_ui_and_cost_reconciliation(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A57", text)
        self.assertIn("打开已有项目", text)

    def test_handoff_mentions_a60_failed_only_cost_preservation(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A60", text)
        self.assertIn("失败-only", text)

    def test_handoff_mentions_a61_legacy_cost_migration(self):
        text = (ROOT / "docs" / "AD_STUDIO_AI_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("A61", text)
        self.assertIn("历史成本迁移", text)

if __name__ == "__main__":
    unittest.main()