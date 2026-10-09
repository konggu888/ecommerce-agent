import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

from ad_studio.workflow_modes import (
    AUTO, SEMI_AUTO, USER_CONTROLLED, WORKFLOW_MODES,
    decide_action, get_project_workflow_mode, normalize_mode,
    preserve_workflow_state, set_project_workflow_mode,
)


class WorkflowModePolicyTests(unittest.TestCase):
    def test_desktop_ui_exposes_and_persists_workflow_modes(self):
        app_source = (Path(__file__).parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        for label in ("AI 全自动", "AI 半自动", "用户控制 / AI 辅助"):
            self.assertIn(label, app_source)
        self.assertIn("set_project_workflow_mode(self.project,selected_mode)", app_source)
        self.assertIn("preserve_workflow_state(previous_plan, data)", app_source)
        self.assertIn("self.workflow_mode.set(self._workflow_mode_label(get_project_workflow_mode(project)))", app_source)
        self.assertIn("def _choose_initial_plan(self, plans):", app_source)
        self.assertIn("if len(plans) == 1:", app_source)
        self.assertIn("candidate['_variant_index']=variant_position", app_source)
        self.assertIn("cloud_generation", app_source)
        self.assertIn("decision.target == 'cloud' and not self._authorize_workflow_action('cloud_generation'", app_source)
        self.assertIn("if needs_cloud_video and CapabilityRouter(ROOT).decide_video().target == 'cloud':", app_source)
        self.assertIn("def _restore_variant_selection(self, variant_index):", app_source)
        self.assertIn("self._restore_variant_selection(original_index)", app_source)
        restore_start = app_source.index("def _restore_variant_selection(self, variant_index):")
        restore_end = app_source.index("\n    def switch_variant(self):", restore_start)
        restore_body = app_source[restore_start:restore_end]
        self.assertLess(restore_body.index("self._cache_active_variant()"), restore_body.index("self._activate_plan(target,info)"))
        self.assertIn("except Exception as exc:", app_source[app_source.index("def batch_generate_variants(self):"):app_source.index("def batch_final_render(self):")])
        self.assertIn("except Exception as e:", app_source[app_source.index("def batch_final_render(self):"):app_source.index("def final_render(self):")])
        self.assertIn("已恢复原来选中的创意方案", app_source)
        self.assertIn("已完成的输出记录已保留", app_source)
        self.assertIn("def _confirm_budget_overrun(self, estimate, remaining", app_source)
        self.assertIn("self._confirm_budget_overrun(estimate,remaining,'AI补镜头预算超限确认')", app_source)
        self.assertIn("self._confirm_budget_overrun(estimated,remaining_budget,'一键生成预算超限确认')", app_source)
        self.assertIn("if not pending:", app_source)
        self.assertIn("if selected_mode == SEMI_AUTO:", app_source)
        self.assertIn("确认 AI 创意方案", app_source)
        self.assertIn("def _ensure_storyboard_approval(self):", app_source)
        self.assertIn("workflow_approvals", app_source)
        self.assertIn("if not self._ensure_storyboard_approval(): return", app_source)
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
        for action in ("approve_creative_plan", "approve_storyboard", "final_delivery", "generate_all_variants"):
            with self.subTest(action=action):
                decision = decide_action(SEMI_AUTO, action)
                self.assertFalse(decision.allowed)
                self.assertTrue(decision.requires_confirmation)
                self.assertTrue(decide_action(SEMI_AUTO, action, user_approved=True).allowed)

    def test_user_controlled_mode_does_not_make_decisions_for_user(self):
        for action in ("choose_creative_plan", "choose_shots", "approve_storyboard", "final_delivery", "generate_all_variants"):
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

    def test_workflow_mode_and_storyboard_approvals_survive_variant_activation(self):
        previous = {
            "workflow_mode": USER_CONTROLLED,
            "workflow_approvals": {"1": True, "2": False},
            "variant_shot_cache": {"1": [{"id": "shot-01"}]},
        }
        next_plan = {"variant_index": 2, "strategy": "another creative plan"}
        preserve_workflow_state(previous, next_plan)
        self.assertEqual(next_plan["workflow_mode"], USER_CONTROLLED)
        self.assertEqual(next_plan["workflow_approvals"], {"1": True, "2": False})
        self.assertNotIn("variant_shot_cache", next_plan)

    def test_mode_persists_in_existing_project_payload(self):
        project = SimpleNamespace(creative_plan={})
        self.assertEqual(set_project_workflow_mode(project, USER_CONTROLLED), USER_CONTROLLED)
        self.assertEqual(get_project_workflow_mode(project), USER_CONTROLLED)
        project.creative_plan = {}
        self.assertEqual(get_project_workflow_mode(project), SEMI_AUTO)


class VariantRecoveryBehaviorTests(unittest.TestCase):
    def test_restore_caches_current_partial_variant_before_switching_back(self):
        events = []

        class Store:
            def save(self, project):
                events.append(("save", project.creative_plan.get("variant_index")))

        class FakeApp:
            pass

        fake = FakeApp()
        fake.project = SimpleNamespace(
            creative_plan={
                "creative_variants": [
                    {"_variant_index": 1, "_variant_label": "方案一"},
                    {"_variant_index": 2, "_variant_label": "方案二"},
                ],
                "variant_shot_cache": {},
            },
            product_info={"url": "", "platform": "自动识别"},
        )
        fake.active_variant_index = 2
        fake.store = Store()
        fake._cache_active_variant = lambda: events.append(("cache", fake.active_variant_index))
        def activate(target, info):
            fake.active_variant_index = target["_variant_index"]
            fake.project.creative_plan["variant_index"] = target["_variant_index"]
            events.append(("activate", target["_variant_index"]))
        fake._activate_plan = activate
        fake.refresh_shots = lambda: events.append(("refresh", fake.active_variant_index))
        fake.show_shot = lambda: events.append(("show", fake.active_variant_index))

        source = (Path(__file__).parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        app_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App")
        method = next(node for node in app_class.body if isinstance(node, ast.FunctionDef) and node.name == "_restore_variant_selection")
        module = ast.Module(body=[method], type_ignores=[])
        ast.fix_missing_locations(module)
        namespace = {}
        exec(compile(module, "ad_studio/app.py", "exec"), namespace)
        restored = namespace["_restore_variant_selection"](fake, 1)

        self.assertTrue(restored)
        self.assertEqual(events[0], ("cache", 2))
        self.assertEqual(events[1], ("activate", 1))
        self.assertEqual(fake.active_variant_index, 1)
        self.assertIn(("save", 1), events)


if __name__ == "__main__":
    unittest.main()
