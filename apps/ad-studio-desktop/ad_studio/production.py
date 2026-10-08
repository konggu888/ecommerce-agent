from pathlib import Path
import json
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

    def render_path(self, project: Project, shot: Shot):
        folder=self.root/'renders'/project.id/shot.id
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
        out=self.root/'postprocessed'/project.id/shot.id/f'v{shot.version}-{aspect.replace(":", "x")}.mp4'
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

    def build_final(self, project: Project, aspect: str = "9:16", variant_index: int | None = None):
        shots=self.current_shots(project)
        if len(shots)!=len(project.shots):
            raise RuntimeError(f'还有 {len(project.shots)-len(shots)} 个镜头没有成片，暂不能输出最终广告')
        suffix=f'-v{int(variant_index)}' if variant_index else ''
        out=self.root/'final'/project.id/f'final-{aspect.replace(":", "x")}{suffix}.mp4'
        concat([Path(s.video_path) for s in shots],out)
        return out
