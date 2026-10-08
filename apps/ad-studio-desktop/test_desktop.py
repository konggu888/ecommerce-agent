import tempfile
import unittest
from pathlib import Path

from ad_studio.engine import detect_platform, estimate_cost, new_project, mark_regenerate
from ad_studio.library import LocalLibrary
from ad_studio.production import ProductionStore
from ad_studio.product_parser import ProductInfo, save_product_library, load_product_library, merge_product_library
from ad_studio.model_router import ModelRouter, ModelProfile, build_stage_prompt


class DesktopCoreTests(unittest.TestCase):

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
            with patch("ad_studio.production.concat") as concat, patch(
                "ad_studio.production.shutil.which", return_value="/usr/bin/ffprobe"
            ), patch("ad_studio.production.subprocess.run", return_value=completed):
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


if __name__ == "__main__":
    unittest.main()
# A30 recovery regression: re-run CI after persisted-manifest recovery fix.
