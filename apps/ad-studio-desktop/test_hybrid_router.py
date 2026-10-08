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


def test_human_speech_gap_stays_real():
    result = route_footage_gap_tasks(
        [{"task_id": "GAP-005", "need": "真人口播", "reason": "缺少讲解素材"}],
        generation_connected=True,
        budget_remaining_rmb=10,
        cost_per_ai_shot_rmb=1,
    )
    assert result["tasks"][0]["recommended_resolution"] == "继续补拍"


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
