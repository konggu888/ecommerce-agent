from pathlib import Path
from typing import Any
import json
import shutil
import subprocess
import datetime
import math
from .models import Project, Shot, accept_hybrid_generated_shot
from .ffmpeg import make_clip, concat, concat_with_transitions
from .providers import GenerationRequest, load_video_provider, load_asset_provider
from .postprocess import process_shot, normalize_output_resolution
from .postprocess import probe_duration
from .music_sync import analyze_music_file, derive_content_minimum_durations, derive_subtitle_minimum_duration, plan_beat_aligned_durations, retime_clip, mix_global_bgm
from .subtitles import parse_srt_cues
from .library import LocalLibrary
from .asset_generation import AssetGenerator, LocalAssetBackend
from .hardware import detect_hardware
from .capability import CapabilityRouter
from .usage_ledger import UsageLedger

class ProductionStore:
    def __init__(self, root: Path, library_root: Path | None = None):
        self.root=root; self.root.mkdir(parents=True,exist_ok=True)
        self.library_root=library_root or root
        self.ledger=UsageLedger(self.root/'usage-ledger.json')

    def save(self, project: Project):
        project.updated_at=datetime.datetime.now().isoformat(timespec='seconds')
        project.save(self.root)

    def load(self, project_id: str):
        p=self.root/f'{project_id}.json'
        if not p.exists(): return None
        data=json.loads(p.read_text(encoding='utf-8'))
        data['shots']=[Shot(**s) for s in data.get('shots',[])]
        project = Project(**data)
        # Re-open is a trust boundary: re-check physical locks against the current library.
        issues = self.validate_series_asset_locks(project)
        if issues:
            self._record_series_lock_issues(project, issues, stage="项目重新打开时发现跨集锁定素材失效")
            self.save(project)
        return project

    def validate_series_asset_locks(self, project: Project, shot_index: int | None = None):
        """Re-check persisted physical actor/scene locks; fail closed on stale library state."""
        locked_rows = []
        for row in (project.creative_plan or {}).get("shots", []):
            try:
                row_index = int(row.get("index", -1))
            except (TypeError, ValueError):
                row_index = -1
            if shot_index is not None and row_index != int(shot_index):
                continue
            req = row.get("asset_resolution", {}) or {}
            for kind, key in (("演员", "actor_asset_id"), ("场景", "scene_asset_id")):
                asset_id = str(req.get(key) or "").strip()
                if asset_id:
                    locked_rows.append((row_index, kind, asset_id))
        if not locked_rows:
            return []
        try:
            by_id = {asset.id: asset for asset in LocalLibrary(self.library_root).all()}
        except Exception as exc:
            return [{"shot_index": idx, "kind": kind, "asset_id": aid,
                     "error_code": "SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE",
                     "error": f"跨集锁定素材库无法读取，已阻止继续制作：{exc}"}
                    for idx, kind, aid in locked_rows]
        issues = []
        for idx, kind, aid in locked_rows:
            asset = by_id.get(aid)
            if asset is None:
                reason = "素材记录不存在（可能已删除或索引已变化）"
            elif not asset.active:
                reason = "素材已停用"
            elif not asset.reusable:
                reason = "素材已设置为不可复用"
            elif asset.kind != kind:
                reason = f"素材类型已改变/不匹配（实际：{asset.kind}，要求：{kind}）"
            else:
                continue
            issues.append({"shot_index": idx, "kind": kind, "asset_id": aid,
                           "error_code": "SERIES_LOCKED_ASSET_INVALID",
                           "error": f"镜头 {idx} 的跨集锁定{kind}素材 {aid} 无效：{reason}；禁止替换或自动生成。"})
        return issues

    def _record_series_lock_issues(self, project: Project, issues: list[dict[str, Any]], *, stage: str):
        recovery = project.creative_plan.setdefault("recovery", {})
        history = recovery.setdefault("history", [])
        for issue in issues:
            signature = (issue.get("error_code"), issue.get("shot_index"), issue.get("asset_id"), issue.get("error"))
            if any((item.get("error_code"), item.get("shot_index"), item.get("asset_id"), item.get("error")) == signature
                   and item.get("status") in ("需处理", "待恢复") for item in history):
                continue
            history.append({**issue, "stage": stage, "retryable": False, "status": "需处理",
                            "next_action": "恢复/重新启用原锁定素材，或由用户明确修改锁定 ID；系统不会自动替换或生成。",
                            "created_at": datetime.datetime.now().isoformat(timespec="seconds")})
        if issues:
            recovery.update({"status": "需处理", "stage": stage,
                             "error": "；".join(issue["error"] for issue in issues),
                             "next_action": "检查本地素材库及原锁定素材，修复后只重试受影响镜头。",
                             "updated_at": datetime.datetime.now().isoformat(timespec="seconds")})

    def record_recovery_failure(self, project: Project, *, stage: str, error: str, next_action: str, retryable: bool = True):
        """统一记录可恢复失败；不清除已有有效资产，保存下一步动作。"""
        now = datetime.datetime.now().isoformat(timespec="seconds")
        plan = project.creative_plan.setdefault("recovery", {})
        history = plan.setdefault("history", [])
        record = {
            "stage": str(stage),
            "error": str(error),
            "retryable": bool(retryable),
            "next_action": str(next_action),
            "status": "待恢复" if retryable else "需处理",
            "created_at": now,
        }
        history.append(record)
        plan.update({"status": record["status"], "stage": record["stage"], "error": record["error"], "next_action": record["next_action"], "updated_at": now})
        self.save(project)
        return record

    def recover_project(self, project: Project):
        """恢复中断项目：清理未完成临时输出、校正失效媒体状态，并保留有效资产与历史。"""
        creative_plan = project.creative_plan
        recovery = creative_plan.setdefault("recovery", {})
        lock_issues = self.validate_series_asset_locks(project)
        if lock_issues:
            self._record_series_lock_issues(project, lock_issues, stage="中断项目恢复时发现跨集锁定素材失效")
        removed_parts = 0
        render_root = self.root / "renders" / project.id
        if render_root.exists():
            for part in render_root.rglob("*.part*.mp4"):
                part.unlink(missing_ok=True)
                removed_parts += 1
        missing_media = []
        restored_previous_versions = []
        for shot in project.shots:
            previous_path = str(getattr(shot, "previous_video_path", None) or "").strip()
            active_file = Path(shot.video_path) if shot.video_path else None
            active_missing = (
                active_file is None
                or not active_file.is_file()
                or active_file.stat().st_size <= 0
            )
            if previous_path and active_missing:
                previous_file = Path(previous_path)
                previous_is_valid = previous_file.is_file() and previous_file.stat().st_size > 0
                if previous_is_valid:
                    # A process may have stopped after version increment but before a new
                    # render completed. Restore the last known-good output after restart.
                    shot.video_path = previous_path
                    shot.previous_video_path = None
                    shot.status = "生成中断（已恢复上一版本）"
                    restored_previous_versions.append(shot.id)
                else:
                    # A stale pointer to a missing or zero-byte file is not recoverable.
                    shot.previous_video_path = None
                    shot.video_path = None
                    shot.status = "待重新生成/重新选择素材"
                    missing_media.append(shot.id)
            elif shot.video_path and (
                not Path(shot.video_path).is_file()
                or Path(shot.video_path).stat().st_size <= 0
            ):
                missing_media.append(shot.id)
                shot.video_path = None
                shot.status = "待重新生成/重新选择素材"
            elif (
                not shot.video_path
                and shot.status == "待重新生成/重新选择素材"
            ):
                # Keep recovery reporting idempotent: a second restart must not
                # make a previously detected missing output disappear from the
                # recovery summary before the user has regenerated that shot.
                missing_media.append(shot.id)
        invalid_outputs = []
        records = list(creative_plan.get("final_output_history_records", []) or [])
        manifests = creative_plan.get("final_output_manifests", {}) or {}
        if isinstance(manifests, dict):
            records.extend(manifests.values())
        seen = set()
        for item in records:
            if not isinstance(item, dict):
                continue
            output_path = str(item.get("output_path") or "")
            if output_path in seen:
                continue
            seen.add(output_path)
            path = Path(output_path)
            if item.get("delivery_status") == "可交付" and (not output_path or not path.exists() or path.stat().st_size <= 0):
                item["delivery_status"] = "不可交付"
                item["recovery_reason"] = "最终输出文件缺失或为空"
                invalid_outputs.append(output_path)
        cost_reconciled = self._sync_actual_cost(project)
        now = datetime.datetime.now().isoformat(timespec="seconds")
        recovery.update({
            "status": "可继续",
            "stage": "恢复完成",
            "next_action": "从未完成阶段继续任务",
            "last_recovery": {"removed_temp_files": removed_parts, "missing_media": missing_media, "restored_previous_versions": restored_previous_versions, "invalid_outputs": invalid_outputs, "cost_reconciled": cost_reconciled, "actual_cost_rmb": project.actual_cost_rmb, "updated_at": now},
            "updated_at": now,
        })
        self.save(project)
        return recovery["last_recovery"]

    def clear_recovery(self, project: Project):
        plan = project.creative_plan.setdefault("recovery", {})
        plan.update({"status": "正常", "stage": "", "error": "", "next_action": "继续当前任务", "updated_at": datetime.datetime.now().isoformat(timespec="seconds")})
        self.save(project)
        return plan

    def _variant_index(self, project: Project) -> int:
        """读取当前项目激活方案；所有物理媒体路径都必须带方案隔离。"""
        try:
            return max(1, int((project.creative_plan or {}).get('variant_index', 1) or 1))
        except (TypeError, ValueError):
            return 1

    def render_path(self, project: Project, shot: Shot):
        variant=self._variant_index(project)
        folder=self.root/'renders'/project.id/f'variant-{variant}'/shot.id
        folder.mkdir(parents=True,exist_ok=True)
        return folder/f'v{shot.version}.mp4'

    def current_shots(self, project: Project):
        """返回可进入最终成片的镜头，严格按分镜序号排序并执行审核闸门。"""
        shots = []
        for shot in sorted(project.shots, key=lambda x: x.index):
            if not shot.video_path or not Path(shot.video_path).exists():
                continue
            if getattr(shot, "clip_source", "ai_generated") == "ai_generated" and getattr(shot, "storyboard_review", "不需要") == "待复核":
                continue
            shots.append(shot)
        return shots

    def final_render_inputs(self, project: Project):
        """返回最终拼接实际消费的镜头路径，便于 UI/测试审计顺序。"""
        shots = self.current_shots(project)
        return [{"index": shot.index, "shot_id": shot.id, "path": str(shot.video_path)} for shot in shots]

    def _sync_actual_cost(self, project: Project):
        summary = self.ledger.project_summary(project.id)
        # If a ledger exists, it is the source of truth after an interrupted save.
        # Keep legacy totals intact for projects that predate the ledger entirely.
        # Failed-only history is not evidence of actual spend. If no successful
        # ledger entry exists, preserve legacy totals rather than resetting them to zero.
        reconciled = bool(summary.get("success", 0))
        if reconciled:
            project.actual_cost_rmb = summary["actual_cost_rmb"]
            project.actual_cost_summary = summary
            for shot in project.shots:
                shot_cost = self.ledger.shot_actual_cost(project.id, shot.id)
                # Once any successful ledger entry exists, the ledger is authoritative
                # for every shot: absence of a shot-level entry means zero recorded
                # spend, not permission to retain a stale snapshot amount.
                shot.actual_cost_rmb = float(shot_cost or 0.0)
        else:
            summary = dict(summary)
            summary["actual_cost_rmb"] = round(float(project.actual_cost_rmb or 0.0), 6)
            legacy_by_category = (project.actual_cost_summary or {}).get("by_category", {})
            if legacy_by_category:
                summary["by_category"] = legacy_by_category
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = summary
        project.cost_estimate["actual_cost_rmb"] = summary["actual_cost_rmb"]
        return reconciled

    def _ensure_legacy_cost_migrated(self, project: Project) -> bool:
        """Move legacy snapshot totals into the ledger once, before its first positive actual charge."""
        summary = self.ledger.project_summary(project.id)
        if float(summary.get("actual_cost_rmb", 0) or 0) > 0:
            return False

        def safe_amount(value: Any) -> float:
            try:
                amount = float(value or 0)
            except (TypeError, ValueError, OverflowError):
                return 0.0
            return amount if math.isfinite(amount) and amount > 0 else 0.0

        old_summary = project.actual_cost_summary if isinstance(project.actual_cost_summary, dict) else {}
        project_total = max(
            safe_amount(project.actual_cost_rmb),
            safe_amount(old_summary.get("actual_cost_rmb", 0)),
        )
        shot_amounts = []
        for shot in project.shots:
            amount = safe_amount(getattr(shot, "actual_cost_rmb", 0))
            if amount > 0:
                shot_amounts.append((shot, amount))
        shot_total = round(sum(amount for _, amount in shot_amounts), 6)
        total_to_preserve = max(project_total, shot_total)
        if total_to_preserve <= 0:
            return False

        records = []
        for shot, amount in shot_amounts:
            records.append({
                "function": "历史实际成本迁移",
                "model_id": "",
                "model_name": "历史记录",
                "provider": "本地迁移",
                "model": "",
                "status": "success",
                "estimated_cost_rmb": amount,
                "project_id": project.id,
                "shot_id": shot.id,
                "category": "legacy",
                "quantity": 1,
                "unit_cost_rmb": amount,
                "error": "从旧项目镜头成本快照迁移；不是新扣款",
            })
        residual = round(max(0.0, total_to_preserve - shot_total), 6)
        if residual > 0:
            records.append({
                "function": "历史实际成本迁移",
                "model_id": "",
                "model_name": "历史记录",
                "provider": "本地迁移",
                "model": "",
                "status": "success",
                "estimated_cost_rmb": residual,
                "project_id": project.id,
                "shot_id": "",
                "category": "legacy",
                "quantity": 1,
                "unit_cost_rmb": residual,
                "error": "从旧项目总成本快照迁移未分配金额；不是新扣款",
            })
        if not records:
            return False
        # One atomic write makes the migration idempotent even if the process exits.
        self.ledger.record_many(records)
        # Persist the migrated baseline in memory immediately. If the next charge
        # cannot be written, the caller can still save the preserved historical total.
        migrated_summary = self.ledger.project_summary(project.id)
        project.actual_cost_rmb = round(float(migrated_summary.get("actual_cost_rmb", 0) or 0), 6)
        project.actual_cost_summary = migrated_summary
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = migrated_summary
        project.cost_estimate["actual_cost_rmb"] = project.actual_cost_rmb
        for shot in project.shots:
            shot_cost = self.ledger.shot_actual_cost(project.id, shot.id)
            if shot_cost is not None:
                shot.actual_cost_rmb = shot_cost
        return True

    def _record_actual_cost(self, project: Project, *, shot: Shot | None, category: str, amount_rmb: float, provider: str, quantity: float = 1.0, unit_cost_rmb: float = 0.0, function: str = "生成任务"):
        amount = round(float(amount_rmb or 0), 6)
        self._ensure_legacy_cost_migrated(project)
        self.ledger.record(
            function=function, model_id="", model_name="", provider=provider, model="",
            status="success", estimated_cost_rmb=amount,
            project_id=project.id, shot_id=shot.id if shot else "",
            category=category, quantity=quantity, unit_cost_rmb=unit_cost_rmb,
        )
        summary = self.ledger.project_summary(project.id)
        # The usage ledger is authoritative; never increment a possibly stale project total.
        project.actual_cost_summary = summary
        project.actual_cost_rmb = round(float(summary.get("actual_cost_rmb", 0) or 0), 6)
        if shot:
            shot_actual = self.ledger.shot_actual_cost(project.id, shot.id)
            if shot_actual is not None:
                shot.actual_cost_rmb = shot_actual
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = summary
        project.cost_estimate["actual_cost_rmb"] = project.actual_cost_rmb
        self.save(project)

    def _record_failed_video_attempt(self, project: Project, shot: Shot, provider: Any, error: str):
        """Log a failed provider attempt without treating its quote as actual spend."""
        try:
            quoted_rate = float(getattr(provider, "cost_per_shot_rmb", 0.0) or 0.0)
        except (TypeError, ValueError, OverflowError):
            quoted_rate = 0.0
        if not math.isfinite(quoted_rate) or quoted_rate < 0:
            quoted_rate = 0.0
        provider_name = str(getattr(provider, "provider_name", "Generic REST") or "Generic REST")
        self.ledger.record(
            function="视频镜头生成",
            model_id="",
            model_name=provider_name,
            provider=provider_name,
            model="",
            status="failed",
            estimated_cost_rmb=0.0,
            project_id=project.id,
            shot_id=shot.id,
            category="video",
            quantity=1,
            unit_cost_rmb=round(quoted_rate, 6),
            error=error,
        )
        # Failed rows remain auditable without counting an unconfirmed charge
        # as actual spend; actual totals remain success-only.
        project.actual_cost_summary = self.ledger.project_summary(project.id)
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = project.actual_cost_summary
        project.cost_estimate["actual_cost_rmb"] = project.actual_cost_summary["actual_cost_rmb"]

    def mark_ready(self, project: Project, shot: Shot, output: Path):
        shot.video_path=str(output)
        shot.previous_video_path = None
        shot.status='已生成'
        self.save(project)

    def accept_hybrid_generated_task(self, project: Project, task: dict):
        """人工明确通过后，把混合生成素材纳入项目分镜并持久化。"""
        if not isinstance(task, dict):
            raise ValueError("缺口任务必须是字典")
        shots = accept_hybrid_generated_shot(task, project.shots)
        project.shots = shots
        self.save(project)
        return next((shot for shot in shots if str(shot.id) == str(task.get("accepted_shot_id"))), None)

    def _record_asset_cost(self, project: Project, shot: Shot, kind: str, amount_rmb: float, provider: str):
        """Keep successfully generated assets available when their cost write needs reconciliation."""
        try:
            self._record_actual_cost(
                project,
                shot=shot,
                category="asset",
                amount_rmb=amount_rmb,
                provider=provider,
                quantity=1,
                unit_cost_rmb=amount_rmb,
                function=f"{kind}素材生成",
            )
            return True, ""
        except Exception as exc:
            try:
                self.record_recovery_failure(
                    project,
                    stage=f"{kind}素材已生成但成本结算未完成",
                    error=str(exc),
                    next_action="核对 usage-ledger.json 与 Provider 账单；保留已生成素材，不要直接重复生成",
                    retryable=True,
                )
            except Exception as recovery_exc:
                project.creative_plan.setdefault("recovery", {}).setdefault("history", []).append({
                    "stage": f"{kind}素材已生成但成本结算未完成",
                    "error": str(exc),
                    "recovery_error": str(recovery_exc),
                    "retryable": True,
                    "status": "需处理",
                    "next_action": "检查本地项目文件与 usage-ledger.json 写入权限、磁盘空间，并核对 Provider 账单",
                    "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
                })
            return False, str(exc)

    def resolve_assets(self, project: Project, shot: Shot, authorize_cloud=None):
        """本地优先；缺失时返回明确的生成需求。真正生成由对应生成器执行。"""
        library=LocalLibrary(self.library_root)
        resolution={}
        plan_shots=project.creative_plan.get("shots", []) if project.creative_plan else []
        ai=next((x for x in plan_shots if int(x.get("index", -1)) == shot.index), {})
        req=ai.get("asset_resolution", {}) or {}
        generator=AssetGenerator(self.root.parent/'asset-generation.json',self.library_root)
        # Preflight all locks before resolving anything else. A stale series lock must
        # not cause unrelated missing assets to be generated as a side effect.
        preflight_issues = self.validate_series_asset_locks(project, shot.index)
        if preflight_issues:
            for issue in preflight_issues:
                kind = issue["kind"]
                resolution[kind] = {
                    "asset": None, "source": "跨集锁定素材无效", "generate_if_missing": False,
                    "locked_asset_id": issue.get("asset_id"), "error_code": issue["error_code"],
                    "error": issue["error"],
                }
            project.creative_plan.setdefault("asset_resolution", {})[shot.id] = resolution
            self._record_series_lock_issues(project, preflight_issues, stage="素材解析前发现跨集锁定素材失效")
            self.save(project)
            return resolution
        for kind, tags, lock_key in (("演员", req.get("actor_tags", []), "actor_asset_id"), ("场景", req.get("scene_tags", []), "scene_asset_id"), ("商品素材", req.get("product_tags", []), None)):
            locked_id = str(req.get(lock_key) or "").strip() if lock_key else ""
            if locked_id:
                # Explicit series identity locks are fail-closed: never substitute a lookalike
                # or trigger generation when the exact library record is unavailable.
                exact = next((asset for asset in library.all() if asset.id == locked_id), None)
                valid = bool(exact and exact.active and exact.reusable and exact.kind == kind)
                found = exact if valid else None
                item = {"asset": found.id if found else None, "source": "跨集锁定素材复用" if found else "跨集锁定素材无效", "generate_if_missing": False, "locked_asset_id": locked_id}
                if not found:
                    reason = "不存在" if exact is None else ("已停用" if not exact.active else ("不可复用" if not exact.reusable else f"类型不匹配（实际：{exact.kind}，要求：{kind}）"))
                    item.update({"error_code": "SERIES_LOCKED_ASSET_INVALID", "error": f"跨集锁定素材 {locked_id} {reason}；禁止自动替换或生成。"})
            else:
                found=library.best_match(kind,tags)
                item={'asset':found.id if found else None,'source':'本地复用' if found else '待自动生成','generate_if_missing':bool(req.get('generation_if_missing', True))}
            if not locked_id and not found and item['generate_if_missing']:
                if generator.configured(kind):
                    item['source']='自动生成中'
                    try:
                        result=generator.generate(kind,project.product_name+'-'+kind,shot.visual+'；需求：'+'、'.join(tags),tags,shot.id,authorize_cloud=authorize_cloud)
                        library._write(library.all()+[result.asset])
                        item.update({'asset':result.asset.id,'source':'已生成并入库','cost_rmb':result.cost_rmb})
                        cost_recorded, cost_error = self._record_asset_cost(project, shot, kind, result.cost_rmb, result.provider)
                        if not cost_recorded:
                            item.update({
                                'source': '已生成并入库（成本待核对）',
                                'cost_status': 'pending',
                                'cost_error': cost_error,
                            })
                    except Exception as exc:
                        if "没有获得明确授权" in str(exc):
                            # A declined consent is control flow, not an ordinary generation failure.
                            # Stop before trying other assets or dispatching a video Provider.
                            raise
                        item.update({'source':'自动生成失败','error':str(exc)})
                else:
                    item['source']='未配置生成服务'
            resolution[kind]=item
        if resolution['演员']['asset']: shot.actor_id=resolution['演员']['asset']
        if resolution['场景']['asset']: shot.scene_id=resolution['场景']['asset']
        if resolution['商品素材']['asset']:
            shot.product_asset_ids=[resolution['商品素材']['asset']]
        shot.asset_source='library' if all(x['asset'] for x in resolution.values()) else 'generate_missing'
        project.creative_plan.setdefault('asset_resolution', {})[shot.id]=resolution
        self.save(project)
        return resolution

    def generate_missing_asset(self, project: Project, shot: Shot, kind: str, request_text: str, asset_provider_path: Path, authorize_cloud=None):
        """缺少本地素材时自动生成，并永久登记到本地库。"""
        library=LocalLibrary(self.library_root)
        decision = CapabilityRouter(self.root.parent).decide_asset(kind)
        if decision.target == 'cloud' and (
            not callable(authorize_cloud) or not bool(authorize_cloud(decision, kind))
        ):
            raise RuntimeError(
                f'{kind}生成需要调用云端 Provider，但本次没有获得明确授权；未发送请求、未创建素材文件、未修改镜头状态。'
            )
        aid=shot.id + '-' + kind
        ext='.png'
        out=self.library_root/'assets'/kind/(aid+ext)
        out.parent.mkdir(parents=True,exist_ok=True)
        shot.status=f'{kind}自动生成中…'
        self.save(project)
        prompt=f'电商广告可复用{kind}素材。镜头：{shot.title}。画面需求：{shot.visual}。素材要求：{request_text}。保持主体稳定、适合后续视频生成与本地剪辑。'
        if decision.target == 'local':
            result = LocalAssetBackend(decision.endpoint).generate_asset(prompt, out)
            provider_name = '本地图像服务'
            cost = 0.0
        else:
            provider=load_asset_provider(asset_provider_path)
            if isinstance(provider, type(load_asset_provider(Path('__missing__')))):
                raise RuntimeError('尚未配置云端资产生成器，且本地素材服务不可用。')
            result=provider.generate_asset(GenerationRequest(prompt=prompt,output=out,reference_assets=[]))
            provider_name = getattr(provider, 'provider_name', '云端资产生成器')
            cost = float(getattr(provider, 'cost_per_asset_rmb', 0.0))
        item=library.register_generated(f'{kind}-{shot.index}',kind,result,tags=[request_text],request=prompt)
        if kind=='演员': shot.actor_id=item.id
        elif kind=='场景': shot.scene_id=item.id
        elif kind=='商品素材': shot.product_asset_ids.append(item.id)
        shot.asset_source='ai_generated'
        cost_recorded, cost_error = self._record_asset_cost(project, shot, kind, cost, provider_name)
        shot.provider = provider_name
        shot.status = f'{kind}已生成并入库' if cost_recorded else f'{kind}已生成并入库（成本待核对）'
        if not cost_recorded:
            shot.generated_from_request = f"{shot.generated_from_request or ''}\n成本待核对：{cost_error}".strip()
        self.save(project)
        return item

    def render_shot(self, project: Project, shot: Shot, provider_path: Path | None = None, config_root: Path | None = None, decision=None, authorize_cloud=None):
        """本地/云端视频生成统一入口。

        clip_source == 'filmed' 时走用户拍摄素材剪辑（本地 FFmpeg 裁剪），
        不调用视频生成服务；否则按能力调度决策：
        本地视频服务可达且硬件不要求云端优先 → 本地；
        否则云端视频 Provider 已配置 → 云端；
        否则明确报错，不伪装成片。
        """
        if shot.clip_source == 'filmed':
            return self.render_footage_shot(project, shot)
        # UI may pass the exact route snapshot the user approved; do not silently re-resolve to a different endpoint after consent.\n        decision = decision or CapabilityRouter(config_root or self.root.parent).decide_video()
        if decision.target == 'local':
            from .providers import GenericVideoProvider
            provider = GenericVideoProvider(
                endpoint=decision.endpoint,
                api_key='',
                cost_per_shot_rmb=0.0,
                provider_name='本地视频服务',
                require_key=False,
            )
            return self._render_with_provider(project, shot, provider, authorize_cloud=authorize_cloud)
        if decision.target == 'cloud':
            provider = load_video_provider(provider_path or (config_root or self.root.parent)/'video-provider.json')
            if isinstance(provider, type(load_video_provider(Path('__missing__')))):
                raise RuntimeError('尚未配置云端视频 Provider，且本地视频服务不可用。')
            return self._render_with_provider(project, shot, provider)
        raise RuntimeError(f'镜头生成不可用：{decision.reason}')

    def render_cloud_shot(self, project: Project, shot: Shot, provider_path: Path):
        provider=load_video_provider(provider_path)
        return self._render_with_provider(project, shot, provider)

    def _render_with_provider(self, project: Project, shot: Shot, provider, authorize_cloud=None):
        out = self.render_path(project, shot)
        temp = out.with_suffix(".part.mp4")
        previous_path = shot.video_path or getattr(shot, "previous_video_path", None)
        prompt = '\n'.join([f"标题：{shot.title}", f"画面：{shot.visual}", f"文案：{shot.script}"])
        provider_call_started = False
        try:
            # Resolve/reuse assets before changing shot state; cloud asset generation requires its own consent.
            # A rejected asset-consent prompt must stop the video request too, not silently continue without assets.
            resolution = self.resolve_assets(project, shot, authorize_cloud=authorize_cloud)
            denied = [item for item in resolution.values() if "没有获得明确授权" in str(item.get("error", ""))]
            if denied:
                raise RuntimeError("用户拒绝或未授权云端素材生成；已阻止后续视频 Provider 调用。")
            if temp.exists():
                temp.unlink()
            shot.status = "生成中…"
            shot.provider = getattr(provider, "provider_name", "Generic REST")
            shot.generated_from_request = prompt
            self.save(project)
            # Re-check immediately before Provider dispatch; asset state may have changed since load.
            lock_issues = self.validate_series_asset_locks(project, shot.index)
            resolution_issues = [item for item in resolution.values()
                                 if item.get("error_code") in ("SERIES_LOCKED_ASSET_INVALID", "SERIES_LOCKED_ASSET_LIBRARY_UNAVAILABLE")]
            if lock_issues or resolution_issues:
                issues = lock_issues + resolution_issues
                self._record_series_lock_issues(project, issues, stage="单镜头生成/重生成前拦截")
                self.save(project)
                raise RuntimeError("SERIES_LOCKED_ASSET_INVALID：跨集锁定素材已失效，已阻止当前镜头生成；未替换素材、未自动生成替代项。")
            library = LocalLibrary(self.library_root)
            asset_ids = [x for x in [shot.actor_id, shot.scene_id, *shot.product_asset_ids] if x]
            asset_map = {asset.id: asset for asset in library.all()}
            asset_paths = [
                asset_map[x].path for x in asset_ids
                if x in asset_map and asset_map[x].path and Path(asset_map[x].path).exists()
            ]
            request = GenerationRequest(
                prompt=prompt,
                output=temp,
                duration=max(1, int(getattr(shot, "duration_seconds", 3) or 3)),
                reference_assets=asset_ids,
                reference_asset_paths=asset_paths,
            )
            provider_call_started = True
            result = Path(provider.generate(request))
            if not result.is_file() or result.stat().st_size <= 0:
                raise RuntimeError("视频 Provider 返回成功，但生成文件不存在或为空。")
            result.replace(out)
        except Exception as exc:
            if "没有获得明确授权" in str(exc) or "用户拒绝或未授权云端素材生成" in str(exc):
                # Consent cancellation is not a provider failure and must not mutate shot state/version.
                temp.unlink(missing_ok=True)
                raise
            temp.unlink(missing_ok=True)
            previous_is_valid = bool(
                previous_path and Path(previous_path).is_file() and Path(previous_path).stat().st_size > 0
            )
            shot.video_path = str(previous_path) if previous_is_valid else None
            shot.previous_video_path = None
            shot.status = "生成失败（已保留上一版本）" if previous_is_valid else "生成失败"
            shot.provider = getattr(provider, "provider_name", shot.provider)
            if provider_call_started:
                try:
                    self._record_failed_video_attempt(project, shot, provider, str(exc))
                except Exception as ledger_exc:
                    project.creative_plan.setdefault("recovery", {}).setdefault("history", []).append({
                        "stage": "视频失败尝试记账",
                        "error": str(ledger_exc),
                        "original_error": str(exc),
                        "retryable": True,
                        "status": "需处理",
                        "next_action": "检查本地 usage-ledger.json 写入权限与磁盘空间",
                        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
                    })
            self.save(project)
            raise RuntimeError(f"镜头 {shot.index} v{shot.version} 生成失败：{exc}") from exc

        # Media generation succeeded. Do not route accounting errors through provider failure recovery.
        shot.video_path = str(out)
        shot.previous_video_path = None
        shot.status = "已生成"
        try:
            video_cost = normalize_cost_estimate_rmb(getattr(provider, "cost_per_shot_rmb", 0.0))
            self._record_actual_cost(
                project,
                shot=shot,
                category="video",
                amount_rmb=video_cost,
                provider=getattr(provider, "provider_name", "Generic REST"),
                quantity=1,
                unit_cost_rmb=video_cost,
                function="视频镜头生成",
            )
            self.mark_ready(project, shot, out)
        except Exception as ledger_exc:
            recovery = project.creative_plan.setdefault("recovery", {})
            recovery.setdefault("history", []).append({
                "stage": "视频已生成但成本记账待核对",
                "error": str(ledger_exc),
                "provider": str(getattr(provider, "provider_name", "Generic REST")),
                "shot_id": shot.id,
                "output_path": str(out),
                "quoted_cost_rmb": getattr(provider, "cost_per_shot_rmb", None),
                "retryable": False,
                "status": "需处理",
                "next_action": "先核对 usage-ledger.json 是否已写入成功记录，再人工修复项目成本汇总；禁止直接重试记账以免重复计费。",
                "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
            })
            shot.status = "已生成（成本待核对）"
            try:
                self.save(project)
            except Exception:
                pass
        return out

    def render_footage_shot(self, project: Project, shot: Shot):
        """从用户拍摄素材中裁剪出本镜头；临时输出成功后才替换正式版本。"""
        from .footage import trim_clip, FootageError
        previous_path = shot.video_path or getattr(shot, "previous_video_path", None)
        out = self.render_path(project, shot)
        temp = out.with_suffix(".part.mp4")
        if temp.exists():
            temp.unlink()
        if not shot.source_file or not Path(shot.source_file).exists():
            # A previous interrupted multi-range trim may leave .part01/.part02 files.
            for part in out.parent.glob(f"{out.stem}.part*.mp4"):
                part.unlink(missing_ok=True)
            previous_is_valid = bool(previous_path and Path(previous_path).is_file() and Path(previous_path).stat().st_size > 0)
            shot.video_path = str(previous_path) if previous_is_valid else None
            shot.previous_video_path = None
            shot.status = '素材裁剪失败（已保留上一版本）' if previous_is_valid else '素材裁剪失败'
            self.save(project)
            raise FootageError(f'素材文件不存在：{shot.source_file}。请检查素材文件夹。')
        shot.status = '素材裁剪中…'
        shot.provider = '本地素材剪辑'
        self.save(project)
        try:
            ranges = getattr(shot, "source_ranges", None) or []
            if len(ranges) <= 1:
                trim_clip(Path(shot.source_file), temp, float(shot.source_start or 0.0), shot.source_duration)
            else:
                parts = []
                for idx, pair in enumerate(ranges, 1):
                    part = out.with_name(f"{out.stem}.part{idx:02d}.mp4")
                    trim_clip(Path(shot.source_file), part, float(pair[0]), float(pair[1]) - float(pair[0]))
                    parts.append(part)
                concat(parts, temp)
                for part in parts:
                    part.unlink(missing_ok=True)
            if not temp.is_file() or temp.stat().st_size <= 0:
                raise FootageError("实拍素材裁剪未生成有效的视频文件。")
            # 临时文件与目标位于同一目录；原成片仅在新输出完整后原子替换。
            temp.replace(out)
        except Exception:
            temp.unlink(missing_ok=True)
            for part in out.parent.glob(f"{out.stem}.part*.mp4"):
                part.unlink(missing_ok=True)
            previous_is_valid = bool(previous_path and Path(previous_path).is_file() and Path(previous_path).stat().st_size > 0)
            shot.video_path = str(previous_path) if previous_is_valid else None
            shot.previous_video_path = None
            shot.status = '素材裁剪失败（已保留上一版本）' if previous_is_valid else '素材裁剪失败'
            self.save(project)
            raise
        self.mark_ready(project, shot, out)
        return out

    def render_placeholder_shot(self, project: Project, shot: Shot):
        out=self.render_path(project,shot)
        make_clip(out,3)
        self.mark_ready(project,shot,out)
        return out

    def postprocess_shot(self, project: Project, shot: Shot, aspect: str = "9:16", speed: float = 1.0):
        if not shot.video_path or not Path(shot.video_path).exists():
            raise RuntimeError("当前镜头还没有真实成片，不能做本地后处理")
        src=Path(shot.video_path)
        variant=self._variant_index(project)
        out=self.root/'postprocessed'/project.id/f'variant-{variant}'/shot.id/f'v{shot.version}-{aspect.replace(":", "x")}.mp4'
        profile = detect_hardware()
        shot.status=f'本地后处理中（策略：{profile.execution_mode}）'
        self.save(project)
        plan_shots=project.creative_plan.get("shots", []) if project.creative_plan else []
        ai=next((x for x in plan_shots if int(x.get("index", -1)) == shot.index), {})
        focus_x=float(ai.get("focus_x", getattr(shot, "focus_x", 0.5)))
        focus_y=float(ai.get("focus_y", getattr(shot, "focus_y", 0.5)))
        ai_speed=float(ai.get("speed", getattr(shot, "speed", speed)))
        transition=str(ai.get("transition", getattr(shot, "transition", "硬切")))
        process_shot(src,out,aspect,ai_speed,focus_x,focus_y,transition)
        shot.video_path=str(out)
        shot.status='已后处理'
        self.save(project)
        return out

    def final_render_gate(self, project: Project, episode_number: int | None = None) -> dict[str, Any]:
        """最终成片安全闸门：发现明确事实/视觉风险时阻止输出。"""
        plan = project.creative_plan or {}
        reasons = []
        fact = plan.get('creative_fact_audit') or {}
        for item in fact.get('variants', []) if isinstance(fact, dict) else []:
            for field, label in (("unsupported_selling_points", "商品资料未支持的卖点"),("forbidden_term_hits", "命中用户禁用词"),("absolute_or_high_risk_claims", "高风险绝对化表达")):
                values = item.get(field) or []
                if values: reasons.append(f"方案{item.get('variant_index','?')}：{label}：{'、'.join(map(str, values))}")
        visual = plan.get('visual_fact_audit') or {}
        for variant in visual.get('variants', []) if isinstance(visual, dict) else []:
            for shot in variant.get('shots', []) if isinstance(variant, dict) else []:
                risks = shot.get('risks') or []
                if risks: reasons.append(f"方案{variant.get('variant_index','?')}·{shot.get('source','未知素材')}：{'；'.join(map(str, risks))}")
        gate_shots = project.shots
        if episode_number is not None:
            gate_shots = [s for s in project.shots if int(getattr(s, "episode_number", 1) or 1) == int(episode_number)]
        reasons.extend([f"镜头{s.index}：AI生成镜头尚未通过人工复核" for s in gate_shots if getattr(s,'clip_source','ai_generated')=='ai_generated' and getattr(s,'storyboard_review','不需要')=='待复核'])
        return {'allowed': not reasons, 'reasons': reasons, 'checked': bool(fact or visual), 'message': '最终成片安全闸门通过' if not reasons else '最终成片被安全闸门拦截'}

    def inspect_final_output(self, output: Path, aspect: str) -> dict[str, Any]:
        """对已经输出的最终视频做机器可验证的交付检查。"""
        output = Path(output)
        result = {"valid": False, "path": str(output), "size_bytes": output.stat().st_size if output.exists() else 0,
                  "duration_seconds": 0.0, "width": 0, "height": 0, "aspect": aspect,
                  "video_stream": False, "reason": ""}
        if not output.exists() or result["size_bytes"] <= 0:
            result["reason"] = "最终视频文件不存在或为空"
            return result
        if not shutil.which("ffprobe"):
            result["reason"] = "未找到 ffprobe，无法完成最终视频机器质检"
            return result
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-print_format", "json",
                 "-show_entries", "format=duration:stream=codec_type,width,height", str(output)],
                check=True, capture_output=True, text=True,
            )
            data = json.loads(probe.stdout or "{}")
            video = next((x for x in data.get("streams", []) if x.get("codec_type") == "video"), None)
            if not video:
                result["reason"] = "最终文件没有可识别的视频流"
                return result
            result["video_stream"] = True
            result["width"] = int(video.get("width") or 0)
            result["height"] = int(video.get("height") or 0)
            result["duration_seconds"] = round(float((data.get("format") or {}).get("duration") or 0), 3)
            expected_w, expected_h = {"9:16": (9, 16), "16:9": (16, 9), "1:1": (1, 1)}.get(aspect, (0, 0))
            if not result["width"] or not result["height"] or result["duration_seconds"] <= 0:
                result["reason"] = "视频流尺寸或时长无效"
                return result
            if expected_w and abs((result["width"] / result["height"]) - (expected_w / expected_h)) > 0.03:
                result["reason"] = f"输出画幅与要求 {aspect} 不一致"
                return result
            minimum_width, minimum_height = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}.get(aspect, (1080, 1920))
            if result["width"] < minimum_width or result["height"] < minimum_height:
                result["reason"] = (
                    f"输出分辨率低于最低 1080P 要求（当前 {result['width']}×{result['height']}，"
                    f"至少需要 {minimum_width}×{minimum_height}）"
                )
                return result
            result["valid"] = True
            result["reason"] = "最终视频机器质检通过"
            return result
        except Exception as exc:
            result["reason"] = f"ffprobe质检失败：{exc}"
            return result

    def write_final_output_manifest(self, project: Project, output: Path, aspect: str, variant_index: int,
                                    shots: list[Shot], safety_gate: dict[str, Any], media_check: dict[str, Any],
                                    episode_number: int | None = None) -> Path:
        """保存最终交付清单，记录实际输出版本、镜头组成和机器质检结果。"""
        manifest_path = Path(output).with_suffix(".json")
        manifest = {
            "project_id": project.id, "variant_index": int(variant_index), "aspect": aspect,
            "episode_number": int(episode_number) if episode_number is not None else None,
            "output_path": str(output), "shot_count": len(shots),
            "shot_ids": [shot.id for shot in shots], "shot_indices": [shot.index for shot in shots],
            "safety_gate": safety_gate, "media_check": media_check,
            "delivery_status": "可交付" if bool(media_check.get("valid")) else "不可交付",
            "created_at": datetime.datetime.now().isoformat(timespec="microseconds"),
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        key = f"{int(variant_index)}|{aspect}" + (f"|ep{int(episode_number)}" if episode_number is not None else "")
        manifest["history_key"] = key
        manifest["revision_id"] = f"{key}|{manifest['created_at']}"
        project.creative_plan.setdefault("final_output_manifests", {})[key] = manifest
        project.creative_plan.setdefault("final_output_history_records", []).append(manifest.copy())
        self.save(project)
        return manifest_path

    def final_output_history(self, project: Project) -> list[dict[str, Any]]:
        """返回本项目已经通过安全闸门和媒体质检的最终输出历史。"""
        plan = project.creative_plan or {}
        history_records = plan.get("final_output_history_records") or []
        if history_records:
            items = [(str(item.get("history_key") or f"{item.get('variant_index','?')}|{item.get('aspect','?')}"), item) for item in history_records if isinstance(item, dict)]
        else:
            manifests = plan.get("final_output_manifests", {})
            items = [(key, item) for key, item in manifests.items()]
        rows = []
        for key, item in items:
            if not isinstance(item, dict):
                continue
            path = Path(str(item.get("output_path", "")))
            rows.append({
                "key": key,
                "revision_id": item.get("revision_id", ""),
                "variant_index": item.get("variant_index"),
                "aspect": item.get("aspect"),
                "episode_number": item.get("episode_number"),
                "output_path": str(path),
                "exists": path.exists(),
                "delivery_status": item.get("delivery_status", "未知"),
                "duration_seconds": (item.get("media_check") or {}).get("duration_seconds", 0),
                "shot_count": item.get("shot_count", 0),
                "created_at": item.get("created_at", ""),
            })
        return sorted(rows, key=lambda x: x.get("created_at", ""), reverse=True)

    def build_final(self, project: Project, aspect: str = "9:16", variant_index: int | None = None,
                    episode_number: int | None = None):
        gate=self.final_render_gate(project, episode_number=episode_number)
        if not gate['allowed']:
            raise RuntimeError(gate['message'] + ":\n" + "\n".join(f"- {x}" for x in gate['reasons']))
        expected_shots = project.shots
        if episode_number is not None:
            expected_shots = [s for s in project.shots if int(getattr(s, "episode_number", 1) or 1) == int(episode_number)]
            if not expected_shots:
                raise RuntimeError(f"项目中没有第{int(episode_number)}集的镜头。")
        current = self.current_shots(project)
        shots = current if episode_number is None else [
            s for s in current if int(getattr(s, "episode_number", 1) or 1) == int(episode_number)
        ]
        if len(shots) != len(expected_shots):
            missing = len(expected_shots) - len(shots)
            label = f"第{int(episode_number)}集" if episode_number is not None else "项目"
            raise RuntimeError(f'{label}还有 {missing} 个镜头没有成片，暂不能输出')
        suffix=f'-v{int(variant_index)}' if variant_index else ''
        episode_suffix=f'-ep{int(episode_number)}' if episode_number is not None else ''
        out=self.root/'final'/project.id/f'final-{aspect.replace(":", "x")}{episode_suffix}{suffix}.mp4'
        out.parent.mkdir(parents=True, exist_ok=True)
        concat_path = out.with_name(out.stem + ".concat.tmp.mp4")
        bgm_path = out.with_name(out.stem + ".bgm.tmp.mp4")
        normalized_path = out.with_name(out.stem + ".1080p.tmp.mp4")
        retimed_paths = []
        shot_transitions = [str(getattr(s, 'transition', '硬切') or '硬切') for s in shots]
        transition_safe = not any(value == '交叉溶解' for value in shot_transitions[1:])
        try:
            shot_paths = [Path(s.video_path) for s in shots]
            bgm_value = (project.creative_plan or {}).get("final_bgm_path")
            if bgm_value:
                bgm = Path(str(bgm_value)).expanduser()
                if not bgm.is_file() or bgm.stat().st_size <= 0:
                    raise RuntimeError(f"项目设置的全局BGM不存在或为空：{bgm}")
                analysis = analyze_music_file(bgm)
                original_durations = [probe_duration(path) for path in shot_paths]
                creative_rows = (project.creative_plan or {}).get("shots", [])
                rows_by_index = {}
                for row in creative_rows if isinstance(creative_rows, list) else []:
                    if isinstance(row, dict):
                        try:
                            rows_by_index[int(row.get("index", -1))] = row
                        except (TypeError, ValueError):
                            continue
                content_rows = []
                for shot in shots:
                    row = dict(rows_by_index.get(int(getattr(shot, "index", -1)), {}))
                    row["dialogue"] = row.get("dialogue") or getattr(shot, "script", "")
                    row["script"] = getattr(shot, "script", "")
                    row["visual"] = row.get("visual") or getattr(shot, "visual", "")
                    row["objective"] = row.get("objective") or getattr(shot, "title", "")
                    row["on_screen_text"] = row.get("on_screen_text") or []
                    row["product_asset_requirements"] = row.get("product_asset_requirements") or getattr(shot, "product_asset_ids", [])
                    row["cta_role"] = row.get("cta_role") or ""
                    row["editing_intent"] = row.get("editing_intent") or {}
                    content_rows.append(row)
                content_protection = derive_content_minimum_durations(content_rows, original_durations)
                subtitle_audit = []
                subtitle_map = (project.creative_plan or {}).get("subtitle_timing_by_shot", {})
                if not isinstance(subtitle_map, dict):
                    subtitle_map = {}
                combined_minimums = list(content_protection["minimum_durations"])
                for shot_index, (shot, clip_path, clip_duration) in enumerate(zip(shots, shot_paths, original_durations)):
                    record = subtitle_map.get(str(getattr(shot, "id", "")), {})
                    reason = "未找到与当前镜头版本绑定的 SRT 记录，沿用常规内容保护"
                    if isinstance(record, dict) and str(record.get("source_video_path", "")) == str(clip_path):
                        try:
                            recorded_duration = float(record.get("source_duration_seconds"))
                            if abs(recorded_duration - clip_duration) > 0.15:
                                raise ValueError("记录的字幕源时长与当前镜头不匹配")
                            srt_path = Path(str(record.get("srt_path", ""))).expanduser()
                            parsed = parse_srt_cues(srt_path, duration=clip_duration)
                            protection = derive_subtitle_minimum_duration(parsed["cues"], clip_duration)
                            if not protection["valid"]:
                                raise ValueError(protection["reason"])
                            combined_minimums[shot_index] = max(combined_minimums[shot_index], protection["minimum_duration"])
                            reason = protection["reason"]
                            subtitle_audit.append({
                                "shot_index": shot_index + 1, "status": "applied",
                                "srt_path": str(srt_path), "cue_count": parsed["cue_count"],
                                "shortest_cue_seconds": protection.get("shortest_cue_seconds"),
                                "minimum_duration": protection["minimum_duration"], "reason": reason,
                            })
                        except (OSError, ValueError, TypeError, KeyError) as exc:
                            reason = f"SRT 时间窗不可用，保守回退：{exc}"
                            subtitle_audit.append({"shot_index": shot_index + 1, "status": "fallback", "reason": reason})
                    else:
                        subtitle_audit.append({"shot_index": shot_index + 1, "status": "fallback", "reason": reason})
                plan = plan_beat_aligned_durations(original_durations, analysis.get("beats", []),
                                                   analysis.get("confidence", 0.0), allow_retime=transition_safe,
                                                   minimum_durations=combined_minimums)
                music_audit = {
                    "enabled": True, "path": str(bgm), "bpm": analysis.get("bpm"),
                    "confidence": analysis.get("confidence", 0.0), "changed": bool(plan.get("changed")),
                    "reason": plan.get("reason"), "beat_reason": analysis.get("reason"),
                    "original_durations": original_durations,
                    "planned_durations": plan.get("durations", original_durations),
                    "content_protection": content_protection["shots"],
                    "subtitle_timing_protection": subtitle_audit,
                }
                if plan.get("changed"):
                    adjusted_paths = []
                    for idx, (shot_path, original_duration, target_duration) in enumerate(
                            zip(shot_paths, original_durations, plan["durations"])):
                        speed = original_duration / target_duration
                        if abs(speed - 1.0) < 0.0075:
                            adjusted_paths.append(shot_path)
                            continue
                        retimed = out.with_name(f"{out.stem}.beat-shot-{idx + 1}.tmp.mp4")
                        retime_clip(shot_path, retimed, speed)
                        retimed_paths.append(retimed)
                        adjusted_paths.append(retimed)
                    shot_paths = adjusted_paths
                project.creative_plan["last_music_sync_audit"] = music_audit
            if any(value == '交叉溶解' for value in shot_transitions[1:]):
                concat_with_transitions(shot_paths, concat_path, shot_transitions, aspect=aspect)
            else:
                concat(shot_paths, concat_path)
            if bgm_value:
                mix_global_bgm(concat_path, Path(str(bgm_value)),
                               bgm_path, float((project.creative_plan or {}).get("final_bgm_volume", 0.16) or 0.16))
                normalize_output_resolution(bgm_path, normalized_path, aspect)
            else:
                normalize_output_resolution(concat_path, normalized_path, aspect)
            normalized_path.replace(out)
        finally:
            concat_path.unlink(missing_ok=True)
            bgm_path.unlink(missing_ok=True)
            normalized_path.unlink(missing_ok=True)
            for path in retimed_paths:
                path.unlink(missing_ok=True)
        media_check=self.inspect_final_output(out, aspect)
        if not media_check["valid"]:
            if out.exists():
                out.unlink()
            raise RuntimeError("最终成片机器质检未通过：" + str(media_check["reason"]))
        self.write_final_output_manifest(
            project, out, aspect, int(variant_index or self._variant_index(project)),
            shots, gate, media_check, episode_number=episode_number,
        )
        return out


def generation_failure_ui_state(shot: Shot) -> dict[str, Any]:
    """Return a truthful UI status after a generation failure, preserving a playable old output."""
    status = str(getattr(shot, "status", "") or "")
    video_path = str(getattr(shot, "video_path", None) or "").strip()
    has_previous_marker = "已保留上一版本" in status or "已恢复上一版本" in status
    if has_previous_marker and video_path:
        path = Path(video_path).expanduser()
        if path.is_file() and path.stat().st_size > 0:
            return {"status": status, "previous_version_available": True, "video_path": str(path)}
    return {"status": "生成失败", "previous_version_available": False, "video_path": ""}


def normalize_cost_estimate_rmb(value: Any) -> float:
    """Validate a provider's per-shot estimate before showing a cost confirmation dialog."""
    try:
        amount = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("预计生成费用无效；请先检查视频生成设置。") from exc
    if not math.isfinite(amount) or amount < 0:
        raise ValueError("预计生成费用必须是有限的非负数；请先检查视频生成设置。")
    return round(amount, 4)
