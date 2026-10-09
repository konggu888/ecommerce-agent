import unittest
from pathlib import Path
from types import SimpleNamespace

from ad_studio.workflow_modes import (
    AUTO, SEMI_AUTO, USER_CONTROLLED, WORKFLOW_MODES,
    decide_action, get_project_workflow_mode, normalize_mode,
    set_project_workflow_mode,
)


class WorkflowModePolicyTests(unittest.TestCase):
    def test_desktop_ui_exposes_and_persists_workflow_modes(self):
        app_source = (Path(__file__).parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        for label in ("AI 全自动", "AI 半自动", "用户控制 / AI 辅助"):
            self.assertIn(label, app_source)
        self.assertIn("set_project_workflow_mode(self.project,selected_mode)", app_source)
        self.assertIn("self.workflow_mode.set(self._workflow_mode_label(get_project_workflow_mode(project)))", app_source)
        self.assertIn("def _choose_initial_plan(self, plans):", app_source)
        self.assertIn("if not self._authorize_workflow_action('final_delivery'", app_source)

    def test_known_modes_are_explicit_and_unknown_defaults_to_semi_auto(self):
        self.assertEqual(WORKFLOW_MODES, (AUTO, SEMI_AUTO, USER_CONTROLLED))
        self.assertEqual(normalize_mode("not-a-mode"), SEMI_AUTO)
        self.assertEqual(normalize_mode(None), SEMI_AUTO)

    def test_auto_mode_still_cannot_bypass_cloud_consent(self):
        decision = decide_action(AUTO, "cloud_generation")
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_confirmation)
        self.assertTrue(decide_action(AUTO, "cloud_generation", user_approved=True).allowed)

    def test_semi_auto_pauses_at_critical_checkpoints(self):
        for action in ("approve_creative_plan", "approve_storyboard", "final_delivery"):
            with self.subTest(action=action):
                decision = decide_action(SEMI_AUTO, action)
                self.assertFalse(decision.allowed)
                self.assertTrue(decision.requires_confirmation)
                self.assertTrue(decide_action(SEMI_AUTO, action, user_approved=True).allowed)

    def test_user_controlled_mode_does_not_make_decisions_for_user(self):
        for action in ("choose_creative_plan", "choose_shots", "approve_storyboard", "final_delivery"):
            with self.subTest(action=action):
                decision = decide_action(USER_CONTROLLED, action)
                self.assertFalse(decision.allowed)
                self.assertTrue(decision.requires_confirmation)

    def test_non_sensitive_auto_actions_can_proceed(self):
        decision = decide_action(AUTO, "analyze_product")
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.requires_confirmation)

    def test_explicit_consent_boundaries_apply_in_every_mode(self):
        for mode in WORKFLOW_MODES:
            for action in ("budget_overrun", "publish_or_real_platform_write", "delete_original_asset"):
                with self.subTest(mode=mode, action=action):
                    self.assertFalse(decide_action(mode, action).allowed)

    def test_mode_persists_in_existing_project_payload(self):
        project = SimpleNamespace(creative_plan={})
        self.assertEqual(set_project_workflow_mode(project, USER_CONTROLLED), USER_CONTROLLED)
        self.assertEqual(get_project_workflow_mode(project), USER_CONTROLLED)
        project.creative_plan = {}
        self.assertEqual(get_project_workflow_mode(project), SEMI_AUTO)


if __name__ == "__main__":
    unittest.main()
