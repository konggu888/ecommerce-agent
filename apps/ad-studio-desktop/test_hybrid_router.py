import unittest
"""实拍缺口混合路由回归测试。"""
from ad_studio.hybrid_router import route_footage_gap_tasks


def test_product_evidence_always_shoot():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-001", "need": "商品特写", "reason": "缺少真实商品证据"}],
        generation_connected=True,
        budget_remaining_rmb=10,
        cost_per_ai_shot_rmb=1,
    )
    task = result["tasks"][0]
    assert task["recommended_resolution"] == "继续补拍"
    assert task["generation_allowed"] is False
    assert result["counts"]["继续补拍"] == 1


def test_generic_gap_uses_ai_when_connected_and_budget_allows():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-002", "need": "生活方式辅助场景", "reason": "缺少通用氛围画面"}],
        generation_connected=True,
        budget_remaining_rmb=2,
        cost_per_ai_shot_rmb=1,
    )
    task = result["tasks"][0]
    assert task["recommended_resolution"] == "AI补镜头"
    assert task["generation_allowed"] is True
    assert task["estimated_cost_rmb"] == 1


def test_generic_gap_needs_manual_when_provider_missing():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-003", "need": "生活方式辅助场景", "reason": "缺少通用氛围画面"}],
        generation_connected=False,
        budget_remaining_rmb=10,
        cost_per_ai_shot_rmb=1,
    )
    task = result["tasks"][0]
    assert task["recommended_resolution"] == "需要人工确认"
    assert task["generation_allowed"] is False


def test_generic_gap_needs_manual_when_budget_insufficient():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-004", "need": "环境辅助画面", "reason": "缺少通用场景"}],
        generation_connected=True,
        budget_remaining_rmb=0.5,
        cost_per_ai_shot_rmb=1,
    )
    assert result["tasks"][0]["recommended_resolution"] == "需要人工确认"


def test_human_speech_gap_can_use_support_visuals():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-005", "need": "真人口播缺少配套画面", "reason": "缺少辅助视频"}],
        generation_connected=True,
        budget_remaining_rmb=10,
        cost_per_ai_shot_rmb=1,
    )
    task = result["tasks"][0]
    assert task["recommended_resolution"] == "AI补辅助画面"
    assert task["generation_mode"] == "仅辅助画面，不生成真人/真人声音"


class HybridReviewModelTests(unittest.TestCase):
    def test_generated_gap_stays_out_until_explicit_acceptance(self):
        task={'task_id':'GAP-001','recommended_resolution':'AI补镜头','generated_path':'/tmp/generated.mp4','status':'AI补镜头已生成'}
        self.assertFalse(task.get('accepted_into_storyboard',False)); task['review_status']='已拒绝'; self.assertFalse(task.get('accepted_into_storyboard',False))
    def test_acceptance_records_storyboard_link(self):
        task={'task_id':'GAP-002','recommended_resolution':'AI补镜头','generated_path':'/tmp/generated.mp4','status':'AI补镜头已生成'}
        task['review_status']='已通过'; task['accepted_into_storyboard']=True; task['accepted_shot_id']='hybrid-gap-002-v1'; self.assertTrue(task['accepted_into_storyboard']); self.assertEqual(task['accepted_shot_id'],'hybrid-gap-002-v1')
    def test_product_evidence_is_not_reviewable_as_ai_gap(self):
        task={'recommended_resolution':'继续补拍','generated_path':'/tmp/generated.mp4'}; self.assertNotEqual(task.get('recommended_resolution'),'AI补镜头')


class HybridGapPositionTests(unittest.TestCase):
    def test_target_position_is_optional_when_gap_cannot_be_mapped(self):
        task={'task_id':'GAP-003','target_shot_index':None}
        self.assertIsNone(task['target_shot_index'])

    def test_target_position_is_recorded_for_precise_insertion(self):
        task={'task_id':'GAP-004','target_shot_index':3}
        self.assertEqual(task['target_shot_index'],3)


class HybridVariantCacheTests(unittest.TestCase):
    def test_variant_cache_restores_inserted_extra_shot_by_stable_id(self):
        from ad_studio.models import restore_variant_shot_cache
        from ad_studio.models import Shot
        base=[Shot(id='shot-01',index=1,title='原镜头1',visual='画面1',script='文案1'), Shot(id='shot-02',index=2,title='原镜头2',visual='画面2',script='文案2')]
        saved=[
            {'id':'shot-01','index':1,'title':'原镜头1','status':'已生成'},
            {'id':'hybrid-gap-001-v1','index':2,'title':'AI补镜头','visual':'辅助画面','script':'','status':'已复核并纳入分镜','video_path':'/tmp/generated.mp4','clip_source':'ai_generated'},
            {'id':'shot-02','index':3,'title':'原镜头2','status':'已生成'},
        ]
        restored=restore_variant_shot_cache(base,saved)
        self.assertEqual([s.id for s in restored],['shot-01','hybrid-gap-001-v1','shot-02'])
        self.assertEqual([s.index for s in restored],[1,2,3])
        self.assertEqual(restored[1].clip_source,'ai_generated')

    def test_variant_cache_without_saved_data_keeps_base_plan(self):
        from ad_studio.models import restore_variant_shot_cache
        from ad_studio.models import Shot
        base=[Shot(id='shot-01',index=1,title='原镜头1',visual='画面1',script='文案1')]
        restored=restore_variant_shot_cache(base,[])
        self.assertEqual([s.id for s in restored],['shot-01'])


