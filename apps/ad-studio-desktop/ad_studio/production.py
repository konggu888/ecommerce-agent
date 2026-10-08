from pathlib import Path
from typing import Any
import json
import shutil
import subprocess
import datetime
from .models import Project, Shot, accept_hybrid_generated_shot
from .ffmpeg import make_clip, concat
from .providers import GenerationRequest, load_video_provider, load_asset_provider
from .postprocess import process_shot
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
        return Project(**data)

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
        plan = project.creative_plan.setdefault("recovery", {})
        removed_parts = 0
        render_root = self.root / "renders" / project.id
        if render_root.exists():
            for part in render_root.rglob("*.part.mp4"):
                part.unlink(missing_ok=True)
                removed_parts += 1
        missing_media = []
        for shot in project.shots:
            if shot.video_path and not Path(shot.video_path).exists():
                missing_media.append(shot.id)
                shot.video_path = None
                shot.status = "待重新生成/重新选择素材"
        invalid_outputs = []
        for item in plan.get("final_output_history_records", []):
            if not isinstance(item, dict):
                continue
            path = Path(str(item.get("output_path") or ""))
            if item.get("delivery_status") == "可交付" and (not path.exists() or path.stat().st_size <= 0):
                item["delivery_status"] = "不可交付"
                item["recovery_reason"] = "最终输出文件缺失或为空"
                invalid_outputs.append(str(path))
        now = datetime.datetime.now().isoformat(timespec="seconds")
        plan.update({
            "status": "可继续",
            "stage": "恢复完成",
            "next_action": "从未完成阶段继续任务",
            "last_recovery": {"removed_temp_files": removed_parts, "missing_media": missing_media, "invalid_outputs": invalid_outputs, "updated_at": now},
            "updated_at": now,
        })
        self.save(project)
        return plan["last_recovery"]

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
        project.cost_estimate.setdefault("actual", {})
        project.cost_estimate["actual"] = summary
        project.cost_estimate["actual_cost_rmb"] = summary["actual_cost_rmb"]

    def _record_actual_cost(self, project: Project, *, shot: Shot | None, category: str, amount_rmb: float, provider: str, quantity: float = 1.0, unit_cost_rmb: float = 0.0, function: str = "生成任务"):
        amount = round(float(amount_rmb or 0), 6)
        self.ledger.record(
            function=function, model_id="", model_name="", provider=provider, model="",
            status="success", estimated_cost_rmb=amount,
            project_id=project.id, shot_id=shot.id if shot else "",
            category=category, quantity=quantity, unit_cost_rmb=unit_cost_rmb,
        )
        project.actual_cost_rmb = round(float(project.actual_cost_rmb or 0) + amount, 6)
        project.actual_cost_summary = self.ledger.project_summary(project.id)
        self.save(project)

    def mark_ready(self, project: Project, shot: Shot, output: Path):
        shot.video_path=str(output); shot.status='已生成'; self.save(project)

    def accept_hybrid_generated_task(self, project: Project, task: dict):
        """人工明确通过后，把混合生成素材纳入项目分镜并持久化。"""
        if not isinstance(task, dict):
            raise ValueError("缺口任务必须是字典")
        shots = accept_hybrid_generated_shot(task, project.shots)
        project.shots = shots
        self.save(project)
        return next((shot for shot in shots if str(shot.id) == str(task.get("accepted_shot_id"))), None)

    def resolve_assets(self, project: Project, shot: Shot):
        """本地优先；缺失时返回明确的生成需求。真正生成由对应生成器执行。"""
        library=LocalLibrary(self.library_root)
        resolution={}
        plan_shots=project.creative_plan.get("shots", []) if project.creative_plan else []
        ai=next((x for x in plan_shots if int(x.get("index", -1)) == shot.index), {})
        req=ai.get("asset_resolution", {}) or {}
        generator=AssetGenerator(self.library_root/'asset-generation.json',self.library_root)
        for kind, tags in (("演员", req.get("actor_tags", [])), ("场景", req.get("scene_tags", [])), ("商品素材", req.get("product_tags", []))):
            found=library.best_match(kind,tags)
            item={'asset':found.id if found else None,'source':'本地复用' if found else '待自动生成','generate_if_missing':bool(req.get('generation_if_missing', True))}
            if not found and item['generate_if_missing']:
                if generator.configured(kind):
                    item['source']='自动生成中'
                    try:
                        result=generator.generate(kind,project.product_name+'-'+kind,shot.visual+'；需求：'+'、'.join(tags),tags,shot.id)
                        library._write(library.all()+[result.asset])
                        item.update({'asset':result.asset.id,'source':'已生成并入库','cost_rmb':result.cost_rmb})
                        self._record_actual_cost(project, shot=shot, category='asset', amount_rmb=result.cost_rmb, provider=result.provider, quantity=1, unit_cost_rmb=result.cost_rmb, function=f'{kind}素材生成')
                    except Exception as exc:
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

    def generate_missing_asset(self, project: Project, shot: Shot, kind: str, request_text: str, asset_provider_path: Path):
        """缺少本地素材时自动生成，并永久登记到本地库。"""
        library=LocalLibrary(self.library_root)
        decision = CapabilityRouter(self.root.parent).decide_asset(kind)
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
        shot.actual_cost_rmb=round(shot.actual_cost_rmb+cost,4)
        self._record_actual_cost(
            project,
            shot=shot,
            category="asset",
            amount_rmb=cost,
            provider=provider_name,
            quantity=1,
            unit_cost_rmb=cost,
            function=f"{kind}素材生成",
        )
        shot.provider = provider_name
        shot.status=f'{kind}已生成并入库'
        self.save(project)
        return item

    def render_shot(self, project: Project, shot: Shot, provider_path: Path | None = None, config_root: Path | None = None):
        """本地/云端视频生成统一入口。

        clip_source == 'filmed' 时走用户拍摄素材剪辑（本地 FFmpeg 裁剪），
        不调用视频生成服务；否则按能力调度决策：
        本地视频服务可达且硬件不要求云端优先 → 本地；
        否则云端视频 Provider 已配置 → 云端；
        否则明确报错，不伪装成片。
        """
        if shot.clip_source == 'filmed':
            return self.render_footage_shot(project, shot)
        decision = CapabilityRouter(config_root or self.root.parent).decide_video()
        if decision.target == 'local':
            from .providers import GenericVideoProvider
            provider = GenericVideoProvider(
                endpoint=decision.endpoint,
                api_key='',
                cost_per_shot_rmb=0.0,
                provider_name='本地视频服务',
                require_key=False,
            )
            return self._render_with_provider(project, shot, provider)
        if decision.target == 'cloud':
            provider = load_video_provider(provider_path or (config_root or self.root.parent)/'video-provider.json')
            if isinstance(provider, type(load_video_provider(Path('__missing__')))):
                raise RuntimeError('尚未配置云端视频 Provider，且本地视频服务不可用。')
            return self._render_with_provider(project, shot, provider)
        raise RuntimeError(f'镜头生成不可用：{decision.reason}')

    def render_cloud_shot(self, project: Project, shot: Shot, provider_path: Path):
        provider=load_video_provider(provider_path)
        return self._render_with_provider(project, shot, provider)

    def _render_with_provider(self, project: Project, shot: Shot, provider):
        out=self.render_path(project,shot)
        # 先写临时文件，只有 Provider 完整成功后才替换正式版本。
        # 这样重新生成 v2 失败时，v1 仍保持可用，不会污染当前镜头。
        temp=out.with_suffix('.part.mp4')
        if temp.exists():
            temp.unlink()
        resolution=self.resolve_assets(project,shot)
        library=LocalLibrary(self.library_root)
        asset_ids=[x for x in [shot.actor_id,shot.scene_id,*shot.product_asset_ids] if x]
        asset_map={a.id:a for a in library.all()}
        asset_paths=[asset_map[x].path for x in asset_ids if x in asset_map and asset_map[x].path and Path(asset_map[x].path).exists()]
        prompt='\n'.join([f'标题：{shot.title}',f'画面：{shot.visual}',f'文案：{shot.script}'])
        previous_path=shot.video_path
        shot.status='生成中…'
        shot.provider=getattr(provider,'provider_name','Generic REST')
        shot.generated_from_request=prompt
        self.save(project)
        try:
            result=provider.generate(GenerationRequest(
                prompt=prompt,
                output=temp,
                duration=3,
                reference_assets=asset_ids,
                reference_asset_paths=asset_paths,
            ))
            result=Path(result)
            if not result.exists() or result.stat().st_size == 0:
                raise RuntimeError('视频 Provider 返回成功，但生成文件不存在或为空。')
            if out.exists():
                out.unlink()
            result.replace(out)
            video_cost=round(float(getattr(provider,'cost_per_shot_rmb',0.0)),4)
            shot.actual_cost_rmb=round(float(shot.actual_cost_rmb or 0.0)+video_cost,4)
            self._record_actual_cost(
                project,
                shot=shot,
                category="video",
                amount_rmb=video_cost,
                provider=getattr(provider,'provider_name','Generic REST'),
                quantity=1,
                unit_cost_rmb=video_cost,
                function="视频镜头生成",
            )
            self.mark_ready(project,shot,out)
            return out
        except Exception as exc:
            if temp.exists():
                temp.unlink()
            shot.video_path=previous_path
            shot.status='生成失败（已保留上一版本）' if previous_path else '生成失败'
            shot.provider=getattr(provider,'provider_name',shot.provider)
            self.save(project)
            raise RuntimeError(f'镜头 {shot.index} v{shot.version} 生成失败：{exc}') from exc

    def render_footage_shot(self, project: Project, shot: Shot):
        """从用户拍摄素材中裁剪出本镜头（本地 FFmpeg，不调用生成服务）。"""
        from .footage import trim_clip, FootageError
        if not shot.source_file or not Path(shot.source_file).exists():
            raise FootageError(f'素材文件不存在：{shot.source_file}。请检查素材文件夹。')
        out = self.render_path(project, shot)
        shot.status = '素材裁剪中…'
        shot.provider = '本地素材剪辑'
        self.save(project)
        try:
            ranges = getattr(shot, 'source_ranges', None) or []
            if len(ranges) <= 1:
                trim_clip(Path(shot.source_file), out, float(shot.source_start or 0.0), shot.source_duration)
            else:
                parts = []
                for idx, pair in enumerate(ranges, 1):
                    part = out.with_name(f'{out.stem}.part{idx:02d}.mp4')
                    trim_clip(Path(shot.source_file), part, float(pair[0]), float(pair[1]) - float(pair[0]))
                    parts.append(part)
                concat(parts, out)
                for part in parts:
                    if part.exists():
                        part.unlink()
        except Exception as exc:
            shot.status = '素材裁剪失败'
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

    def final_render_gate(self, project: Project) -> dict[str, Any]:
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
        reasons.extend([f"镜头{s.index}：AI生成镜头尚未通过人工复核" for s in project.shots if getattr(s,'clip_source','ai_generated')=='ai_generated' and getattr(s,'storyboard_review','不需要')=='待复核'])
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
            result["valid"] = True
            result["reason"] = "最终视频机器质检通过"
            return result
        except Exception as exc:
            result["reason"] = f"ffprobe质检失败：{exc}"
            return result

    def write_final_output_manifest(self, project: Project, output: Path, aspect: str, variant_index: int,
                                    shots: list[Shot], safety_gate: dict[str, Any], media_check: dict[str, Any]) -> Path:
        """保存最终交付清单，记录实际输出版本、镜头组成和机器质检结果。"""
        manifest_path = Path(output).with_suffix(".json")
        manifest = {
            "project_id": project.id, "variant_index": int(variant_index), "aspect": aspect,
            "output_path": str(output), "shot_count": len(shots),
            "shot_ids": [shot.id for shot in shots], "shot_indices": [shot.index for shot in shots],
            "safety_gate": safety_gate, "media_check": media_check,
            "delivery_status": "可交付" if bool(media_check.get("valid")) else "不可交付",
            "created_at": datetime.datetime.now().isoformat(timespec="microseconds"),
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        key = f"{int(variant_index)}|{aspect}"
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
                "output_path": str(path),
                "exists": path.exists(),
                "delivery_status": item.get("delivery_status", "未知"),
                "duration_seconds": (item.get("media_check") or {}).get("duration_seconds", 0),
                "shot_count": item.get("shot_count", 0),
                "created_at": item.get("created_at", ""),
            })
        return sorted(rows, key=lambda x: x.get("created_at", ""), reverse=True)

    def build_final(self, project: Project, aspect: str = "9:16", variant_index: int | None = None):
        gate=self.final_render_gate(project)
        if not gate['allowed']:
            raise RuntimeError(gate['message'] + ":\n" + "\n".join(f"- {x}" for x in gate['reasons']))
        shots=self.current_shots(project)
        if len(shots)!=len(project.shots):
            raise RuntimeError(f'还有 {len(project.shots)-len(shots)} 个镜头没有成片，暂不能输出最终广告')
        suffix=f'-v{int(variant_index)}' if variant_index else ''
        out=self.root/'final'/project.id/f'final-{aspect.replace(":", "x")}{suffix}.mp4'
        concat([Path(s.video_path) for s in shots],out)
        media_check=self.inspect_final_output(out, aspect)
        if not media_check["valid"]:
            if out.exists():
                out.unlink()
            raise RuntimeError("最终成片机器质检未通过：" + str(media_check["reason"]))
        self.write_final_output_manifest(
            project, out, aspect, int(variant_index or self._variant_index(project)),
            shots, gate, media_check,
        )
        return out