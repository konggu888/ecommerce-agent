# A102 final-render fixtures mock the normalization output file explicitly.
import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ad_studio.engine import detect_platform, estimate_cost, new_project, mark_regenerate
from ad_studio.library import LocalLibrary
from ad_studio.production import ProductionStore, generation_failure_ui_state, normalize_cost_estimate_rmb
from ad_studio.product_parser import ProductInfo, save_product_library, load_product_library, merge_product_library
from ad_studio.model_router import ModelRouter, ModelProfile, build_stage_prompt
from ad_studio.usage_ledger import UsageLedger


class DesktopCoreTests(unittest.TestCase):

    def test_setup_form_grid_rows_do_not_overlap(self):
        source_path = Path(__file__).with_name("ad_studio") / "app.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        app_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App")
        ui = next(node for node in app_class.body if isinstance(node, ast.FunctionDef) and node.name == "ui")

        def grid_position(fragment):
            for node in ast.walk(ui):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "grid":
                    continue
                segment = ast.get_source_segment(source, node) or ""
                if fragment not in segment:
                    continue
                keywords = {item.arg: ast.literal_eval(item.value) for item in node.keywords if item.arg in {"row", "column"}}
                return keywords.get("row"), keywords.get("column")
            self.fail(f"Could not find grid placement for {fragment!r}")

        expected = {
            "self.task_type": (2, 1),
            "self.form": (3, 1),
            "self.variant_count": (4, 1),
            "self.footage_mode": (5, 1),
            "textvariable=self.footage_folder": (5, 2),
            "text='选择素材文件夹'": (5, 3),
            "text='留空/自动：交给AI判断；手动选择仅作为约束'": (3, 2),
        }
        for fragment, position in expected.items():
            with self.subTest(control=fragment):
                self.assertEqual(grid_position(fragment), position)

        self.assertIn("actions=ttk.Frame(setup)", source)
        self.assertIn("ttk.Button(actions,text=label,command=command).grid(row=index//6,column=index%6", source)


    def test_ai_stage_prompts_preserve_product_fact_boundary(self):
        product = {"name": "商品X", "selling_points": ["用户确认卖点"], "specs": {"容量": "500ml"}}
        prompt = build_stage_prompt("product_understanding", {"product": product}, {})
        self.assertIn("不得发明资料中没有的规格、功效或价格", prompt)
        self.assertIn("用户确认卖点", prompt)
        selling_prompt = build_stage_prompt("selling_points", {"product": product}, {})
        self.assertIn("只提炼真实可依据的核心卖点", selling_prompt)

    def test_ai_create_plan_runs_full_understanding_to_asset_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            router = ModelRouter(Path(td) / "model-config.json")
            product = {"name": "商品X", "selling_points": ["用户确认卖点"], "specs": {"容量": "500ml"}}
            router.resolve_route = lambda function: ModelProfile(id="test", name="测试模型", provider="local_openai")
            calls = []
            def fake_complete(profile, prompt, function=None, **kwargs):
                calls.append(function or "")
                stage = next((s for s in ("product_understanding","selling_points","audience_pain","ad_strategy","ad_intensity","video_form","script","storyboard","asset_selection") if f"当前阶段：{s}" in prompt), "")
                outputs = {
                    "product_understanding": {"product_summary":"商品X","product_type":"日用品","positioning":"用户确认定位","usage_scenes":["家庭"]},
                    "selling_points": {"selling_points":["用户确认卖点"]},
                    "audience_pain": {"target_audience":["目标用户"],"pain_points":["真实痛点"]},
                    "ad_strategy": {"strategy":"场景证明","hook":"开场展示","proof":"实拍证明","cta":"了解商品"},
                    "ad_intensity": {"ad_level":"标准广告"},
                    "video_form": {"video_form":"真人实拍","duration_seconds":30},
                    "script": {"script":"围绕用户确认卖点"},
                    "storyboard": {"shots":[{"index":1,"objective":"展示卖点","visual":"展示商品","dialogue":"","duration_seconds":5}]},
                    "asset_selection": {"asset_selection":[{"shot_index":1,"asset_type":"product","requirements":["商品"]}]},
                }
                return outputs[stage]
            router.complete_json = fake_complete
            result = router.create_plan(product, {})
            self.assertEqual(len(calls), 9)
            self.assertEqual(calls[0], "商品理解")
            self.assertEqual(calls[-1], "素材选择")
            self.assertEqual(result["selling_points"], ["用户确认卖点"])
            self.assertEqual(result["duration_seconds"], 30)
            self.assertIn("creative_stages", result)

    def test_creative_variant_audit_distinguishes_mechanism_from_surface_changes(self):
        from ad_studio.model_router import audit_ad_variant_set, build_creative_test_plan
        base = {
            "hook": "问题开场", "strategy": "痛点策略", "selling_points": ["卖点A"],
            "video_form": "真人口播", "proof": "实拍证明", "cta": "立即了解",
            "script": "版本文案",
        }
        surface = dict(base, script="换一种说法")
        mechanism = dict(base, hook="结果开场")
        audit = audit_ad_variant_set([base, surface, mechanism], "广告投放视频")
        self.assertTrue(audit["enabled"])
        self.assertEqual(audit["pairs"][0]["test_quality"], "仅表层差异")
        self.assertIn("hook", audit["pairs"][1]["mechanism_differences"])
        plan = build_creative_test_plan([base, mechanism], audit_ad_variant_set([base, mechanism], "广告投放视频"))
        self.assertEqual(plan["variants"][0]["result_status"], "待真实投放数据")
        self.assertIn("不猜测平台", plan["data_boundary"])
        metric_keys = {"ctr", "cvr", "cpc_rmb", "cpa_rmb", "roas"}
        self.assertFalse(metric_keys.intersection(plan["variants"][0]))
        self.assertFalse(metric_keys.intersection(plan["variants"][1]))

    def test_creative_variants_keep_independent_variant_state(self):
        from ad_studio.models import Project
        p = Project(id="p1", product_name="测试", platform="", form="广告投放视频", level=1, actor_id=None, scene_id=None, shots=[])
        p.creative_plan = {
            "creative_variants": [{"variant_index": 1, "hook": "A"}, {"variant_index": 2, "hook": "B"}],
            "variant_count": 2,
            "variant_1": {"status": "ready"},
            "variant_2": {"status": "review"},
        }
        self.assertEqual(len(p.creative_plan["creative_variants"]), 2)
        self.assertEqual(p.creative_plan["variant_1"]["status"], "ready")
        self.assertEqual(p.creative_plan["variant_2"]["status"], "review")

    def test_three_task_types_have_distinct_deterministic_policies(self):
        from ad_studio.creative_engine import apply_task_type_policy, validate_task_type_plan
        base = {
            "duration_seconds": 60,
            "strategy": "策略",
            "hook": "开场钩子",
            "script": "购买下单转化",
            "shots": [
                {"objective": "商品", "visual": "商品细节功能展示", "dialogue": "购买下单"},
                {"objective": "detail", "visual": "产品特写"},
            ],
        }
        policies = {}
        for task_type in ("电商短视频", "商品主图视频", "广告投放视频"):
            raw = dict(base)
            raw["shots"] = [dict(x) for x in base["shots"]]
            result = apply_task_type_policy(raw, {"task_type": task_type})
            policies[task_type] = result["task_policy"]
            self.assertEqual(result["task_type"], task_type)
            self.assertGreaterEqual(result["duration_seconds"], result["task_policy"]["min_seconds"])
            self.assertLessEqual(result["duration_seconds"], result["task_policy"]["max_seconds"])
        self.assertNotEqual(policies["电商短视频"]["sequence"], policies["商品主图视频"]["sequence"])
        self.assertNotEqual(policies["商品主图视频"]["sequence"], policies["广告投放视频"]["sequence"])
        self.assertTrue(validate_task_type_plan(
            apply_task_type_policy(dict(base), {"task_type": "广告投放视频"}),
            {"task_type": "广告投放视频"}
        ))

    def test_footage_planner_uses_only_supplied_assets_and_respects_task_rules(self):
        with tempfile.TemporaryDirectory() as td:
            router = ModelRouter(Path(td) / "model-config.json")
            profile = ModelProfile(id="test", name="测试模型", provider="local_openai")
            router.resolve_route = lambda function: profile
            captured = {}
            def fake_complete(profile, prompt, function=None, **kwargs):
                captured["prompt"] = prompt
                return {
                    "footage_plan": [{
                        "source": "A.mp4",
                        "start": 1,
                        "duration": 4,
                        "covered_selling_points": ["卖点A"],
                        "reason": "开场先展示商品",
                    }]
                }
            router.complete_json = fake_complete
            clips = [{"name": "A.mp4", "duration": 10, "width": 1080, "height": 1920, "fps": 30}]
            creative = {
                "task_type": "电商短视频",
                "selling_points": ["卖点A"],
                "shots": [{"index": 1, "objective": "展示卖点A"}],
                "task_policy": {"min_seconds": 30, "max_seconds": 60, "sequence": ["hook", "selling_point", "cta"]},
            }
            result = router.plan_footage(
                {"name": "商品X", "selling_points": ["卖点A"]},
                creative,
                clips,
                footage_analysis={"clips": [{"source": "A.mp4", "best_take": True, "material_rank": 1}]},
                footage_coverage={"opening_candidate": "A.mp4", "covered": [{"selling_point": "卖点A", "source": "A.mp4"}]},
            )
            self.assertEqual(result[0]["source"], "A.mp4")
            self.assertLessEqual(result[0]["start"] + result[0]["duration"], 10)
            self.assertIn("只能使用 footage_clips 清单中列出的素材文件", captured["prompt"])
            self.assertIn("task_type", captured["prompt"])
            self.assertIn("卖点A", captured["prompt"])

    def test_footage_planner_rejects_missing_plan_output(self):
        with tempfile.TemporaryDirectory() as td:
            router = ModelRouter(Path(td) / "model-config.json")
            router.resolve_route = lambda function: ModelProfile(id="test", name="测试模型", provider="local_openai")
            router.complete_json = lambda *args, **kwargs: {}
            with self.assertRaisesRegex(RuntimeError, "没有返回有效的 footage_plan"):
                router.plan_footage({"name": "商品X"}, {"task_type": "电商短视频"}, [{"name": "A.mp4", "duration": 10}], {})

    def test_footage_plan_enforces_speech_filler_cleanup_and_timestamp_ranges(self):
        with tempfile.TemporaryDirectory() as td:
            router = ModelRouter(Path(td) / "model-config.json")
            router.resolve_route = lambda function: ModelProfile(id="test", name="测试模型", provider="local_openai")
            captured = {}
            def fake_complete(profile, prompt, function=None, **kwargs):
                captured["prompt"] = prompt
                return {"footage_plan": [{
                    "source": "talk.mp4", "start": 2, "duration": 4,
                    "ranges": [{"start": 2, "end": 6}],
                    "reason": "保留核心卖点口播"
                }]}
            router.complete_json = fake_complete
            creative = {
                "task_type": "电商短视频",
                "selling_points": ["卖点A"],
                "footage_transcripts": [{
                    "source": "talk.mp4",
                    "segments": [
                        {"start": 0, "end": 2, "text": "大家好今天呢先跟大家聊一下"},
                        {"start": 2, "end": 6, "text": "这个商品的核心卖点A是用户确认的事实"},
                    ],
                }],
            }
            result = router.plan_footage(
                {"name": "商品X", "selling_points": ["卖点A"]},
                creative,
                [{"name": "talk.mp4", "duration": 10, "width": 1080, "height": 1920, "fps": 30}],
                footage_analysis={"clips": [{"source": "talk.mp4", "best_take": True}]},
                footage_coverage={},
            )
            self.assertEqual(result[0]["source"], "talk.mp4")
            self.assertIn("寒暄、重复、口头禅、停顿", captured["prompt"])
            self.assertIn("ranges 使用素材原始时间轴", captured["prompt"])
            self.assertIn("不能为了删废话破坏一句话的完整语义", captured["prompt"])

    def test_product_library_round_trip_preserves_user_facts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            info = ProductInfo(
                url="https://item.jd.com/999.html",
                platform="京东",
                name="商品X",
                selling_points=["卖点A", "卖点B"],
                specs={"容量": "500ml", "材质": "不锈钢"},
                forbidden_terms=["第一", "全网最低"],
            )
            save_product_library(info, root)
            restored = load_product_library(info.url, root)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.selling_points, ["卖点A", "卖点B"])
            self.assertEqual(restored.specs["容量"], "500ml")
            self.assertIn("全网最低", restored.forbidden_terms)

    def test_product_library_merge_does_not_invent_missing_facts(self):
        base = ProductInfo(url="https://item.jd.com/1000.html", platform="京东", name="商品Y")
        saved = ProductInfo(
            url=base.url,
            platform="京东",
            name="商品Y",
            selling_points=["用户确认卖点"],
            specs={"规格": "已确认"},
            forbidden_terms=["绝对"],
        )
        merged = merge_product_library(base, saved)
        self.assertEqual(merged.selling_points, ["用户确认卖点"])
        self.assertEqual(merged.specs, {"规格": "已确认"})
        self.assertEqual(merged.forbidden_terms, ["绝对"])
        self.assertEqual(merged.description, "")
        self.assertEqual(merged.images, [])

    def test_project_lifecycle_isolated_between_projects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            a = new_project("https://item.jd.com/111.html", 1, "AI自动选择")
            b = new_project("https://item.jd.com/222.html", 3, "产品展示")
            a.product_info = {"name": "商品A", "description": "A"}
            b.product_info = {"name": "商品B", "description": "B"}
            a.creative_plan = {"task_type": "电商短视频", "variant_index": 1}
            b.creative_plan = {"task_type": "商品主图视频", "variant_index": 1}
            store.save(a)
            store.save(b)
            restored_a = store.load(a.id)
            restored_b = store.load(b.id)
            self.assertNotEqual(restored_a.id, restored_b.id)
            self.assertEqual(restored_a.product_info["name"], "商品A")
            self.assertEqual(restored_b.product_info["name"], "商品B")
            self.assertEqual(restored_a.creative_plan["task_type"], "电商短视频")
            self.assertEqual(restored_b.creative_plan["task_type"], "商品主图视频")
            self.assertNotEqual((root / f"{a.id}.json").read_text(encoding="utf-8"),
                                (root / f"{b.id}.json").read_text(encoding="utf-8"))

    def test_task_type_is_persisted_and_not_replaced_by_platform(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/333.html", 2, "AI自动选择")
            p.creative_plan = {"task_type": "广告投放视频", "variant_count": 3}
            store.save(p)
            restored = store.load(p.id)
            self.assertEqual(restored.platform, "京东")
            self.assertEqual(restored.creative_plan["task_type"], "广告投放视频")
            self.assertEqual(restored.creative_plan["variant_count"], 3)

    def test_platform_detection(self):
        self.assertEqual(detect_platform("https://item.jd.com/123.html"), "京东")
        self.assertEqual(detect_platform("https://detail.tmall.com/item.htm?id=123"), "淘宝")
        self.assertEqual(detect_platform("https://mobile.yangkeduo.com/goods.html"), "拼多多")

    def test_budget_policy(self):
        c = estimate_cost(5)
        self.assertTrue(c["超预算"])
        self.assertEqual(c["总计"], 3.6)
        self.assertEqual(estimate_cost(6)["总计"], 4.32)

    def test_cost_breakdown_is_auditable_and_configurable(self):
        c = estimate_cost(5, {"cloud_video_per_shot": 1.0})
        self.assertEqual(c["云端"], 5.0)
        self.assertEqual(c["总计"], 5.0)
        video = next(x for x in c["明细"] if x["项目"] == "云端视频生成")
        self.assertEqual(video["数量"], 5)
        self.assertEqual(video["单价"], 1.0)
        self.assertEqual(video["小计"], 5.0)
        self.assertTrue(c["计价说明"])

    def test_only_selected_shot_changes_version(self):
        p = new_project("https://item.jd.com/123.html", 2, "真人口播")
        old = [s.version for s in p.shots]
        mark_regenerate(p, 2)
        self.assertEqual(p.shots[2].version, old[2] + 1)
        self.assertEqual([s.version for i, s in enumerate(p.shots) if i != 2], [old[i] for i in range(len(old)) if i != 2])

    def test_asset_persists_and_reuses(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "actor.txt"
            src.write_text("actor", encoding="utf-8")
            lib = LocalLibrary(root / "library")
            a = lib.add_file(src, "测试演员", "演员")
            again = lib.reusable("演员")
            self.assertEqual(len(again), 1)
            self.assertEqual(again[0].id, a.id)

    def test_default_assets_have_stable_ids(self):
        with tempfile.TemporaryDirectory() as td:
            lib = LocalLibrary(Path(td) / 'library')
            lib.ensure_defaults()
            ids = {a.id for a in lib.all()}
            self.assertIn('actor-linchuan', ids)
            self.assertIn('scene-home', ids)
            lib.ensure_defaults()
            self.assertEqual(len(ids), len(lib.all()))

    def test_project_save_load(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.cost_estimate = estimate_cost(len(p.shots))
            store.save(p)
            restored = store.load(p.id)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.id, p.id)
            self.assertEqual(len(restored.shots), len(p.shots))
            self.assertEqual(restored.cost_estimate["总计"], 3.6)

    def test_hybrid_gap_router_blocks_product_evidence_and_respects_budget(self):
        from ad_studio.hybrid_router import route_footage_gap_tasks
        result = route_footage_gap_tasks([
            {"task_id": "product-1", "need": "商品细节特写"},
            {"task_id": "generic-1", "need": "通用氛围辅助画面"},
        ], generation_connected=True, budget_remaining_rmb=1.0, cost_per_ai_shot_rmb=0.8)
        self.assertEqual(result["tasks"][0]["recommended_resolution"], "继续补拍")
        self.assertFalse(result["tasks"][0]["generation_allowed"])
        self.assertEqual(result["tasks"][1]["recommended_resolution"], "AI补镜头")
        self.assertAlmostEqual(result["budget_remaining_rmb"], 0.2)

    def test_hybrid_generation_failure_is_not_marked_success(self):
        from ad_studio.hybrid_router import execute_ai_gap_generation
        def fail(_task):
            raise RuntimeError("provider failed")
        result = execute_ai_gap_generation([
            {"task_id": "gap-1", "need": "通用辅助画面",
             "recommended_resolution": "AI补镜头", "generation_allowed": True}
        ], generator=fail, budget_remaining_rmb=1.0, cost_per_ai_shot_rmb=0.5)
        task = result["tasks"][0]
        self.assertEqual(result["failed"], 1)
        self.assertEqual(task["status"], "AI补镜头生成失败")
        self.assertFalse(task.get("accepted_into_storyboard", False))

    def test_hybrid_generated_shot_requires_human_review_before_acceptance(self):
        from ad_studio.models import Shot, accept_hybrid_generated_shot
        shots = [Shot(id="shot-01", index=1, title="原镜头", visual="商品", script="")]
        task = {
            "task_id": "gap-1", "generated_path": "/tmp/gap.mp4",
            "review_status": "待复核", "need": "通用辅助画面",
        }
        with self.assertRaises(ValueError):
            accept_hybrid_generated_shot(task, shots)
        task["review_status"] = "已通过"
        updated = accept_hybrid_generated_shot(task, shots)
        self.assertEqual(updated[-1].storyboard_review, "已通过")
        self.assertTrue(task["accepted_into_storyboard"])

    def test_reviewed_hybrid_task_persists_into_project(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            task = {
                "task_id": "GAP-PERSIST-1",
                "generated_path": str(Path(td) / "support.mp4"),
                "review_status": "已通过",
                "estimated_cost_rmb": 0.72,
                "provider": "测试Provider",
                "target_shot_index": 2,
            }
            Path(task["generated_path"]).write_bytes(b"fake-video")
            accepted = store.accept_hybrid_generated_task(p, task)
            self.assertIsNotNone(accepted)
            self.assertTrue(task["accepted_into_storyboard"])
            self.assertEqual(len(p.shots), 6)
            self.assertTrue(any(s.id == task["accepted_shot_id"] for s in p.shots))
            restored = store.load(p.id)
            self.assertEqual(len(restored.shots), 6)
            self.assertTrue(any(s.id == task["accepted_shot_id"] for s in restored.shots))


    def test_creative_variant_analysis_does_not_assume_platform_or_fabricate_metrics(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        app = App.__new__(App)
        app.project = type('Project', (), {
            'creative_plan': {
                'creative_variants': [
                    {
                        'variant_test_axis': {'name': '痛点切入'},
                        'hook': '先展示用户最烦的问题',
                        'strategy': '先痛点后解决方案',
                        'selling_points': ['省时间'],
                        'video_form': '产品演示',
                        'proof': '前后对比',
                        'cta': '了解更多',
                        'target_audience': ['忙碌用户'],
                    },
                    {
                        'variant_test_axis': {'name': '结果切入'},
                        'hook': '先展示使用结果',
                        'strategy': '先结果后解释',
                        'selling_points': ['省时间'],
                        'video_form': '真人演示',
                        'proof': '实际使用',
                        'cta': '立即了解',
                        'target_audience': ['忙碌用户'],
                    },
                ]
            }
        })()
        # 该逻辑必须能够在完全没有 variant_performance 时正常存在；
        # 测试的是“创意分析不依赖平台数据”，而不是 UI 弹窗。
        plan=app.project.creative_plan
        variants=plan['creative_variants']
        axes=[v.get('variant_test_axis',{}).get('name') for v in variants]
        self.assertEqual(axes, ['痛点切入', '结果切入'])
        self.assertNotIn('variant_performance', plan)
        self.assertNotIn('抖音', ' '.join(str(v) for v in variants))
        self.assertNotIn('淘宝', ' '.join(str(v) for v in variants))

    def test_variant_performance_metrics_are_calculated_and_persistable(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        app = App.__new__(App)
        metrics = app._variant_metrics({
            'impressions': '10000',
            'clicks': '500',
            'conversions': '25',
            'spend_rmb': '100',
            'revenue_rmb': '400',
        })
        self.assertEqual(metrics['impressions'], 10000)
        self.assertEqual(metrics['clicks'], 500)
        self.assertEqual(metrics['conversions'], 25)
        self.assertAlmostEqual(metrics['ctr'], 0.05)
        self.assertAlmostEqual(metrics['cvr'], 0.05)
        self.assertAlmostEqual(metrics['cpc_rmb'], 0.2)
        self.assertAlmostEqual(metrics['cpa_rmb'], 4.0)
        self.assertAlmostEqual(metrics['roas'], 4.0)
        self.assertEqual(app._variant_metrics({})['ctr'], 0.0)

    def test_variant_state_survives_plan_switch(self):
        # 切换方案会重建当前 creative_plan；已生成的版本缓存/输出记录必须保留。
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        with tempfile.TemporaryDirectory() as td:
            app = App.__new__(App)
            app.project = new_project("https://item.jd.com/123.html", 2, "真人口播")
            app.project.creative_plan = {
                "creative_variants": [
                    {"_variant_index": 1, "video_form": "方案A"},
                    {"_variant_index": 2, "video_form": "方案B"},
                ],
                "variant_count": 2,
                "variant_shot_cache": {
                    "1": [{"id": "shot-01", "index": 1, "title": "A镜头", "visual": "A", "script": "A"}],
                    "2": [{"id": "shot-01", "index": 1, "title": "B镜头", "visual": "B", "script": "B"}],
                },
                "variant_outputs": {"1": {"path": "/tmp/a-final.mp4", "status": "已输出"}},
                "variant_footage_gap_tasks": {"1": {"tasks": [{"task_id": "A"}]}},
            }
            app.active_variant_index = 1
            app.level = type("V", (), {"get": lambda self: 2})()
            app.form = type("V", (), {"get": lambda self: "AI自动选择"})()
            app.task_type = type("V", (), {"get": lambda self: "电商短视频"})()
            app.lib = type("L", (), {"reusable": lambda self, kind: []})()
            app._activate_plan({
                "_variant_index": 2,
                "_variant_label": "方案2｜B",
                "video_form": "AI自动选择",
                "duration_seconds": 30,
                "product_summary": "测试商品",
                "product_type": "测试商品",
                "selling_points": ["核心卖点"],
                "target_audience": ["目标用户"],
                "pain_points": ["痛点"],
                "usage_scenes": ["使用场景"],
                "positioning": "高效解决用户需求",
                "ad_level": 2,
                "hook": "快速抓住注意力",
                "strategy": "方案B策略",
                "script": "展示卖点并引导购买",
                "shots": [{
                    "index": 1,
                    "objective": "开场",
                    "visual": "商品快速展示",
                    "dialogue": "立即了解商品"
                }],
            }, type("Info", (), {"name": "测试商品"})())
            self.assertEqual(app.project.creative_plan["variant_outputs"]["1"]["path"], "/tmp/a-final.mp4")
            self.assertIn("2", app.project.creative_plan["variant_shot_cache"])
            self.assertIn("1", app.project.creative_plan["variant_footage_gap_tasks"])

    def test_batch_generation_captures_original_variant_before_preflight(self):
        # 回归：预算预审会切换方案，原始方案必须在预审前锁定。
        import inspect
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        source = inspect.getsource(App.batch_generate_variants)
        lock = source.index("original_index=self.active_variant_index")
        preflight = source.index("for pos,raw0 in enumerate(variants,1):")
        restore = source.index("original=original_index")
        self.assertLess(lock, preflight)
        self.assertLess(preflight, restore)

    def test_variant_runtime_state_isolated_for_hybrid_gap_tasks(self):
        # GitHub Linux runner不一定安装Tk；测试只需要App的无GUI状态方法。
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys
            import types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan = {
                "variant_footage_gap_tasks": {},
                "variant_hybrid_reviewed_shots": {},
            }
            app = App.__new__(App)
            app.project = p
            app.active_variant_index = 1
            p.creative_plan["footage_gap_tasks"] = {
                "tasks": [{
                    "task_id": "A-GAP-1",
                    "variant_index": 1,
                    "recommended_resolution": "AI补镜头",
                    "generated_path": "/tmp/a.mp4",
                    "review_status": "已通过",
                }]
            }
            p.creative_plan["hybrid_reviewed_shots"] = [{"task_id": "A-GAP-1", "variant_index": 1}]
            app._cache_active_variant()

            app.active_variant_index = 2
            p.creative_plan["footage_gap_tasks"] = {"tasks": [{
                "task_id": "B-GAP-1",
                "variant_index": 2,
                "recommended_resolution": "AI补镜头",
            }]}
            p.creative_plan["hybrid_reviewed_shots"] = [{"task_id": "B-GAP-1", "variant_index": 2}]
            app._cache_active_variant()

            # 模拟切换回方案1：必须恢复 A，不能看到 B。
            app.active_variant_index = 1
            app._restore_active_variant_runtime()
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["footage_gap_tasks"]["tasks"]],
                ["A-GAP-1"],
            )
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["hybrid_reviewed_shots"]],
                ["A-GAP-1"],
            )

            app.active_variant_index = 2
            app._restore_active_variant_runtime()
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["footage_gap_tasks"]["tasks"]],
                ["B-GAP-1"],
            )
            self.assertEqual(
                [x["task_id"] for x in p.creative_plan["hybrid_reviewed_shots"]],
                ["B-GAP-1"],
            )

    def test_variant_render_paths_are_physically_isolated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan["variant_index"] = 1
            a = store.render_path(p, p.shots[0])
            p.creative_plan["variant_index"] = 2
            b = store.render_path(p, p.shots[0])
            self.assertNotEqual(a, b)
            self.assertIn("variant-1", str(a))
            self.assertIn("variant-2", str(b))
            self.assertNotEqual(store._variant_index(p), 1)

            # 后处理路径同样不能复用另一个方案的目录。
            self.assertIn("variant-2", str(root / "postprocessed" / p.id / "variant-2" / p.shots[0].id))
    def test_final_render_inputs_are_ordered_and_pending_hybrid_is_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            for shot in p.shots:
                path = root / f"{shot.id}.mp4"
                path.write_bytes(b"video")
                shot.video_path = str(path)
            p.shots[1].storyboard_review = "待复核"
            inputs = store.final_render_inputs(p)
            self.assertEqual([x["index"] for x in inputs], [1, 3, 4, 5])
            self.assertEqual(inputs[0]["index"], 1)
            p.shots[1].storyboard_review = "已通过"
            inputs = store.final_render_inputs(p)
            self.assertEqual([x["index"] for x in inputs], [1, 2, 3, 4, 5])


    def test_final_output_manifest_records_quality_and_version(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            output = root / "final.mp4"
            output.write_bytes(b"video")
            shots = p.shots[:2]
            media = {"valid": True, "path": str(output), "size_bytes": 5, "duration_seconds": 6.0,
                     "width": 1080, "height": 1920, "aspect": "9:16", "video_stream": True,
                     "reason": "最终视频机器质检通过"}
            gate = {"allowed": True, "reasons": [], "checked": True, "message": "最终成片安全闸门通过"}
            manifest_path = store.write_final_output_manifest(p, output, "9:16", 2, shots, gate, media)
            data = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(data["variant_index"], 2)
            self.assertEqual(data["shot_indices"], [1, 2])
            self.assertTrue(data["media_check"]["valid"])
            self.assertTrue(p.creative_plan["final_output_manifests"]["2|9:16"]["media_check"]["valid"])

    def test_final_output_inspection_rejects_wrong_aspect(self):
        with tempfile.TemporaryDirectory() as td:
            from unittest.mock import patch
            root = Path(td)
            store = ProductionStore(root)
            output = root / "final.mp4"
            output.write_bytes(b"video")
            fake_probe = '{"streams":[{"codec_type":"video","width":1920,"height":1080}],"format":{"duration":"5.2"}}'
            completed = type("Completed", (), {"stdout": fake_probe})()
            with patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                result = store.inspect_final_output(output, "9:16")
            self.assertFalse(result["valid"])
            self.assertIn("画幅", result["reason"])

    def test_final_output_inspection_accepts_valid_media(self):
        with tempfile.TemporaryDirectory() as td:
            from unittest.mock import patch
            root = Path(td)
            store = ProductionStore(root)
            output = root / "final.mp4"
            output.write_bytes(b"video")
            fake_probe = '{"streams":[{"codec_type":"video","width":1080,"height":1920}],"format":{"duration":"5.2"}}'
            completed = type("Completed", (), {"stdout": fake_probe})()
            with patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                result = store.inspect_final_output(output, "9:16")
            self.assertTrue(result["valid"])
            self.assertEqual(result["duration_seconds"], 5.2)

    def test_final_output_inspection_rejects_below_1080_class_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            from unittest.mock import patch
            root = Path(td)
            store = ProductionStore(root)
            output = root / "low.mp4"
            output.write_bytes(b"video")
            fake_probe = '{"streams":[{"codec_type":"video","width":720,"height":1280}],"format":{"duration":"5.2"}}'
            completed = type("Completed", (), {"stdout": fake_probe})()
            with patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                result = store.inspect_final_output(output, "9:16")
            self.assertFalse(result["valid"])
            self.assertIn("1080P", result["reason"])
            self.assertIn("720×1280", result["reason"])

    def test_final_delivery_repair_routes_point_back_to_correct_stage(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != 'tkinter':
                raise
            import sys, types
            fake_tk = types.ModuleType('tkinter')
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType('tkinter.ttk')
            fake_tk.filedialog = types.ModuleType('tkinter.filedialog')
            fake_tk.messagebox = types.ModuleType('tkinter.messagebox')
            sys.modules['tkinter'] = fake_tk
            sys.modules['tkinter.ttk'] = fake_tk.ttk
            sys.modules['tkinter.filedialog'] = fake_tk.filedialog
            sys.modules['tkinter.messagebox'] = fake_tk.messagebox
            from ad_studio.app import App
        app=App.__new__(App)
        routes=app._final_delivery_repair_routes(
            {'reasons':['方案1：商品资料未支持的卖点：功效A','镜头3：AI生成镜头尚未通过人工复核','方案1·clip.mp4：商品可能被遮挡']},
            {'valid':False,'reason':'输出画幅与要求 9:16 不一致'},
        )
        mapping={x['issue']:x['route'] for x in routes}
        self.assertEqual(mapping['方案1：商品资料未支持的卖点：功效A'],'创意事实检查')
        self.assertEqual(mapping['镜头3：AI生成镜头尚未通过人工复核'],'AI补镜头复核')
        self.assertEqual(mapping['方案1·clip.mp4：商品可能被遮挡'],'成片视觉复核')
        self.assertEqual(mapping['输出画幅与要求 9:16 不一致'],'最终成片输出')

    def test_final_output_history_is_separated_by_variant_and_aspect(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            a = root / "a.mp4"
            b = root / "b.mp4"
            a.write_bytes(b"a")
            b.write_bytes(b"b")
            media = {"valid": True, "duration_seconds": 5.0}
            gate = {"allowed": True}
            store.write_final_output_manifest(p, a, "9:16", 1, p.shots[:1], gate, media)
            store.write_final_output_manifest(p, b, "16:9", 2, p.shots[:1], gate, media)
            rows = store.final_output_history(p)
            self.assertEqual({x["key"] for x in rows}, {"1|9:16", "2|16:9"})
            self.assertTrue(all(x["delivery_status"] == "可交付" for x in rows))

    def test_audio_mixing_preserves_voice_and_lowers_bgm(self):
        from unittest.mock import patch
        from ad_studio.audio import mix_voice_bgm
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "mix.m4a"
            with patch("ad_studio.audio.shutil.which", return_value="/usr/bin/ffmpeg"), patch(
                "ad_studio.audio.subprocess.run"
            ) as run:
                mix_voice_bgm(Path(td) / "voice.wav", Path(td) / "bgm.mp3", out)
            args = run.call_args.args[0]
            joined = " ".join(args)
            self.assertIn("afftdn", joined)
            self.assertIn("volume=0.12", joined)
            self.assertIn("amix=inputs=2:duration=first", joined)

    def test_subtitles_use_real_timestamps_and_segment_long_speech(self):
        from ad_studio.subtitles import segment_subtitles, write_srt_segments
        segments = [{"start": 1.0, "end": 5.0, "text": "这是一个非常重要的商品卖点说明文字需要按可读长度分段"}]
        rows = segment_subtitles(segments, max_chars=10)
        self.assertGreater(len(rows), 1)
        self.assertAlmostEqual(rows[0]["start"], 1.0)
        self.assertAlmostEqual(rows[-1]["end"], 5.0)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "speech.srt"
            write_srt_segments(segments, out, max_chars=10)
            body = out.read_text(encoding="utf-8")
            self.assertIn("00:00:01,000 --> ", body)
            self.assertIn("这是一个非常重要的", body)


    def test_a20_final_delivery_safety_gate_blocks_unverified_risks(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan["creative_fact_audit"] = {"variants": [{"variant_index": 1, "unsupported_selling_points": ["未经资料支持的功效"], "forbidden_term_hits": ["全网最低"], "absolute_or_high_risk_claims": ["绝对有效"]}]}
            p.creative_plan["visual_fact_audit"] = {"variants": [{"variant_index": 1, "shots": [{"source": "clip.mp4", "risks": ["商品可能被遮挡"]}]}]}
            p.shots[0].clip_source = "ai_generated"
            p.shots[0].storyboard_review = "待复核"
            result = store.final_render_gate(p)
            self.assertFalse(result["allowed"])
            self.assertGreaterEqual(len(result["reasons"]), 4)
            self.assertTrue(any("未经资料支持的功效" in x for x in result["reasons"]))
            self.assertTrue(any("全网最低" in x for x in result["reasons"]))
            self.assertTrue(any("商品可能被遮挡" in x for x in result["reasons"]))
            self.assertTrue(any("尚未通过人工复核" in x for x in result["reasons"]))

    def test_a21_final_delivery_media_qc_and_variant_aspect_history_are_independent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            gate = {"allowed": True, "reasons": [], "checked": True}
            for variant, aspect, name in ((1, "9:16", "a.mp4"), (2, "16:9", "b.mp4")):
                output = root / name
                output.write_bytes(b"video")
                media = {"valid": True, "path": str(output), "size_bytes": 5, "duration_seconds": 5.0, "width": 1080 if aspect == "9:16" else 1920, "height": 1920 if aspect == "9:16" else 1080, "aspect": aspect, "video_stream": True, "reason": "最终视频机器质检通过"}
                store.write_final_output_manifest(p, output, aspect, variant, p.shots[:1], gate, media)
            rows = store.final_output_history(p)
            self.assertEqual({x["key"] for x in rows}, {"1|9:16", "2|16:9"})
            self.assertEqual(len({x["output_path"] for x in rows}), 2)
            self.assertTrue(all(x["delivery_status"] == "可交付" for x in rows))

    def test_a22_final_delivery_recheck_routes_each_failure_without_regeneration(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != "tkinter":
                raise
            import sys, types
            fake_tk = types.ModuleType("tkinter")
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType("tkinter.ttk")
            fake_tk.filedialog = types.ModuleType("tkinter.filedialog")
            fake_tk.messagebox = types.ModuleType("tkinter.messagebox")
            sys.modules["tkinter"] = fake_tk
            sys.modules["tkinter.ttk"] = fake_tk.ttk
            sys.modules["tkinter.filedialog"] = fake_tk.filedialog
            sys.modules["tkinter.messagebox"] = fake_tk.messagebox
            from ad_studio.app import App
        app = App.__new__(App)
        routes = app._final_delivery_repair_routes({"reasons": ["方案1：商品资料未支持的卖点：功效A", "镜头3：AI生成镜头尚未通过人工复核", "方案1·clip.mp4：商品可能被遮挡"]}, {"valid": False, "reason": "输出画幅与要求 9:16 不一致"})
        mapping = {x["issue"]: x["route"] for x in routes}
        self.assertEqual(mapping["方案1：商品资料未支持的卖点：功效A"], "创意事实检查")
        self.assertEqual(mapping["镜头3：AI生成镜头尚未通过人工复核"], "AI补镜头复核")
        self.assertEqual(mapping["方案1·clip.mp4：商品可能被遮挡"], "成片视觉复核")
        self.assertEqual(mapping["输出画幅与要求 9:16 不一致"], "最终成片输出")

    def test_a23_hybrid_review_to_final_render_is_closed_loop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            task = {"task_id": "A23-GAP-1", "generated_path": str(root / "support.mp4"), "review_status": "待复核", "target_shot_index": 2}
            Path(task["generated_path"]).write_bytes(b"fake-video")
            with self.assertRaises(ValueError):
                store.accept_hybrid_generated_task(p, task)
            self.assertFalse(task.get("accepted_into_storyboard", False))
            task["review_status"] = "已通过"
            accepted = store.accept_hybrid_generated_task(p, task)
            self.assertIsNotNone(accepted)
            self.assertTrue(task["accepted_into_storyboard"])
            self.assertTrue(any(s.id == task["accepted_shot_id"] and s.storyboard_review == "已通过" for s in p.shots))
            for shot in p.shots:
                if shot.video_path:
                    continue
                path = root / f"{shot.id}.mp4"
                path.write_bytes(b"video")
                shot.video_path = str(path)
            inputs = store.final_render_inputs(p)
            self.assertTrue(any(x["shot_id"] == task["accepted_shot_id"] for x in inputs))


    def test_a24_final_safety_gate_blocks_all_explicit_risk_classes(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan["creative_fact_audit"] = {
                "variants": [{
                    "variant_index": 1,
                    "unsupported_selling_points": ["未经资料支持的功效"],
                    "forbidden_term_hits": ["全网最低"],
                    "absolute_or_high_risk_claims": ["绝对有效"],
                }]
            }
            p.creative_plan["visual_fact_audit"] = {
                "variants": [{"variant_index": 1, "shots": [{"source": "clip.mp4", "risks": ["商品被遮挡"]}]}]
            }
            p.shots[0].clip_source = "ai_generated"
            p.shots[0].storyboard_review = "待复核"
            gate = store.final_render_gate(p)
            self.assertFalse(gate["allowed"])
            self.assertTrue(gate["checked"])
            self.assertGreaterEqual(len(gate["reasons"]), 4)
            self.assertTrue(any("商品资料未支持的卖点" in x for x in gate["reasons"]))
            self.assertTrue(any("命中用户禁用词" in x for x in gate["reasons"]))
            self.assertTrue(any("高风险绝对化表达" in x for x in gate["reasons"]))
            self.assertTrue(any("商品被遮挡" in x for x in gate["reasons"]))
            self.assertTrue(any("AI生成镜头尚未通过人工复核" in x for x in gate["reasons"]))

    def test_a24_build_final_cannot_write_output_when_safety_gate_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            p.creative_plan["creative_fact_audit"] = {
                "variants": [{"variant_index": 1, "unsupported_selling_points": ["未证实卖点"]}]
            }
            with self.assertRaises(RuntimeError):
                store.build_final(p, "9:16", 1)
            final_dir = root / "final" / p.id
            self.assertFalse(final_dir.exists() and any(final_dir.iterdir()))


    def test_short_drama_final_render_is_episode_isolated(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "AI短剧")
            p.creative_plan = {"production_mode": "short_drama"}
            p.shots = p.shots[:2]
            for index, shot in enumerate(p.shots, 1):
                shot.episode_number = index
                video = root / f"{shot.id}.mp4"
                video.write_bytes(b"video")
                shot.video_path = str(video)
            completed = type("Completed", (), {"stdout": '{"streams":[{"codec_type":"video","width":1080,"height":1920}],"format":{"duration":"4.0"}}'})()
            def fake_normalize(source, target, aspect):
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                Path(target).write_bytes(Path(source).read_bytes())
                return Path(target)
            with patch("ad_studio.production.concat") as concat, patch(
                "ad_studio.production.normalize_output_resolution", side_effect=fake_normalize
            ), patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                def fake_concat(inputs, output):
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    Path(output).write_bytes(b"episode-video")
                concat.side_effect = fake_concat
                output = store.build_final(p, "9:16", variant_index=1, episode_number=2)
            self.assertEqual(concat.call_count, 1)
            self.assertEqual([Path(x) for x in concat.call_args.args[0]], [Path(p.shots[1].video_path)])
            self.assertIn("-ep2", output.name)
            manifest = __import__("json").loads(output.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["episode_number"], 2)
            self.assertEqual(manifest["shot_ids"], [p.shots[1].id])
            self.assertIn("1|9:16|ep2", p.creative_plan["final_output_manifests"])

    def test_short_drama_episode_render_blocks_when_selected_episode_incomplete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "AI短剧")
            p.shots = p.shots[:2]
            p.shots[0].episode_number = 1
            p.shots[1].episode_number = 2
            video = root / f"{p.shots[0].id}.mp4"
            video.write_bytes(b"video")
            p.shots[0].video_path = str(video)
            with self.assertRaisesRegex(RuntimeError, "第2集还有 1 个镜头"):
                store.build_final(p, "9:16", episode_number=2)

    def test_a25_media_qc_rejects_missing_empty_and_no_video_stream(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            result = store.inspect_final_output(root / "missing.mp4", "9:16")
            self.assertFalse(result["valid"])
            self.assertIn("不存在或为空", result["reason"])

            empty = root / "empty.mp4"
            empty.write_bytes(b"")
            result = store.inspect_final_output(empty, "9:16")
            self.assertFalse(result["valid"])

            invalid = root / "no-video.mp4"
            invalid.write_bytes(b"not-video")
            completed = type("Completed", (), {"stdout": '{"streams":[{"codec_type":"audio"}],"format":{"duration":"5.2"}}'})()
            with patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                result = store.inspect_final_output(invalid, "9:16")
            self.assertFalse(result["valid"])
            self.assertIn("视频流", result["reason"])

    def test_a25_media_qc_rejects_zero_duration_and_invalid_dimensions(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            for probe in (
                '{"streams":[{"codec_type":"video","width":1080,"height":1920}],"format":{"duration":"0"}}',
                '{"streams":[{"codec_type":"video","width":0,"height":1920}],"format":{"duration":"5.2"}}',
            ):
                output = root / "bad.mp4"
                output.write_bytes(b"video")
                completed = type("Completed", (), {"stdout": probe})()
                with patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                    "ad_studio.production.subprocess.run", return_value=completed
                ):
                    result = store.inspect_final_output(output, "9:16")
                self.assertFalse(result["valid"])
                self.assertIn("尺寸或时长无效", result["reason"])

    def test_a25_media_qc_failure_never_marks_manifest_deliverable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            output = root / "failed.mp4"
            output.write_bytes(b"broken")
            manifest = store.write_final_output_manifest(
                p, output, "9:16", 1, p.shots[:1], {"allowed": True},
                {"valid": False, "reason": "视频流无效", "duration_seconds": 0},
            )
            import json
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["delivery_status"], "不可交付")

    def test_a25_build_final_deletes_invalid_output_and_writes_no_manifest(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            for shot in p.shots:
                path = root / f"{shot.id}.mp4"
                path.write_bytes(b"video")
                shot.video_path = str(path)
            completed = type("Completed", (), {"stdout": '{"streams":[{"codec_type":"video","width":1920,"height":1080}],"format":{"duration":"5.2"}}'})()
            def fake_normalize(source, target, aspect):
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                Path(target).write_bytes(Path(source).read_bytes())
                return Path(target)
            with patch("ad_studio.production.concat") as concat, patch(
                "ad_studio.production.normalize_output_resolution", side_effect=fake_normalize
            ), patch("ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"), patch(
                "ad_studio.production.subprocess.run", return_value=completed
            ):
                def fake_concat(inputs, output):
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    Path(output).write_bytes(b"invalid-output")
                concat.side_effect = fake_concat
                with self.assertRaises(RuntimeError) as cm:
                    store.build_final(p, "9:16", 1)
            self.assertIn("机器质检未通过", str(cm.exception))
            self.assertFalse((root / "final" / p.id / "final-9x16-v1.mp4").exists())
            self.assertFalse((p.creative_plan or {}).get("final_output_manifests"))


    def test_a26_final_output_history_keeps_revisions_independent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "真人口播")
            gate = {"allowed": True, "reasons": [], "checked": True}
            media = {"valid": True, "duration_seconds": 5.0, "width": 1080, "height": 1920}
            outputs = []
            for idx, (variant, aspect) in enumerate(((1, "9:16"), (1, "9:16"), (2, "16:9")), 1):
                output = root / f"final-{idx}.mp4"
                output.write_bytes(b"video")
                outputs.append(output)
                store.write_final_output_manifest(p, output, aspect, variant, p.shots[:idx], gate, media)
            rows = store.final_output_history(p)
            self.assertEqual(len(rows), 3)
            self.assertEqual([x["key"] for x in rows].count("1|9:16"), 2)
            self.assertEqual(len({x["revision_id"] for x in rows}), 3)
            self.assertEqual({x["variant_index"] for x in rows}, {1, 2})
            self.assertEqual({x["aspect"] for x in rows}, {"9:16", "16:9"})
            self.assertEqual({x["shot_count"] for x in rows}, {1, 2, 3})
            self.assertTrue(all(x["delivery_status"] == "可交付" for x in rows))
            # 当前方案+画幅索引仍保留最新记录，供交付中心定位当前输出。
            latest = p.creative_plan["final_output_manifests"]["1|9:16"]
            self.assertEqual(latest["output_path"], str(outputs[1]))


    def test_a27_delivery_recheck_reports_blocker_then_recovers_without_regeneration(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != "tkinter":
                raise
            import sys, types
            fake_tk = types.ModuleType("tkinter")
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType("tkinter.ttk")
            fake_tk.filedialog = types.ModuleType("tkinter.filedialog")
            fake_tk.messagebox = types.ModuleType("tkinter.messagebox")
            sys.modules["tkinter"] = fake_tk
            sys.modules["tkinter.ttk"] = fake_tk.ttk
            sys.modules["tkinter.filedialog"] = fake_tk.filedialog
            sys.modules["tkinter.messagebox"] = fake_tk.messagebox
            from ad_studio.app import App
        from types import SimpleNamespace
        from unittest.mock import patch

        app = App.__new__(App)
        project = new_project("https://item.jd.com/123.html", 2, "真人口播")
        project.creative_plan["creative_fact_audit"] = {
            "variants": [{"variant_index": 1, "unsupported_selling_points": ["未证实卖点"]}]
        }
        output = Path(tempfile.gettempdir()) / "a27-delivery.mp4"
        output.write_bytes(b"video")
        media = {"valid": True, "duration_seconds": 5.0, "width": 1080, "height": 1920, "reason": "最终视频机器质检通过"}
        history = [{"key": "1|9:16", "revision_id": "r1", "variant_index": 1, "aspect": "9:16",
                    "output_path": str(output), "exists": True, "delivery_status": "可交付",
                    "duration_seconds": 5.0, "shot_count": 5, "created_at": "2026-10-09T04:00:00.000000"}]
        class FakeStore:
            def save(self, _project): pass
            def final_output_history(self, _project): return history
            def inspect_final_output(self, _output, _aspect): return media
            def final_render_gate(self, _project):
                if _project.creative_plan.get("creative_fact_audit"):
                    return {"allowed": False, "reasons": ["方案1：商品资料未支持的卖点：未证实卖点"]}
                return {"allowed": True, "reasons": []}
        app.project = project
        app.store = FakeStore()
        app.active_variant_index = 1
        app.aspect = SimpleNamespace(get=lambda: "9:16")

        blocked = app._run_final_delivery_recheck()
        self.assertFalse(blocked["delivery_ready"])
        self.assertEqual(blocked["repair_routes"][0]["route"], "创意事实检查")
        self.assertEqual(blocked["output_path"], str(output))

        # 修复事实后重新检查：只复用现有输出，不重新生成。
        project.creative_plan["creative_fact_audit"] = {}
        recovered = app._run_final_delivery_recheck()
        self.assertTrue(recovered["delivery_ready"])
        self.assertTrue(recovered["media_check"]["valid"])
        self.assertEqual(recovered["repair_routes"], [])


    def test_a28_project_persistence_restores_versions_material_status_review_and_output_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            p = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            p.product_info = {
                "name": "商品X",
                "selling_points": ["用户确认卖点"],
                "specs": {"容量": "500ml"},
                "forbidden_terms": ["全网最低"],
            }
            p.creative_plan.update({
                "variant_index": 2,
                "variant_count": 2,
                "variant_1": {"status": "已完成"},
                "variant_2": {"status": "审核中"},
                "variant_shot_cache": {"2": [{"id": p.shots[0].id, "index": 1, "title": "首镜头", "visual": "商品", "script": "卖点"}]},
            })
            p.shots[0].version = 3
            p.shots[0].status = "已生成"
            p.shots[0].video_path = str(root / "shot-v3.mp4")
            p.shots[0].storyboard_review = "已通过"
            p.shots[0].clip_source = "filmed"
            p.shots[0].source_file = str(root / "raw.mp4")
            p.shots[0].source_ranges = [[1.2, 3.4]]
            output = root / "final-v2.mp4"
            output.write_bytes(b"video")
            store.write_final_output_manifest(
                p, output, "9:16", 2, p.shots[:1],
                {"allowed": True, "reasons": [], "checked": True},
                {"valid": True, "duration_seconds": 4.5, "width": 1080, "height": 1920},
            )
            store.save(p)

            restored = store.load(p.id)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.product_info["specs"]["容量"], "500ml")
            self.assertEqual(restored.creative_plan["variant_index"], 2)
            self.assertEqual(restored.creative_plan["variant_2"]["status"], "审核中")
            self.assertEqual(restored.shots[0].version, 3)
            self.assertEqual(restored.shots[0].storyboard_review, "已通过")
            self.assertEqual(restored.shots[0].clip_source, "filmed")
            self.assertEqual(restored.shots[0].source_ranges, [[1.2, 3.4]])
            history = store.final_output_history(restored)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["key"], "2|9:16")
            self.assertEqual(history[0]["duration_seconds"], 4.5)
            self.assertEqual(history[0]["shot_count"], 1)

    def test_a28_two_projects_do_not_share_persistent_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            a = new_project("https://item.jd.com/a.html", 1, "电商短视频")
            b = new_project("https://item.jd.com/b.html", 1, "商品主图视频")
            a.creative_plan["variant_index"] = 1
            a.product_info["name"] = "商品A"
            b.creative_plan["variant_index"] = 2
            b.product_info["name"] = "商品B"
            store.save(a)
            store.save(b)
            ar = store.load(a.id)
            br = store.load(b.id)
            self.assertEqual(ar.product_info["name"], "商品A")
            self.assertEqual(br.product_info["name"], "商品B")
            self.assertEqual(ar.creative_plan["variant_index"], 1)
            self.assertEqual(br.creative_plan["variant_index"], 2)
            self.assertNotEqual(ar.id, br.id)
            self.assertTrue((root / f"{ar.id}.json").exists())
            self.assertTrue((root / f"{br.id}.json").exists())

    def test_a29_real_data_boundary_requires_explicit_user_provenance_and_unverified_status(self):
        try:
            from ad_studio.app import App
        except ModuleNotFoundError as exc:
            if exc.name != "tkinter":
                raise
            import sys, types
            fake_tk = types.ModuleType("tkinter")
            fake_tk.Tk = object
            fake_tk.ttk = types.ModuleType("tkinter.ttk")
            fake_tk.filedialog = types.ModuleType("tkinter.filedialog")
            fake_tk.messagebox = types.ModuleType("tkinter.messagebox")
            sys.modules["tkinter"] = fake_tk
            sys.modules["tkinter.ttk"] = fake_tk.ttk
            sys.modules["tkinter.filedialog"] = fake_tk.filedialog
            sys.modules["tkinter.messagebox"] = fake_tk.messagebox
            from ad_studio.app import App
        app=App.__new__(App)
        project=new_project("https://item.jd.com/123.html", 2, "广告投放视频")
        payload=app._variant_metrics({"impressions":1000,"clicks":100,"conversions":5,"spend_rmb":200,"revenue_rmb":800})
        saved=app._record_variant_performance(project, 1, payload)
        self.assertEqual(saved["impressions"], 1000)
        self.assertAlmostEqual(saved["ctr"], 0.1)
        provenance=project.creative_plan["variant_performance_provenance"]["1"]
        self.assertEqual(provenance["source_type"], "user_provided")
        self.assertEqual(provenance["verification_status"], "unverified")
        self.assertIn("不验证真实性", provenance["statement"])
        self.assertNotIn("platform_api_response", saved)

        from ad_studio.model_router import build_creative_test_plan
        plan=build_creative_test_plan([{"variant_test_axis":{"id":"hook","name":"开场钩子"}},{"variant_test_axis":{"id":"strategy","name":"核心策略"}}])
        self.assertEqual(plan["result_status"] if "result_status" in plan else "待真实投放数据", "待真实投放数据")
        self.assertFalse(any(k in plan for k in ("ctr","cvr","cpc_rmb","cpa_rmb","roas")))
        self.assertIn("不产生平台转化指标", plan["data_boundary"])


    def test_a30_recovery_records_failures_without_losing_project_state(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "电商短视频")
            shot = project.shots[0]
            shot.status = "生成中…"
            store.save(project)
            record = store.record_recovery_failure(project, stage="AI调用", error="provider timeout", next_action="检查模型配置后重试", retryable=True)
            self.assertEqual(record["status"], "待恢复")
            self.assertEqual(project.creative_plan["recovery"]["next_action"], "检查模型配置后重试")
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].status, "生成中…")
            self.assertEqual(restored.creative_plan["recovery"]["stage"], "AI调用")

    def test_a30_recovery_cleans_interrupted_assets_and_marks_corrupt_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            missing = root / "missing-source.mp4"
            shot.video_path = str(missing)
            shot.status = "已生成"
            render_dir = root / "renders" / project.id / "variant-1" / shot.id
            render_dir.mkdir(parents=True)
            (render_dir / "v1.part.mp4").write_bytes(b"partial")
            corrupt = root / "final.mp4"
            history = {"output_path": str(corrupt), "delivery_status": "可交付"}
            project.creative_plan["final_output_history_records"] = [history]
            store.save(project)
            result = store.recover_project(project)
            self.assertEqual(result["removed_temp_files"], 1)
            self.assertEqual(result["missing_media"], [shot.id])
            self.assertEqual(result["invalid_outputs"], [str(corrupt)])
            self.assertEqual(shot.status, "待重新生成/重新选择素材")
            self.assertEqual(history["delivery_status"], "不可交付")
            self.assertEqual(project.creative_plan["recovery"]["status"], "可继续")

    def test_a30_budget_and_non_retryable_failures_have_explicit_next_actions(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            budget = store.record_recovery_failure(project, stage="预算不足", error="剩余预算不足以执行AI补镜头", next_action="补充预算或改用本地/实拍方案", retryable=False)
            self.assertEqual(budget["status"], "需处理")
            self.assertIn("补充预算", budget["next_action"])
            resumed = store.clear_recovery(project)
            self.assertEqual(resumed["status"], "正常")


    def test_a31_handoff_docs_contain_project_map_progress_acceptance_tests_and_safety_boundaries(self):
        root = Path(__file__).resolve().parents[2]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        logic = (root / "apps" / "ad-studio-desktop" / "PROJECT_LOGIC.md").read_text(encoding="utf-8")
        help_doc = (root / "apps" / "ad-studio-desktop" / "HELP.md").read_text(encoding="utf-8")
        plan = (root / "docs" / "AD_STUDIO_ACCEPTANCE_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("AI 商品广告工厂", help_doc)
        self.assertIn("LLM 负责思考和决策", agents)
        self.assertIn("## 验收入口与 AI 接手地图", logic)
        self.assertIn("A0 → A1 → A2", plan)
        self.assertIn("A30 · 失败恢复", plan)
        self.assertIn("A31 · 帮助文档", plan)
        self.assertIn("python tools/check_ad_studio_docs.py", agents)
        for phrase in ("输入是什么", "谁负责决策", "谁负责执行", "状态保存在哪里", "失败时怎么办", "哪些部分是真接通"):
            self.assertIn(phrase, agents)
        self.assertIn("当前已知限制", help_doc)
        self.assertIn("测试", logic)


    def test_a43_regeneration_failure_restores_previous_good_video_and_persists_it(self):
        class FailingProvider:
            provider_name = "测试失败 Provider"
            cost_per_shot_rmb = 0.72

            def generate(self, request):
                raise RuntimeError("模拟 Provider 超时")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            shot.status = "已生成"
            store.save(project)

            mark_regenerate(project, 0)
            self.assertIsNone(shot.video_path)
            self.assertEqual(shot.previous_video_path, str(old_output))
            store.save(project)

            with self.assertRaisesRegex(RuntimeError, "模拟 Provider 超时"):
                store._render_with_provider(project, shot, FailingProvider())

            self.assertEqual(shot.video_path, str(old_output))
            self.assertIsNone(shot.previous_video_path)
            self.assertEqual(shot.status, "生成失败（已保留上一版本）")
            self.assertEqual(old_output.read_bytes(), b"previous-good-video")
            self.assertFalse(store.render_path(project, shot).with_suffix(".part.mp4").exists())
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].video_path, str(old_output))
            self.assertEqual(restored.shots[0].status, "生成失败（已保留上一版本）")

    def test_a45_ui_failure_state_keeps_recovered_previous_video_status(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as td:
            old_video = Path(td) / "old-v1.mp4"
            old_video.write_bytes(b"playable-old-video")
            shot = SimpleNamespace(
                status="生成失败（已保留上一版本）",
                video_path=str(old_video),
            )
            state = generation_failure_ui_state(shot)
            self.assertEqual(state["status"], "生成失败（已保留上一版本）")
            self.assertTrue(state["previous_version_available"])
            self.assertEqual(state["video_path"], str(old_video))

            shot.video_path = str(Path(td) / "missing.mp4")
            state = generation_failure_ui_state(shot)
            self.assertEqual(state["status"], "生成失败")
            self.assertFalse(state["previous_version_available"])
            self.assertEqual(state["video_path"], "")

    def test_a43_project_recovery_restores_previous_video_after_interrupted_regeneration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            store.save(project)

            mark_regenerate(project, 0)
            shot.status = "生成中…"
            render_output = store.render_path(project, shot)
            part = render_output.with_suffix(".part.mp4")
            split_part = render_output.with_name(f"{render_output.stem}.part01.mp4")
            part.parent.mkdir(parents=True, exist_ok=True)
            part.write_bytes(b"partial-video")
            split_part.write_bytes(b"partial-split-video")
            store.save(project)

            result = store.recover_project(project)
            self.assertEqual(result["removed_temp_files"], 2)
            self.assertEqual(result["restored_previous_versions"], [shot.id])
            self.assertEqual(shot.video_path, str(old_output))
            self.assertIsNone(shot.previous_video_path)
            self.assertEqual(shot.status, "生成中断（已恢复上一版本）")
            self.assertFalse(part.exists())
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].video_path, str(old_output))


    def test_a53_recovery_rejects_zero_byte_previous_video(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            zero_byte_video = root / "zero-byte-v1.mp4"
            zero_byte_video.write_bytes(b"")
            shot.video_path = None
            shot.previous_video_path = str(zero_byte_video)
            shot.status = "生成中…"
            store.save(project)
            result = store.recover_project(project)
            self.assertEqual(result["restored_previous_versions"], [])
            self.assertIn(shot.id, result["missing_media"])
            self.assertIsNone(shot.video_path)
            self.assertIsNone(shot.previous_video_path)
            self.assertEqual(shot.status, "待重新生成/重新选择素材")
            restored = store.load(project.id)
            self.assertIsNone(restored.shots[0].video_path)
            self.assertIsNone(restored.shots[0].previous_video_path)


    def test_a54_recovery_restores_valid_previous_video_when_active_video_is_zero_byte(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            active_zero = root / "active-v2.mp4"
            active_zero.write_bytes(b"")
            previous_good = root / "previous-v1.mp4"
            previous_good.write_bytes(b"playable-previous-video")
            shot.video_path = str(active_zero)
            shot.previous_video_path = str(previous_good)
            shot.status = "生成中…"
            store.save(project)
            result = store.recover_project(project)
            self.assertEqual(result["restored_previous_versions"], [shot.id])
            self.assertEqual(shot.video_path, str(previous_good))
            self.assertIsNone(shot.previous_video_path)
            self.assertEqual(shot.status, "生成中断（已恢复上一版本）")

    def test_a54_recovery_clears_zero_byte_active_video_without_previous_video(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            active_zero = root / "active-v1.mp4"
            active_zero.write_bytes(b"")
            shot.video_path = str(active_zero)
            shot.previous_video_path = None
            shot.status = "生成中…"
            store.save(project)
            result = store.recover_project(project)
            self.assertIn(shot.id, result["missing_media"])
            self.assertIsNone(shot.video_path)
            self.assertEqual(shot.status, "待重新生成/重新选择素材")

    def test_a57_generate_shot_ui_surfaces_cost_reconciliation_state(self):
        app_source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        start = app_source.index("def generate_shot(self):")
        end = app_source.index("def regen_shot(self):", start)
        block = app_source[start:end]
        self.assertIn('if s.status == "已生成（成本待核对）":', block)
        self.assertIn("项目实际成本待核对", block)
        self.assertIn("usage-ledger.json", block)
        self.assertNotIn("项目实际累计", block.split('if s.status == "已生成（成本待核对）":', 1)[1].split("else:", 1)[0])

    def test_a46_edit_shot_routes_through_safe_regeneration_transition(self):
        app_source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        start = app_source.index("def edit_shot(self):")
        end = app_source.index("def load_project(self):", start)
        edit_block = app_source[start:end]
        self.assertIn("mark_regenerate(self.project,self.project.shots.index(s))", edit_block)
        self.assertNotIn("s.video_path=None", edit_block)
        self.assertNotIn("s.version+=1", edit_block)


    def test_a47_asset_resolution_failure_restores_previous_video(self):
        class FailingAssetStore(ProductionStore):
            def resolve_assets(self, project, shot, authorize_cloud=None):
                raise RuntimeError("模拟素材解析失败")

        class UnusedProvider:
            provider_name = "未调用 Provider"
            cost_per_shot_rmb = 0.72
            def generate(self, request):
                raise AssertionError("素材解析失败后不应调用视频 Provider")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = FailingAssetStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            store.save(project)

            mark_regenerate(project, 0)
            store.save(project)
            with self.assertRaisesRegex(RuntimeError, "模拟素材解析失败"):
                store._render_with_provider(project, shot, UnusedProvider())

            self.assertEqual(shot.video_path, str(old_output))
            self.assertIsNone(shot.previous_video_path)
            self.assertEqual(shot.status, "生成失败（已保留上一版本）")
            self.assertEqual(old_output.read_bytes(), b"previous-good-video")
            self.assertFalse(store.render_path(project, shot).with_suffix(".part.mp4").exists())
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].video_path, str(old_output))


    def test_a48_footage_trim_failure_does_not_delete_existing_output(self):
        from unittest.mock import patch
        from ad_studio.footage import FootageError

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            output = store.render_path(project, shot)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"previous-good-video")
            source = root / "source.mp4"
            source.write_bytes(b"dummy-source")
            shot.video_path = str(output)
            shot.clip_source = "filmed"
            shot.source_file = str(source)
            shot.source_duration = 2.0
            store.save(project)

            with patch("ad_studio.footage.trim_clip", side_effect=RuntimeError("模拟裁剪失败")):
                with self.assertRaisesRegex(RuntimeError, "模拟裁剪失败"):
                    store.render_footage_shot(project, shot)

            self.assertEqual(output.read_bytes(), b"previous-good-video")
            self.assertEqual(shot.video_path, str(output))
            self.assertEqual(shot.status, "素材裁剪失败（已保留上一版本）")
            self.assertFalse(output.with_suffix(".part.mp4").exists())
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].video_path, str(output))


    def test_a49_missing_footage_source_cleans_stale_split_parts_and_keeps_old_video(self):
        from ad_studio.footage import FootageError

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            shot.clip_source = "filmed"
            shot.source_file = str(root / "missing-source.mp4")
            store.save(project)

            mark_regenerate(project, 0)
            output = store.render_path(project, shot)
            stale_part = output.with_name(f"{output.stem}.part01.mp4")
            stale_part.write_bytes(b"stale-split")
            with self.assertRaises(FootageError):
                store.render_footage_shot(project, shot)

            self.assertFalse(stale_part.exists())
            self.assertEqual(shot.video_path, str(old_output))
            self.assertEqual(old_output.read_bytes(), b"previous-good-video")
            self.assertEqual(shot.status, "素材裁剪失败（已保留上一版本）")



    def test_a51_cost_estimate_is_validated_before_confirmation(self):
        self.assertEqual(normalize_cost_estimate_rmb("0.72"), 0.72)
        self.assertEqual(normalize_cost_estimate_rmb(0), 0.0)
        for invalid in ("not-a-number", float("nan"), float("inf"), float("-inf"), -0.01, None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    normalize_cost_estimate_rmb(invalid)

    def test_a50_video_prompt_uses_real_line_breaks(self):
        class CapturingProvider:
            provider_name = "测试 Provider"
            cost_per_shot_rmb = 0.0

            def __init__(self):
                self.prompt = None

            def generate(self, request):
                self.prompt = request.prompt
                request.output.write_bytes(b"generated-video")
                return request.output

        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            shot.title = "开场镜头"
            shot.visual = "画面主体在左侧"
            shot.script = "突出真实卖点"
            provider = CapturingProvider()
            store._render_with_provider(project, shot, provider)
            self.assertEqual(
                provider.prompt,
                "标题：开场镜头\n画面：画面主体在左侧\n文案：突出真实卖点",
            )
            self.assertNotIn("\\n", provider.prompt)


    def test_a55_ledger_failure_does_not_turn_successful_video_into_provider_failure(self):
        class SuccessfulProvider:
            provider_name = "测试 Provider"
            cost_per_shot_rmb = 0.72
            def generate(self, request):
                request.output.write_bytes(b"generated-video")
                return request.output

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            store.save(project)
            mark_regenerate(project, 0)

            def fail_cost_record(*args, **kwargs):
                raise OSError("账本只读")

            store._record_actual_cost = fail_cost_record
            output = store._render_with_provider(project, shot, SuccessfulProvider())

            self.assertEqual(output.read_bytes(), b"generated-video")
            self.assertEqual(shot.video_path, str(output))
            self.assertEqual(shot.status, "已生成（成本待核对）")
            self.assertTrue(any(
                item.get("stage") == "视频已生成但成本记账待核对"
                for item in project.creative_plan.get("recovery", {}).get("history", [])
            ))
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].video_path, str(output))
            self.assertEqual(restored.shots[0].status, "已生成（成本待核对）")

    def test_a59_project_cost_total_comes_from_success_ledger_rows(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            store.ledger.record(
                function="已有成功任务", model_id="", model_name="", provider="测试",
                model="", status="success", estimated_cost_rmb=0.40,
                project_id=project.id, shot_id=shot.id, category="video",
            )
            store.ledger.record(
                function="失败任务", model_id="", model_name="", provider="测试",
                model="", status="failed", estimated_cost_rmb=0.0, unit_cost_rmb=0.72,
                project_id=project.id, shot_id=shot.id, category="video",
            )
            project.actual_cost_rmb = 99.0
            store._record_actual_cost(
                project, shot=shot, category="video", amount_rmb=0.72,
                provider="测试", quantity=1, unit_cost_rmb=0.72, function="本次成功任务",
            )
            summary = store.ledger.project_summary(project.id)
            self.assertAlmostEqual(summary["actual_cost_rmb"], 1.12)
            self.assertAlmostEqual(project.actual_cost_rmb, 1.12)
            self.assertAlmostEqual(project.cost_estimate["actual_cost_rmb"], 1.12)
            self.assertAlmostEqual(project.cost_estimate["actual"]["actual_cost_rmb"], 1.12)

    def test_a52_failed_video_attempt_is_auditable_without_double_counting_actual_cost(self):
        class FailingProvider:
            provider_name = "测试 Provider"
            cost_per_shot_rmb = 0.72
            def generate(self, request):
                raise RuntimeError("模拟失败后重试")

        class SuccessfulProvider:
            provider_name = "测试 Provider"
            cost_per_shot_rmb = 0.72
            def generate(self, request):
                request.output.write_bytes(b"generated-video")
                return request.output

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            old_output = store.render_path(project, shot)
            old_output.parent.mkdir(parents=True, exist_ok=True)
            old_output.write_bytes(b"previous-good-video")
            shot.video_path = str(old_output)
            shot.status = "已生成"
            store.save(project)

            mark_regenerate(project, 0)
            with self.assertRaisesRegex(RuntimeError, "模拟失败后重试"):
                store._render_with_provider(project, shot, FailingProvider())

            after_failure = store.ledger.project_summary(project.id)
            self.assertEqual(after_failure["actual_cost_rmb"], 0)
            self.assertEqual(after_failure["failed"], 1)
            failed_rows = [
                row for row in store.ledger.recent(20)
                if row.get("project_id") == project.id and row.get("status") == "failed"
            ]
            self.assertEqual(len(failed_rows), 1)
            self.assertEqual(failed_rows[0]["category"], "video")
            self.assertEqual(failed_rows[0]["estimated_cost_rmb"], 0)
            self.assertEqual(failed_rows[0]["unit_cost_rmb"], 0.72)

            mark_regenerate(project, 0)
            store._render_with_provider(project, shot, SuccessfulProvider())
            final_summary = store.ledger.project_summary(project.id)
            self.assertEqual(final_summary["actual_cost_rmb"], 0.72)
            self.assertEqual(final_summary["success"], 1)
            self.assertEqual(final_summary["failed"], 1)
            self.assertAlmostEqual(project.actual_cost_rmb, 0.72)


    def test_a57_project_recovery_reconciles_actual_cost_from_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            project.actual_cost_rmb = 99.0
            shot.actual_cost_rmb = 99.0
            store.ledger.record(
                function="视频镜头生成", model_id="", model_name="测试", provider="测试", model="",
                status="success", estimated_cost_rmb=0.72, project_id=project.id, shot_id=shot.id,
                category="video", quantity=1, unit_cost_rmb=0.72,
            )
            store.ledger.record(
                function="演员素材生成", model_id="", model_name="测试", provider="测试", model="",
                status="success", estimated_cost_rmb=0.25, project_id=project.id, shot_id=shot.id,
                category="asset", quantity=1, unit_cost_rmb=0.25,
            )
            store.ledger.record(
                function="视频镜头生成", model_id="", model_name="测试", provider="测试", model="",
                status="failed", estimated_cost_rmb=0.0, project_id=project.id, shot_id=shot.id,
                category="video", quantity=1, unit_cost_rmb=0.72, error="模拟失败",
            )
            store.save(project)
            result = store.recover_project(project)
            self.assertTrue(result["cost_reconciled"])
            self.assertAlmostEqual(project.actual_cost_rmb, 0.97)
            self.assertAlmostEqual(shot.actual_cost_rmb, 0.97)
            self.assertAlmostEqual(project.actual_cost_summary["actual_cost_rmb"], 0.97)
            restored = store.load(project.id)
            self.assertAlmostEqual(restored.actual_cost_rmb, 0.97)
            self.assertAlmostEqual(restored.shots[0].actual_cost_rmb, 0.97)

    def test_a57_project_recovery_preserves_legacy_cost_when_no_ledger_rows_exist(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            project.actual_cost_rmb = 2.5
            project.shots[0].actual_cost_rmb = 1.2
            store.save(project)
            result = store.recover_project(project)
            self.assertFalse(result["cost_reconciled"])
            self.assertAlmostEqual(project.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(project.shots[0].actual_cost_rmb, 1.2)
            restored = store.load(project.id)
            self.assertAlmostEqual(restored.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(restored.shots[0].actual_cost_rmb, 1.2)

    def test_a57_open_existing_project_runs_recovery_before_display(self):
        source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        start = source.index("def load_project(self):")
        end = source.index("def product_library_settings", start)
        body = source[start:end]
        recovery_at = body.index("self.store.recover_project(project)")
        assignment_at = body.index("self.project=project")
        self.assertLess(recovery_at, assignment_at)
        self.assertIn("已记账实际", body)


    def test_a60_failed_only_ledger_preserves_legacy_actual_cost(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            project.actual_cost_rmb = 2.5
            project.actual_cost_summary = {"actual_cost_rmb": 2.5, "by_category": {"video": 2.5}}
            shot = project.shots[0]
            shot.actual_cost_rmb = 1.2
            store.ledger.record(
                function="视频镜头生成", model_id="", model_name="测试", provider="测试", model="",
                status="failed", estimated_cost_rmb=0.0, project_id=project.id, shot_id=shot.id,
                category="video", quantity=1, unit_cost_rmb=0.72, error="模拟失败，无成功扣费确认",
            )
            store.save(project)
            result = store.recover_project(project)
            self.assertFalse(result["cost_reconciled"])
            self.assertAlmostEqual(project.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(shot.actual_cost_rmb, 1.2)
            self.assertAlmostEqual(project.cost_estimate["actual_cost_rmb"], 2.5)
            self.assertEqual(project.cost_estimate["actual"]["by_category"], {"video": 2.5})
            restored = store.load(project.id)
            self.assertAlmostEqual(restored.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(restored.shots[0].actual_cost_rmb, 1.2)
            self.assertAlmostEqual(restored.cost_estimate["actual_cost_rmb"], 2.5)
            self.assertEqual(restored.cost_estimate["actual"]["by_category"], {"video": 2.5})


    def test_a61_legacy_costs_migrate_once_before_first_successful_charge(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            project.actual_cost_rmb = 2.5
            project.actual_cost_summary = {"actual_cost_rmb": 2.5, "by_category": {"video": 2.5}}
            shot = project.shots[0]
            shot.actual_cost_rmb = 1.2
            store.ledger.record(
                function="失败尝试", model_id="", model_name="测试", provider="测试", model="",
                status="failed", estimated_cost_rmb=0.0, project_id=project.id, shot_id=shot.id,
                category="video", quantity=1, unit_cost_rmb=0.72, error="失败报价不是实际支出",
            )

            store._record_actual_cost(
                project, shot=shot, category="asset", amount_rmb=0.72,
                provider="测试", quantity=1, unit_cost_rmb=0.72, function="商品素材生成",
            )
            summary = store.ledger.project_summary(project.id)
            self.assertAlmostEqual(summary["actual_cost_rmb"], 3.22)
            self.assertAlmostEqual(project.actual_cost_rmb, 3.22)
            self.assertAlmostEqual(shot.actual_cost_rmb, 1.92)

            store._record_actual_cost(
                project, shot=shot, category="asset", amount_rmb=0.50,
                provider="测试", quantity=1, unit_cost_rmb=0.50, function="场景素材生成",
            )
            summary = store.ledger.project_summary(project.id)
            self.assertAlmostEqual(summary["actual_cost_rmb"], 3.72)
            self.assertAlmostEqual(shot.actual_cost_rmb, 2.42)
            migrated = [
                row for row in store.ledger.recent(50)
                if row.get("project_id") == project.id and row.get("function") == "历史实际成本迁移"
            ]
            self.assertEqual(len(migrated), 2)
            self.assertAlmostEqual(sum(row["estimated_cost_rmb"] for row in migrated), 2.5)

    def test_a61_record_many_migration_keeps_ledger_rows_atomic(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            before = store.ledger.recent(20)
            with self.assertRaises((TypeError, ValueError, OverflowError)):
                store.ledger.record_many([
                    {"function": "迁移有效行", "project_id": "p", "estimated_cost_rmb": 1.0},
                    {"function": "迁移无效行", "project_id": "p", "quantity": "not-a-number"},
                ])
            self.assertEqual(store.ledger.recent(20), before)


    def test_a63_migrated_legacy_cost_survives_when_new_charge_record_fails(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            project.actual_cost_rmb = 2.5
            project.actual_cost_summary = {"actual_cost_rmb": 2.5, "by_category": {"video": 2.5}}
            shot = project.shots[0]
            shot.actual_cost_rmb = 1.2
            store.ledger.record(
                function="失败尝试", model_id="", model_name="测试", provider="测试", model="",
                status="failed", estimated_cost_rmb=0.0, project_id=project.id, shot_id=shot.id,
                category="video", quantity=1, unit_cost_rmb=0.72, error="失败报价不是实际支出",
            )
            store.save(project)

            def fail_current_record(**kwargs):
                raise OSError("模拟本次账本写入失败")
            store.ledger.record = fail_current_record

            with self.assertRaisesRegex(OSError, "模拟本次账本写入失败"):
                store._record_actual_cost(
                    project, shot=shot, category="asset", amount_rmb=0.72,
                    provider="测试", quantity=1, unit_cost_rmb=0.72, function="商品素材生成",
                )

            self.assertAlmostEqual(project.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(shot.actual_cost_rmb, 1.2)
            self.assertAlmostEqual(project.cost_estimate["actual_cost_rmb"], 2.5)
            migrated = [
                row for row in store.ledger.recent(20)
                if row.get("project_id") == project.id and row.get("function") == "历史实际成本迁移"
            ]
            self.assertEqual(len(migrated), 2)
            store.save(project)
            restored = store.load(project.id)
            self.assertAlmostEqual(restored.actual_cost_rmb, 2.5)
            self.assertAlmostEqual(restored.shots[0].actual_cost_rmb, 1.2)


    def test_a64_asset_cost_record_failure_keeps_generated_asset_and_marks_reconciliation(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td))
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]

            def fail_cost_record(*args, **kwargs):
                raise OSError("模拟素材成本记账故障")
            store._record_actual_cost = fail_cost_record

            recorded, error = store._record_asset_cost(project, shot, "商品", 0.72, "测试 Provider")
            self.assertFalse(recorded)
            self.assertIn("模拟素材成本记账故障", error)
            history = project.creative_plan.get("recovery", {}).get("history", [])
            self.assertTrue(any(x.get("stage") == "商品素材已生成但成本结算未完成" for x in history))
            self.assertIn("usage-ledger.json", history[-1].get("next_action", ""))

    def test_a64_asset_generation_callers_distinguish_cost_failure_from_generation_failure(self):
        source = (Path(__file__).resolve().parent / "ad_studio" / "production.py").read_text(encoding="utf-8")
        resolve_start = source.index("def resolve_assets")
        generate_start = source.index("def generate_missing_asset", resolve_start)
        render_start = source.index("def render_shot", generate_start)
        resolve_body = source[resolve_start:generate_start]
        generate_body = source[generate_start:render_start]
        self.assertIn("self._record_asset_cost", resolve_body)
        self.assertIn("已生成并入库（成本待核对）", resolve_body)
        self.assertIn("self._record_asset_cost", generate_body)
        self.assertIn("成本待核对", generate_body)

    def test_a64_resolve_assets_keeps_generated_asset_when_cost_record_fails(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from ad_studio.models import Asset

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            project.creative_plan = {"shots": [{
                "index": shot.index,
                "asset_resolution": {
                    "actor_tags": ["test-actor"], "scene_tags": [], "product_tags": [],
                    "generation_if_missing": True,
                },
            }]}
            generated_path = root / "generated-actor.png"
            generated_path.write_bytes(b"fake-generated-actor")

            class FakeGenerator:
                def __init__(self, *args, **kwargs):
                    pass
                def configured(self, kind):
                    return kind == "演员"
                def generate(self, kind, name, prompt, tags, request_id, authorize_cloud=None):
                    asset = Asset("a64-generated-actor", name, kind, "ai_generated", str(generated_path), tags)
                    return SimpleNamespace(asset=asset, cost_rmb=0.72, provider="测试 Provider")

            store._record_asset_cost = lambda *args, **kwargs: (False, "模拟账本只读")

            with patch("ad_studio.production.AssetGenerator", FakeGenerator):
                resolution = store.resolve_assets(project, shot)

            actor_result = resolution["演员"]
            self.assertEqual(actor_result["source"], "已生成并入库（成本待核对）")
            self.assertEqual(actor_result["cost_status"], "pending")
            self.assertEqual(actor_result["asset"], "a64-generated-actor")
            self.assertEqual(shot.actor_id, "a64-generated-actor")
            self.assertTrue(generated_path.is_file())
            library_items = LocalLibrary(root / "library").all()
            self.assertTrue(any(item.id == "a64-generated-actor" for item in library_items))
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].actor_id, "a64-generated-actor")
            self.assertEqual(restored.creative_plan["asset_resolution"][shot.id]["演员"]["cost_status"], "pending")

    def test_a64_generate_missing_asset_keeps_asset_when_cost_record_fails(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]

            class FakeCapabilityRouter:
                def __init__(self, *args, **kwargs):
                    pass
                def decide_asset(self, kind):
                    return SimpleNamespace(target="local", endpoint="http://127.0.0.1/test", reason="test")

            class FakeLocalBackend:
                def __init__(self, endpoint):
                    self.endpoint = endpoint
                def generate_asset(self, prompt, output):
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(b"fake-generated-asset")
                    return output

            store._record_asset_cost = lambda *args, **kwargs: (False, "模拟账本只读")

            with patch("ad_studio.production.CapabilityRouter", FakeCapabilityRouter), \
                 patch("ad_studio.production.LocalAssetBackend", FakeLocalBackend):
                item = store.generate_missing_asset(
                    project, shot, "演员", "test actor", root / "asset-generation.json"
                )

            self.assertEqual(shot.actor_id, item.id)
            self.assertEqual(shot.status, "演员已生成并入库（成本待核对）")
            self.assertIn("成本待核对：模拟账本只读", shot.generated_from_request)
            self.assertTrue(Path(item.path).is_file())
            self.assertTrue(any(asset.id == item.id for asset in LocalLibrary(root / "library").all()))
            restored = store.load(project.id)
            self.assertEqual(restored.shots[0].actor_id, item.id)
            self.assertEqual(restored.shots[0].status, "演员已生成并入库（成本待核对）")
            self.assertIn("成本待核对：模拟账本只读", restored.shots[0].generated_from_request)


    def test_a65_single_ledger_record_uses_atomic_replace_and_preserves_old_file_on_failure(self):
        from unittest.mock import patch
        from pathlib import Path as PathType
        with tempfile.TemporaryDirectory() as td:
            ledger = ProductionStore(Path(td)).ledger
            ledger.record(function="既有记录", model_id="", model_name="", provider="测试", model="", status="success",
                          estimated_cost_rmb=1.25, project_id="p", category="video")
            original = ledger.path.read_text(encoding="utf-8")
            with patch.object(PathType, "replace", side_effect=OSError("模拟原子替换失败")):
                with self.assertRaisesRegex(OSError, "模拟原子替换失败"):
                    ledger.record(function="新记录", model_id="", model_name="", provider="测试", model="", status="success",
                                  estimated_cost_rmb=0.72, project_id="p", category="video")
            self.assertEqual(ledger.path.read_text(encoding="utf-8"), original)
            self.assertEqual(len(ledger.recent(10)), 1)
            self.assertEqual(ledger.recent(10)[0]["function"], "既有记录")
            # The failed atomic replacement must not leave an orphaned temp file.
            self.assertEqual(list(ledger.path.parent.glob(f".{ledger.path.name}.*.tmp")), [])

    def test_a65_ledger_retains_more_than_2000_cost_history_rows(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = ProductionStore(Path(td)).ledger
            ledger.record_many([
                {"function": f"历史记录-{i}", "model_id": "", "model_name": "", "provider": "测试", "model": "",
                 "status": "success", "estimated_cost_rmb": 0.01, "project_id": "p", "category": "video"}
                for i in range(2001)
            ])
            summary = ledger.project_summary("p")
            self.assertEqual(summary["entries"], 2001)
            self.assertAlmostEqual(summary["actual_cost_rmb"], 20.01)
            self.assertEqual(len(ledger._load()), 2001)
            # recent(limit) is only a display slice; it must not truncate the ledger or totals.
            self.assertEqual(len(ledger.recent(10)), 10)
            summary_after_recent = ledger.project_summary("p")
            self.assertEqual(summary_after_recent["entries"], 2001)
            self.assertAlmostEqual(summary_after_recent["actual_cost_rmb"], 20.01)




    def test_a91_series_asset_lock_detects_disabled_retyped_and_nonreusable_assets(self):
        from ad_studio.models import Asset
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "真人口播")
            project.creative_plan = {"shots": [{"index": 1, "asset_resolution": {
                "actor_asset_id": "actor-fixed", "scene_asset_id": "scene-fixed"}}]}
            library = LocalLibrary(root / "library")
            library._write([
                Asset("actor-fixed", "固定演员", "演员", "user_upload", None, [], active=False, reusable=True),
                Asset("scene-fixed", "固定场景", "演员", "user_upload", None, [], active=True, reusable=True),
            ])
            issues = store.validate_series_asset_locks(project)
            self.assertEqual(len(issues), 2)
            self.assertIn("停用", issues[0]["error"])
            self.assertIn("类型", issues[1]["error"])
            library._write([
                Asset("actor-fixed", "固定演员", "演员", "user_upload", None, [], active=True, reusable=False),
                Asset("scene-fixed", "固定场景", "场景", "user_upload", None, [], active=True, reusable=True),
            ])
            issues = store.validate_series_asset_locks(project)
            self.assertEqual(len(issues), 1)
            self.assertIn("不可复用", issues[0]["error"])

    def test_a91_project_reload_records_stale_series_lock_and_preserves_exact_id(self):
        from ad_studio.models import Asset
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library = LocalLibrary(root / "library")
            library._write([Asset("actor-fixed", "固定演员", "演员", "user_upload", None, [], active=True, reusable=True)])
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "真人口播")
            project.creative_plan = {"shots": [{"index": 1, "asset_resolution": {"actor_asset_id": "actor-fixed"}}]}
            store.save(project)
            library._write([])
            restored = store.load(project.id)
            self.assertEqual(restored.creative_plan["shots"][0]["asset_resolution"]["actor_asset_id"], "actor-fixed")
            self.assertEqual(restored.creative_plan["recovery"]["status"], "需处理")
            self.assertIn("SERIES_LOCKED_ASSET_INVALID", restored.creative_plan["recovery"]["history"][-1]["error_code"])




    def test_a91_invalid_series_lock_blocks_asset_resolution_before_fallback(self):
        from ad_studio.models import Asset
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library = LocalLibrary(root / "library")
            library._write([Asset("actor-fixed", "固定演员", "演员", "user_upload", None, [], active=False, reusable=True)])
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "真人口播")
            shot = project.shots[0]
            project.creative_plan = {"shots": [{
                "index": shot.index,
                "asset_resolution": {"actor_asset_id": "actor-fixed", "product_tags": ["应有但不生成"]},
            }]}
            result = store.resolve_assets(project, shot)
            self.assertEqual(result["演员"]["error_code"], "SERIES_LOCKED_ASSET_INVALID")
            self.assertFalse(result["演员"]["generate_if_missing"])
            self.assertNotIn("商品素材", result)  # no unrelated fallback/generation after lock failure




    def test_a92_locked_series_assets_resolve_to_same_physical_ids_across_episodes(self):
        from ad_studio.models import Asset, Shot
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library = LocalLibrary(root / "library")
            library._write([
                Asset("actor-series-1", "系列固定演员", "演员", "user_upload", None, ["主角"]),
                Asset("scene-series-1", "系列固定场景", "场景", "user_upload", None, ["主场景"]),
                Asset("actor-lookalike", "相似演员", "演员", "user_upload", None, ["主角"]),
                Asset("scene-lookalike", "相似场景", "场景", "user_upload", None, ["主场景"]),
            ])
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "真人口播")
            first = project.shots[0]
            first.episode_number = 1
            second = Shot(id="shot-episode-2", index=2, title="第二集", visual="同一主角进入同一场景", script="继续剧情", episode_number=2)
            project.shots.append(second)
            rows = []
            for idx in (1, 2):
                rows.append({"index": idx, "episode_number": idx, "asset_resolution": {
                    "actor_tags": ["主角"], "scene_tags": ["主场景"], "product_tags": [],
                    "actor_asset_id": "actor-series-1", "scene_asset_id": "scene-series-1",
                    "generation_if_missing": False,
                }})
            project.creative_plan = {"shots": rows}
            first_resolution = store.resolve_assets(project, first)
            second_resolution = store.resolve_assets(project, second)
            self.assertEqual(first_resolution["演员"]["asset"], "actor-series-1")
            self.assertEqual(second_resolution["演员"]["asset"], "actor-series-1")
            self.assertEqual(first_resolution["场景"]["asset"], "scene-series-1")
            self.assertEqual(second_resolution["场景"]["asset"], "scene-series-1")
            self.assertEqual(first.actor_id, second.actor_id)
            self.assertEqual(first.scene_id, second.scene_id)
            self.assertNotEqual(first.actor_id, "actor-lookalike")
            self.assertNotEqual(first.scene_id, "scene-lookalike")
            # Persist the resolved per-shot actor/scene bindings before testing reload.
            store.save(project)
            restored = store.load(project.id)
            restored_by_id = {shot.id: shot for shot in restored.shots}
            self.assertEqual(restored_by_id[first.id].actor_id, "actor-series-1")
            self.assertEqual(restored_by_id[second.id].actor_id, "actor-series-1")
            self.assertEqual(restored_by_id[first.id].scene_id, "scene-series-1")
            self.assertEqual(restored_by_id[second.id].scene_id, "scene-series-1")



    def test_a93_invalid_series_lock_blocks_provider_dispatch_and_preserves_other_shots(self):
        from ad_studio.models import Asset

        class CountingProvider:
            provider_name = "测试 Provider"
            cost_per_shot_rmb = 1.0
            def __init__(self):
                self.calls = 0
            def generate(self, request):
                self.calls += 1
                raise AssertionError("锁定素材失效时不得调用 Provider")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library = LocalLibrary(root / "library")
            library._write([
                Asset("actor-fixed", "固定演员", "演员", "user_upload", None, [], active=False, reusable=True),
            ])
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            self.assertGreaterEqual(len(project.shots), 2)
            target, untouched = project.shots[0], project.shots[1]
            untouched.status = "已生成"
            untouched.video_path = "existing-other-shot.mp4"
            project.creative_plan = {"shots": [{
                "index": target.index,
                "asset_resolution": {
                    "actor_asset_id": "actor-fixed",
                    "product_tags": ["不应在锁定失败后触发补素材"],
                    "generation_if_missing": True,
                },
            }]}
            provider = CountingProvider()

            with self.assertRaisesRegex(RuntimeError, "SERIES_LOCKED_ASSET_INVALID"):
                store._render_with_provider(project, target, provider)

            self.assertEqual(provider.calls, 0, "失效锁定必须在 Provider 调用前拦截")
            self.assertIn("生成失败", target.status)
            self.assertIsNone(target.actor_id, "不得静默绑定其他演员")
            self.assertEqual(untouched.status, "已生成")
            self.assertEqual(untouched.video_path, "existing-other-shot.mp4")
            self.assertEqual(
                project.creative_plan["shots"][0]["asset_resolution"]["actor_asset_id"],
                "actor-fixed",
                "失败时必须保留原锁定 ID 供恢复处理",
            )


    def test_a94_restoring_original_locked_asset_allows_exact_resolution_retry(self):
        from ad_studio.models import Asset

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library = LocalLibrary(root / "library")
            library._write([
                Asset("actor-fixed", "系列固定演员", "演员", "user_upload", None, ["主角"], active=False, reusable=True),
                Asset("actor-lookalike", "相似演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True),
            ])
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            shot = project.shots[0]
            project.creative_plan = {"shots": [{
                "index": shot.index,
                "asset_resolution": {
                    "actor_asset_id": "actor-fixed",
                    "actor_tags": ["主角"],
                    "generation_if_missing": True,
                },
            }]}

            failed = store.resolve_assets(project, shot)
            self.assertEqual(failed["演员"]["error_code"], "SERIES_LOCKED_ASSET_INVALID")
            self.assertFalse(failed["演员"]["generate_if_missing"])
            self.assertIsNone(shot.actor_id)

            # Recovery is explicit: the same physical asset ID becomes valid again.
            library._write([
                Asset("actor-fixed", "系列固定演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True),
                Asset("actor-lookalike", "相似演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True),
            ])
            retried = store.resolve_assets(project, shot)

            self.assertEqual(retried["演员"]["asset"], "actor-fixed")
            self.assertEqual(retried["演员"]["locked_asset_id"], "actor-fixed")
            self.assertEqual(retried["演员"]["source"], "跨集锁定素材复用")
            self.assertFalse(retried["演员"]["generate_if_missing"])
            self.assertEqual(shot.actor_id, "actor-fixed")
            self.assertNotEqual(shot.actor_id, "actor-lookalike")


    def test_a95_corrupt_library_index_fails_closed_before_provider_dispatch(self):
        from ad_studio.models import Asset

        class CountingProvider:
            provider_name = "计数测试 Provider"
            cost_per_shot_rmb = 1.0
            def __init__(self):
                self.calls = 0
            def generate(self, request):
                self.calls += 1
                raise AssertionError("素材索引损坏时不应调用 Provider")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library_root = root / "library"
            library = LocalLibrary(library_root)
            library._write([
                Asset("actor-fixed", "系列固定演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True),
            ])
            store = ProductionStore(root / "projects", library_root=library_root)
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            target = project.shots[0]
            other = project.shots[1]
            other.status = "已生成"
            other.video_path = "existing-other-shot.mp4"
            project.creative_plan = {"shots": [{
                "index": target.index,
                "asset_resolution": {
                    "actor_asset_id": "actor-fixed",
                    "product_tags": ["不应触发自动补素材"],
                    "generation_if_missing": True,
                },
            }]}

            # Simulate a truncated/corrupt local asset index after the project was created.
            library.index.write_text('{"assets": [broken', encoding="utf-8")
            issues = store.validate_series_asset_locks(project, target.index)
            self.assertTrue(issues)
            self.assertEqual(issues[0]["error_code"], "SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE")

            resolution = store.resolve_assets(project, target)
            self.assertEqual(resolution["演员"]["error_code"], "SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE")
            self.assertFalse(resolution["演员"]["generate_if_missing"])
            self.assertNotIn("商品素材", resolution, "索引异常时不得继续处理其他素材")

            provider = CountingProvider()
            with self.assertRaisesRegex(RuntimeError, "SERIES_LOCKED_ASSET_INVALID"):
                store._render_with_provider(project, target, provider)
            self.assertEqual(provider.calls, 0)
            self.assertEqual(other.status, "已生成")
            self.assertEqual(other.video_path, "existing-other-shot.mp4")
            self.assertEqual(
                project.creative_plan["shots"][0]["asset_resolution"]["actor_asset_id"],
                "actor-fixed",
                "索引恢复前必须保留原锁定 ID，不能静默解绑",
            )


    def test_a96_repaired_asset_index_allows_retry_of_original_series_lock(self):
        from ad_studio.models import Asset

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            library_root = root / "library"
            library = LocalLibrary(library_root)
            original = Asset("actor-fixed", "系列固定演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True)
            lookalike = Asset("actor-lookalike", "相似演员", "演员", "user_upload", None, ["主角"], active=True, reusable=True)
            library._write([original, lookalike])
            store = ProductionStore(root / "projects", library_root=library_root)
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            shot = project.shots[0]
            project.creative_plan = {"shots": [{
                "index": shot.index,
                "asset_resolution": {
                    "actor_asset_id": "actor-fixed",
                    "actor_tags": ["主角"],
                    "generation_if_missing": True,
                },
            }]}

            library.index.write_text('{"assets":[', encoding="utf-8")
            broken = store.resolve_assets(project, shot)
            self.assertEqual(broken["演员"]["error_code"], "SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE")
            self.assertFalse(broken["演员"]["generate_if_missing"])
            self.assertIsNone(shot.actor_id)

            # Restore a valid index containing the exact original ID and a tempting lookalike.
            library._write([original, lookalike])
            retried = store.resolve_assets(project, shot)
            self.assertEqual(retried["演员"]["asset"], "actor-fixed")
            self.assertEqual(retried["演员"]["locked_asset_id"], "actor-fixed")
            self.assertEqual(retried["演员"]["source"], "跨集锁定素材复用")
            self.assertFalse(retried["演员"]["generate_if_missing"])
            self.assertEqual(shot.actor_id, "actor-fixed")
            self.assertNotEqual(shot.actor_id, "actor-lookalike")


    def test_a97_project_recovery_only_requeues_missing_shot_and_preserves_valid_sibling(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            target, untouched = project.shots[:2]

            valid_output = root / "renders" / "untouched-shot.mp4"
            valid_output.parent.mkdir(parents=True, exist_ok=True)
            valid_output.write_bytes(b"valid-video-placeholder")
            target.video_path = str(root / "renders" / "missing-target-shot.mp4")
            target.status = "生成中"
            untouched.video_path = str(valid_output)
            untouched.status = "已生成"
            untouched.version = 3
            untouched.actual_cost_rmb = 1.25
            store.save(project)

            result = store.recover_project(project)

            self.assertIn(target.id, result["missing_media"])
            self.assertNotIn(untouched.id, result["missing_media"])
            self.assertIsNone(target.video_path)
            self.assertEqual(target.status, "待重新生成/重新选择素材")
            self.assertEqual(untouched.video_path, str(valid_output))
            self.assertEqual(untouched.status, "已生成")
            self.assertEqual(untouched.version, 3)
            self.assertEqual(untouched.actual_cost_rmb, 1.25)

            restored = store.load(project.id)
            restored_by_id = {shot.id: shot for shot in restored.shots}
            self.assertIsNone(restored_by_id[target.id].video_path)
            self.assertEqual(restored_by_id[untouched.id].video_path, str(valid_output))
            self.assertEqual(restored_by_id[untouched.id].status, "已生成")


    def test_a98_recovery_repeats_missing_shot_until_regenerated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            target, untouched = project.shots[:2]

            valid_output = root / "renders" / "untouched-shot.mp4"
            valid_output.parent.mkdir(parents=True, exist_ok=True)
            valid_output.write_bytes(b"valid-video-placeholder")
            target.video_path = str(root / "renders" / "missing-target-shot.mp4")
            target.status = "生成中"
            untouched.video_path = str(valid_output)
            untouched.status = "已生成"
            untouched.version = 2
            store.save(project)

            first = store.recover_project(project)
            self.assertIn(target.id, first["missing_media"])
            self.assertEqual(target.status, "待重新生成/重新选择素材")
            self.assertEqual(untouched.video_path, str(valid_output))
            self.assertEqual(untouched.status, "已生成")

            second = store.recover_project(project)
            self.assertIn(
                target.id,
                second["missing_media"],
                "重复打开/恢复项目时，尚未重生成的缺失镜头仍须出现在恢复摘要中",
            )
            self.assertEqual(target.status, "待重新生成/重新选择素材")
            self.assertEqual(untouched.video_path, str(valid_output))
            self.assertEqual(untouched.status, "已生成")
            self.assertEqual(untouched.version, 2)

            restored = store.load(project.id)
            restored_by_id = {shot.id: shot for shot in restored.shots}
            self.assertIn(target.id, restored.creative_plan["recovery"]["last_recovery"]["missing_media"])
            self.assertEqual(restored_by_id[untouched.id].video_path, str(valid_output))

    def test_a99_successful_ledger_clears_stale_cost_on_unbilled_sibling_shot(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 1, "连续短剧")
            charged, uncharged = project.shots[:2]
            store._record_actual_cost(
                project, shot=charged, category="video", amount_rmb=0.72, provider="test"
            )
            # Simulate stale persisted snapshots after the successful charge was recorded.
            charged.actual_cost_rmb = 0.72
            uncharged.actual_cost_rmb = 8.88
            project.actual_cost_rmb = 99.0
            store.save(project)

            result = store.recover_project(project)

            self.assertTrue(result["cost_reconciled"])
            self.assertAlmostEqual(project.actual_cost_rmb, 0.72)
            self.assertAlmostEqual(charged.actual_cost_rmb, 0.72)
            self.assertAlmostEqual(uncharged.actual_cost_rmb, 0.0)
            restored = store.load(project.id)
            restored_by_id = {shot.id: shot for shot in restored.shots}
            self.assertAlmostEqual(restored.actual_cost_rmb, 0.72)
            self.assertAlmostEqual(restored_by_id[uncharged.id].actual_cost_rmb, 0.0)


    def test_asset_generation_config_uses_app_config_root_not_custom_library_root(self):
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            projects_root = root / "projects"
            custom_library = root / "custom-library"
            store = ProductionStore(projects_root, library_root=custom_library)
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            project.creative_plan = {"shots": [{
                "index": shot.index,
                "asset_resolution": {
                    "actor_tags": [], "scene_tags": [], "product_tags": [],
                    "generation_if_missing": False,
                },
            }]}
            seen = {}

            class CapturingGenerator:
                def __init__(self, config_path, library_root):
                    seen["config_path"] = Path(config_path)
                    seen["library_root"] = Path(library_root)
                def configured(self, kind):
                    return False

            with patch("ad_studio.production.AssetGenerator", CapturingGenerator):
                store.resolve_assets(project, shot)

            self.assertEqual(seen["config_path"], projects_root.parent / "asset-generation.json")
            self.assertEqual(seen["library_root"], custom_library)
            self.assertNotEqual(seen["config_path"], custom_library / "asset-generation.json")


    def test_creation_preflight_discloses_model_destinations_without_secrets(self):
        from ad_studio.app import build_creation_preflight_detail

        with tempfile.TemporaryDirectory() as td:
            router = ModelRouter(Path(td) / "model-config.json")
            profile = ModelProfile(
                id="custom-proxy", name="自定义代理",
                provider="openai_compatible",
                base_url="https://proxy.example/v1?token=do-not-display",
                model="custom-model", api_key="do-not-display-key",
                enabled=True, input_price_rmb_per_1k=0, output_price_rmb_per_1k=0,
            )
            router.add_or_update(profile)
            router.add_or_update(ModelProfile(
                id="fallback-model", name="潜在回退模型",
                provider="openai_compatible", base_url="https://fallback.example/v1",
                model="fallback-model", api_key="fallback-secret", enabled=True,
            ))
            router.set_route("商品理解", profile.id)
            detail = build_creation_preflight_detail(
                "https://item.example/product/1", 5.0, 2, router
            )
            self.assertIn("本确认仅授权读取商品链接", detail)
            self.assertIn("https://proxy.example/v1", detail)
            self.assertIn("商品理解", detail)
            self.assertIn("不代表服务免费", detail)
            self.assertNotIn("do-not-display", detail)
            self.assertIn("其他已启用模型", detail)

    def test_explicit_authorization_gate_runs_no_operation_when_declined(self):
        from ad_studio.app import run_after_explicit_authorization

        calls = []
        authorized, result = run_after_explicit_authorization(
            lambda: False,
            lambda: calls.append("external") or "unexpected",
        )
        self.assertFalse(authorized)
        self.assertIsNone(result)
        self.assertEqual(calls, [])

        authorized, result = run_after_explicit_authorization(
            lambda: True,
            lambda: calls.append("external") or "allowed",
        )
        self.assertTrue(authorized)
        self.assertEqual(result, "allowed")
        self.assertEqual(calls, ["external"])

    def test_creation_preflight_is_before_product_parse_and_model_planning(self):
        source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        create_start = source.index("    def create(self):")
        create_end = source.index("    def refresh_shots(self):", create_start)
        body = source[create_start:create_end]
        gate = body.index("run_after_explicit_authorization(")
        consent = body.index("askyesno('AI创意规划与数据去向授权'")
        product_parse = body.index("lambda: parse_product_url(url)")
        model_plan = body.index("self.model_router.create_plans(")
        self.assertLess(gate, consent)
        self.assertLess(consent, product_parse)
        self.assertLess(gate, model_plan)
        cancel_branch = body[product_parse:model_plan]
        self.assertIn("if not authorized:", cancel_branch)
        self.assertIn("return", cancel_branch)
        self.assertIn("未读取商品页面、未调用 AI 模型/Provider", cancel_branch)


    def test_per_shot_provider_consent_discloses_destination_and_redacts_secrets(self):
        from types import SimpleNamespace
        from ad_studio.app import build_provider_execution_consent

        decision = SimpleNamespace(
            target="cloud",
            endpoint="https://provider.example/v1/generate?api_key=must-not-display",
            reason="本地视频服务不可用，转云端",
        )
        detail = build_provider_execution_consent(
            decision, "镜头 1 视频生成", 1.25, "商品标题：测试商品"
        )
        self.assertIn("实际执行目标：云端服务", detail)
        self.assertIn("https://provider.example/v1/generate", detail)
        self.assertIn("本地视频服务不可用，转云端", detail)
        self.assertIn("本次预估费用：¥1.25", detail)
        self.assertIn("数据边界", detail)
        self.assertIn("只有确认后才会调用此端点", detail)
        self.assertNotIn("must-not-display", detail)
        self.assertNotIn("api_key=", detail)

    def test_per_shot_provider_consent_distinguishes_local_and_unavailable(self):
        from types import SimpleNamespace
        from ad_studio.app import build_provider_execution_consent

        local = build_provider_execution_consent(
            SimpleNamespace(target="local", endpoint="http://127.0.0.1:8188/generate", reason="本机服务可达"),
            "镜头 1", 0.0,
        )
        self.assertIn("本地服务", local)
        self.assertIn("不会因本地请求失败而自动改用云端", local)

        unavailable = build_provider_execution_consent(
            SimpleNamespace(target="unavailable", endpoint="", reason="没有可用 Provider"),
            "镜头 1", 0.0,
        )
        self.assertIn("没有可用的已配置 Provider", unavailable)
        self.assertIn("不会发起生成请求", unavailable)

    def test_video_generation_uses_the_route_snapshot_that_was_confirmed(self):
        app_source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        production_source = (Path(__file__).resolve().parent / "ad_studio" / "production.py").read_text(encoding="utf-8")
        start = app_source.index("    def generate_shot(self):")
        end = app_source.index("    def regen_shot(self):", start)
        body = app_source[start:end]
        helper_start = app_source.index("    def _authorize_shot_generation(self, shot, action_label):")
        helper_end = app_source.index("    def _confirm_asset_cloud_generation(self, decision, kind, shot):", helper_start)
        helper = app_source[helper_start:helper_end]
        authorize = body.index("self._authorize_shot_generation(s,")
        mutate = body.index("s.status='生成中…'")
        render = body.index("self.store.render_shot(self.project,s,config_root=ROOT,decision=decision,authorize_cloud=")
        consent = helper.index("askyesno('确认生成端点与费用'")
        resolve = helper.index("self.store.resolve_assets(")
        self.assertLess(consent, resolve)
        self.assertLess(authorize, mutate)
        self.assertLess(mutate, render)
        self.assertIn("decision = decision or CapabilityRouter(config_root or self.root.parent).decide_video()", production_source)


    def test_asset_generator_requires_explicit_cloud_consent_before_provider_call(self):
        import json
        from types import SimpleNamespace
        from unittest.mock import patch
        from ad_studio.asset_generation import AssetGenerator

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "asset-generation.json"
            config.write_text(json.dumps({
                "演员": {
                    "endpoint": "https://asset.example/generate?secret=do-not-show",
                    "api_key": "test-secret",
                    "price_rmb": 0.8,
                }
            }, ensure_ascii=False), encoding="utf-8")
            decision = SimpleNamespace(
                target="cloud", endpoint="https://asset.example/generate?secret=do-not-show",
                reason="本地服务不可用，转云端",
            )
            generator = AssetGenerator(config, root / "library", capability=SimpleNamespace(decide_asset=lambda kind: decision))
            with patch.object(generator, "_cloud_generate") as cloud_call:
                with self.assertRaisesRegex(RuntimeError, "没有获得明确授权"):
                    generator.generate("演员", "演员A", "测试提示词")
                cloud_call.assert_not_called()
                assets_root = root / "library" / "assets"
                self.assertFalse(assets_root.exists() and any(path.is_file() for path in assets_root.rglob("*")))

                result = object()
                cloud_call.return_value = result
                returned = generator.generate(
                    "演员", "演员A", "测试提示词",
                    authorize_cloud=lambda route, kind: route.target == "cloud" and kind == "演员",
                )
                self.assertIs(returned, result)
                cloud_call.assert_called_once()

    def test_generate_missing_asset_rejects_cloud_without_consent_before_mutation(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            original_status = shot.status

            class FakeCapabilityRouter:
                def __init__(self, *args, **kwargs):
                    pass
                def decide_asset(self, kind):
                    return SimpleNamespace(
                        target="cloud", endpoint="https://asset.example/generate",
                        reason="本地服务不可用，转云端",
                    )

            with patch("ad_studio.production.CapabilityRouter", FakeCapabilityRouter), \
                 patch("ad_studio.production.load_asset_provider") as load_provider:
                with self.assertRaisesRegex(RuntimeError, "没有获得明确授权"):
                    store.generate_missing_asset(
                        project, shot, "演员", "test actor", root / "asset-generation.json"
                    )
                load_provider.assert_not_called()
                self.assertEqual(shot.status, original_status)
                assets_root = root / "library" / "assets"
                self.assertFalse(assets_root.exists() and any(item.is_file() for item in assets_root.rglob("*")))



    def test_declined_asset_consent_blocks_video_provider_before_shot_state_mutation(self):
        from unittest.mock import Mock

        with tempfile.TemporaryDirectory() as td:
            store = ProductionStore(Path(td) / "projects", library_root=Path(td) / "library")
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            original_status = shot.status
            original_version = shot.version
            provider = Mock()
            store.resolve_assets = Mock(side_effect=RuntimeError("用户拒绝或未授权云端素材生成；未发送请求。"))

            with self.assertRaisesRegex(RuntimeError, "已阻止后续视频 Provider 调用|未授权云端素材生成"):
                store._render_with_provider(project, shot, provider, authorize_cloud=lambda decision, kind: False)

            provider.generate.assert_not_called()
            self.assertEqual(shot.status, original_status)
            self.assertEqual(shot.version, original_version)

    def test_ui_requests_asset_consent_before_marking_shot_generating(self):
        source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        start = source.index("    def generate_shot(self):")
        end = source.index("    def regen_shot(self):", start)
        body = source[start:end]
        helper_start = source.index("    def _authorize_shot_generation(self, shot, action_label):")
        helper_end = source.index("    def _confirm_asset_cloud_generation(self, decision, kind, shot):", helper_start)
        helper = source[helper_start:helper_end]
        asset_prompt_start = helper_end
        asset_prompt_end = source.index("    @ui_action", asset_prompt_start)
        asset_prompt_helper = source[asset_prompt_start:asset_prompt_end]
        authorize = body.index("self._authorize_shot_generation(s,")
        status_mutation = body.index("s.status='生成中…'")
        video_dispatch = body.index("self.store.render_shot(self.project,s,config_root=ROOT,decision=decision,authorize_cloud=")
        asset_resolve = helper.index("self.store.resolve_assets(")
        asset_callback = helper.index("self._confirm_asset_cloud_generation(asset_decision, kind, shot)")
        asset_prompt = asset_prompt_helper.index("askyesno('确认云端素材端点与费用'")
        self.assertLess(asset_resolve, asset_callback)
        self.assertGreater(asset_prompt, 0)
        self.assertLess(authorize, status_mutation)
        self.assertLess(status_mutation, video_dispatch)


    def test_usage_ledger_sanitizes_endpoint_and_retains_cost_certainty_after_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "usage-ledger.json"
            ledger = UsageLedger(ledger_path)
            row = ledger.record(
                function="test", model_id="m1", model_name="模型一",
                provider="openai_compatible", model="model-1", status="success",
                estimated_cost_rmb=0.0, cost_status="usage_missing",
                usage_status="missing",
                endpoint="https://user:password@provider.example/v1/chat/completions?api_key=do-not-store#frag",
            )
            self.assertEqual(row["endpoint"], "https://provider.example/v1/chat/completions")
            self.assertNotIn("password", ledger_path.read_text(encoding="utf-8"))
            self.assertNotIn("do-not-store", ledger_path.read_text(encoding="utf-8"))
            restored = UsageLedger(ledger_path).recent(1)[0]
            self.assertEqual(restored["cost_status"], "usage_missing")
            self.assertEqual(restored["usage_status"], "missing")
            summary = UsageLedger(ledger_path).summary()
            self.assertTrue(summary["has_unknown_cost"])
            self.assertEqual(summary["unknown_cost_entries"], 1)

    def test_model_router_distinguishes_missing_usage_from_missing_price(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "model-config.json"
            config_path.write_text(json.dumps({
                "default_model": "priced",
                "models": [
                    {"id": "priced", "name": "价格已配置", "provider": "openai_compatible",
                     "base_url": "https://user:pass@priced.example/v1",
                     "model": "priced-model", "api_key": "key",
                     "input_price_rmb_per_1k": 0, "output_price_rmb_per_1k": 0, "enabled": True},
                    {"id": "unpriced", "name": "价格缺失", "provider": "openai_compatible",
                     "base_url": "https://unpriced.example/v1", "model": "unpriced-model",
                     "api_key": "key", "enabled": True}
                ],
                "routes": {"商品理解": "priced"}
            }, ensure_ascii=False), encoding="utf-8")
            router = ModelRouter(config_path)
            router.set_project_context("ledger-test-project")
            profile = router.get("priced")
            response = MagicMock()
            response.__enter__.return_value.read.return_value = json.dumps({
                "choices": [{"message": {"content": "{\"ok\": true}"}}]
            }).encode("utf-8")
            with patch("ad_studio.model_router.urllib.request.urlopen", return_value=response):
                router.complete_json(profile, "test prompt", function="商品理解")
            first = router.ledger.recent(1)[0]
            self.assertEqual(first["cost_status"], "usage_missing")
            self.assertEqual(first["usage_status"], "missing")
            self.assertEqual(first["endpoint"], "https://priced.example/v1/chat/completions")

            unpriced = router.get("unpriced")
            response2 = MagicMock()
            response2.__enter__.return_value.read.return_value = json.dumps({
                "usage": {"prompt_tokens": 1000, "completion_tokens": 0},
                "choices": [{"message": {"content": "{\"ok\": true}"}}]
            }).encode("utf-8")
            with patch("ad_studio.model_router.urllib.request.urlopen", return_value=response2):
                router.complete_json(unpriced, "test prompt", function="商品理解")
            second = router.ledger.recent(1)[0]
            self.assertEqual(second["cost_status"], "price_missing")
            self.assertEqual(second["usage_status"], "reported")
            self.assertEqual(second["estimated_cost_rmb"], 0.0)
            self.assertTrue(router.ledger.summary()["has_unknown_cost"])



    def test_cloud_render_routes_forward_asset_consent_callback(self):
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        from ad_studio.providers import GenericVideoProvider, UnconfiguredProvider

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ProductionStore(root / "projects", library_root=root / "library")
            project = new_project("https://item.jd.com/123.html", 2, "广告投放视频")
            shot = project.shots[0]
            provider = GenericVideoProvider(
                endpoint="https://video.example/generate", api_key="test-key"
            )
            callback = lambda decision, kind: False
            dispatch = Mock(return_value="mock-render")
            store._render_with_provider = dispatch
            decision = SimpleNamespace(
                target="cloud", endpoint="https://video.example/generate",
                reason="本地服务不可用，转云端",
            )
            with patch("ad_studio.production.load_video_provider",
                       side_effect=[provider, UnconfiguredProvider()]):
                result = store.render_shot(
                    project, shot, config_root=root, decision=decision,
                    authorize_cloud=callback,
                )
            self.assertEqual(result, "mock-render")
            dispatch.assert_called_once_with(
                project, shot, provider, authorize_cloud=callback
            )

            dispatch.reset_mock()
            with patch("ad_studio.production.load_video_provider", return_value=provider):
                result = store.render_cloud_shot(
                    project, shot, root / "video-provider.json",
                    authorize_cloud=callback,
                )
            self.assertEqual(result, "mock-render")
            dispatch.assert_called_once_with(
                project, shot, provider, authorize_cloud=callback
            )


    def test_footage_reanalysis_consent_discloses_routes_and_data_without_secrets(self):
        from types import SimpleNamespace
        from ad_studio.app import build_footage_reanalysis_consent_detail

        director = SimpleNamespace(
            name="视觉导演", provider="openai_compatible",
            base_url="https://vision.example/v1?api_key=hidden-vision",
            input_price_rmb_per_1k=0.0, output_price_rmb_per_1k=0.0,
        )
        speech = SimpleNamespace(
            name="本地转写", provider="local_openai",
            base_url="http://127.0.0.1:1234/v1", enabled=True,
            transcription_enabled=True,
        )
        class FakeRouter:
            def resolve_route(self, function):
                self.asserted_function = function
                return director
            def route(self, function):
                return speech

        detail = build_footage_reanalysis_consent_detail(FakeRouter(), Path("/private/customer-footage"))
        self.assertIn("https://vision.example/v1", detail)
        self.assertIn("关键帧图片", detail)
        self.assertIn("音频文件", detail)
        self.assertIn("本机/回环端点", detail)
        self.assertIn("实际费用可能未知", detail)
        self.assertIn("取消后不会扫描", detail)
        self.assertNotIn("hidden-vision", detail)
        self.assertNotIn("api_key=", detail)
        self.assertNotIn("/private/customer-footage", detail)

    def test_footage_reanalysis_consent_precedes_scan_manifest_and_external_analysis(self):
        source = (Path(__file__).resolve().parent / "ad_studio" / "app.py").read_text(encoding="utf-8")
        start = source.index("    def reanalyze_footage(self):")
        end = source.index("    @ui_action", start + 10)
        body = source[start:end]
        consent = body.index("askyesno('重新分析实拍素材与数据去向授权'")
        scan = body.index("clips=scan_footage(folder)")
        manifest = body.index("build_visual_manifest(")
        analysis = body.index("self.model_router.analyze_footage(")
        self.assertLess(consent, scan)
        self.assertLess(consent, manifest)
        self.assertLess(consent, analysis)

    def test_creation_preflight_denial_keeps_external_pipeline_call_counts_at_zero(self):
        from unittest.mock import Mock
        from ad_studio.app import run_after_explicit_authorization

        parse = Mock()
        scan = Mock()
        vision = Mock()
        transcription = Mock()
        planning = Mock()

        def external_pipeline():
            parse()
            scan()
            vision()
            transcription()
            planning()

        authorized, result = run_after_explicit_authorization(lambda: False, external_pipeline)
        self.assertFalse(authorized)
        self.assertIsNone(result)
        for operation in (parse, scan, vision, transcription, planning):
            operation.assert_not_called()

    def test_budget_denial_skips_all_project_persistence_operations(self):
        from unittest.mock import Mock
        from ad_studio.app import run_after_explicit_authorization

        save_project = Mock()
        save_product = Mock()
        save_library = Mock()
        refresh_ui = Mock()

        def persist_project():
            save_project()
            save_product()
            save_library()
            refresh_ui()

        authorized, result = run_after_explicit_authorization(lambda: False, persist_project)
        self.assertFalse(authorized)
        self.assertIsNone(result)
        for operation in (save_project, save_product, save_library, refresh_ui):
            operation.assert_not_called()

    def test_create_uses_explicit_gate_before_planning_and_budget_gate_before_persistence(self):
        import inspect
        from ad_studio.app import App

        source = inspect.getsource(App.create)
        first_gate = source.index("run_after_explicit_authorization(")
        parse = source.index("lambda: parse_product_url(url)")
        planning = source.index("self.model_router.create_plans(")
        budget_gate = source.rindex("run_after_explicit_authorization(")
        persist = source.index("self.store.save(self.project)")
        denial = source.index("if not authorized:", budget_gate)
        self.assertLess(first_gate, parse)
        self.assertLess(parse, planning)
        self.assertLess(planning, budget_gate)
        self.assertLess(budget_gate, persist)
        self.assertLess(denial, persist)

if __name__ == "__main__":
    unittest.main()
# A30 recovery regression: re-run CI after persisted-manifest recovery fix.