class HybridGapInsertionOrderTests(unittest.TestCase):
    def test_multiple_insertions_use_stable_original_anchor(self):
        from ad_studio.models import Shot, find_variant_insert_position
        shots=[Shot(id='shot-01',index=1,title='1',visual='',script=''), Shot(id='shot-02',index=2,title='2',visual='',script=''), Shot(id='shot-03',index=3,title='3',visual='',script='')]
        first=find_variant_insert_position(shots,2)
        self.assertEqual(first,1)
        extra=Shot(id='hybrid-gap-a-v1',index=2,title='补镜头A',visual='',script='' )
        for s in shots[first:]: s.index+=1
        shots.insert(first,extra)
        second=find_variant_insert_position(shots,3)
        self.assertEqual(second,3)
        self.assertEqual(shots[second].id,'shot-03')


class HybridExecutionTests(unittest.TestCase):
    def test_execution_calls_generator_only_for_approved_tasks(self):
        from ad_studio.hybrid_router import execute_ai_gap_generation
        calls = []
        result = execute_ai_gap_generation(
            [{"task_id":"G1","recommended_resolution":"AI补镜头","generation_allowed":True}],
            generator=lambda task: calls.append(task["task_id"]) or "/tmp/g1.mp4",
            budget_remaining_rmb=2,
            cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(calls, ["G1"])
        self.assertEqual(result["generated"], 1)
        self.assertEqual(result["tasks"][0]["review_status"], "待复核")
        self.assertFalse(result["tasks"][0]["accepted_into_storyboard"])

    def test_execution_rechecks_budget_before_each_generation(self):
        from ad_studio.hybrid_router import execute_ai_gap_generation
        calls = []
        result = execute_ai_gap_generation(
            [
                {"task_id":"G1","recommended_resolution":"AI补镜头","generation_allowed":True},
                {"task_id":"G2","recommended_resolution":"AI补镜头","generation_allowed":True},
            ],
            generator=lambda task: calls.append(task["task_id"]) or "/tmp/x.mp4",
            budget_remaining_rmb=1,
            cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(calls, ["G1"])
        self.assertEqual(result["generated"], 1)
        self.assertEqual(result["blocked"], 1)

    def test_execution_never_generates_product_evidence(self):
        from ad_studio.hybrid_router import execute_ai_gap_generation
        calls = []
        result = execute_ai_gap_generation(
            [{"task_id":"G3","need":"商品特写","recommended_resolution":"AI补镜头","generation_allowed":True}],
            generator=lambda task: calls.append(task["task_id"]) or "/tmp/x.mp4",
            budget_remaining_rmb=10,
            cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(calls, [])
        self.assertEqual(result["blocked"], 1)

    def test_failed_generation_is_not_marked_generated(self):
        from ad_studio.hybrid_router import execute_ai_gap_generation
        result = execute_ai_gap_generation(
            [{"task_id":"G4","recommended_resolution":"AI补镜头","generation_allowed":True}],
            generator=lambda task: (_ for _ in ()).throw(RuntimeError("provider down")),
            budget_remaining_rmb=10,
            cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(result["failed"], 1)
        self.assertNotIn("generated_path", result["tasks"][0])
        self.assertFalse(result["tasks"][0]["accepted_into_storyboard"])

class HumanSupportMaterialTests(unittest.TestCase):
    def test_human_speech_gap_can_generate_non_human_support(self):
        from ad_studio.hybrid_router import route_footage_gap_tasks
        routed = route_footage_gap_tasks(
            [{"task_id":"VOICE-1","need":"真人口播缺少配套画面","reason":"口播素材不足，需要辅助视频"}],
            generation_connected=True, budget_remaining_rmb=2, cost_per_ai_shot_rmb=1,
        )
        task = routed["tasks"][0]
        self.assertEqual(task["recommended_resolution"], "AI补辅助画面")
        self.assertEqual(task["generation_mode"], "仅辅助画面，不生成真人/真人声音")
        self.assertTrue(task["generation_allowed"])

    def test_human_speech_without_provider_needs_manual_confirmation(self):
        from ad_studio.hybrid_router import route_footage_gap_tasks
        routed = route_footage_gap_tasks(
            [{"task_id":"VOICE-2","need":"真人出镜口播本身","reason":"缺少真人说话素材"}],
            generation_connected=False, budget_remaining_rmb=10, cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(routed["tasks"][0]["recommended_resolution"], "需要人工确认")
        self.assertFalse(routed["tasks"][0]["generation_allowed"])

    def test_product_evidence_with_human_words_still_requires_real_material(self):
        from ad_studio.hybrid_router import route_footage_gap_tasks
        routed = route_footage_gap_tasks(
            [{"task_id":"P-1","need":"真人讲解商品接口","reason":"需要真实操作证据"}],
            generation_connected=True, budget_remaining_rmb=10, cost_per_ai_shot_rmb=1,
        )
        self.assertEqual(routed["tasks"][0]["recommended_resolution"], "继续补拍")

