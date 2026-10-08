from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil
import subprocess
import json
from .library import LocalLibrary
from .engine import FORMS, new_project, mark_regenerate, estimate_cost, estimate_asset_generation
from .gpu import detect_gpu
from .hardware import detect_hardware, format_hardware
from .capability import CapabilityRouter
from .production import ProductionStore
from .product_parser import parse_product_url, save_product
from .creative_engine import CreativeEngine, validate_plan, validate_task_type_plan, TASK_TYPE_POLICIES
from .model_router import ModelRouter, ModelProfile, FUNCTIONS
from .browser_skill import _find_agent_browser
from .ffmpeg import available as ffmpeg_available, has_nvenc
from .providers import load_video_provider
from .footage import build_visual_manifest, footage_analysis_public, archive_analyzed_waste, classify_footage_gaps, build_footage_gap_tasks
from .transcription import extract_audio
from .ui_contract import verify_ui_action_contract, UIContractError, ui_action


class UnconfiguredCreativeLLM:
    def create_plan(self, product, constraints):
        raise RuntimeError(
            "尚未配置创意大模型。请在设置中接入 GPT、Claude、Gemini、国内模型或本地模型后再生成广告策略。"
        )


ROOT=Path(__file__).resolve().parents[1]/'data'/'ad-studio'
PROJECTS=ROOT/'projects'
LIBRARY_CONFIG=ROOT/'library-location.json'


class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title('AI 商品广告工厂 · 本地版'); self.geometry('1180x760'); self.minsize(980,650)
        self.library_root=self._load_library_root()
        self.lib=LocalLibrary(self.library_root); self.lib.ensure_defaults(); self.store=ProductionStore(PROJECTS, library_root=self.library_root); self.project=None
        self.model_router=ModelRouter(ROOT/'model-config.json')
        self.creative_engine=CreativeEngine(self.model_router)
        self.active_variant_index=1
        self.ui(); self.aspect=tk.StringVar(value='9:16'); self.refresh_assets(); self.refresh_gpu()

    def _load_library_root(self):
        default=ROOT/'library'
        if LIBRARY_CONFIG.exists():
            try:
                p=Path(json.loads(LIBRARY_CONFIG.read_text(encoding='utf-8')).get('path','')).expanduser()
                if str(p): return p
            except Exception:
                pass
        return default

    def _ui_execution_gate(self):
        """AI/出片关键操作前的 UI 硬闸门：后端存在不等于用户可操作。"""
        try:
            verify_ui_action_contract(Path(__file__))
            return True
        except (OSError, SyntaxError, UIContractError) as exc:
            messagebox.showerror('UI 操作入口检查失败', f'代码可能已经实现，但界面入口存在缺失或失配。\\n\\n{exc}\\n\\n必须先修复 UI，再执行本次操作。')
            return False

    @ui_action
    def asset_library_settings(self):
        win=tk.Toplevel(self); win.title('资产库硬盘位置'); win.geometry('760x280'); win.transient(self)
        frm=ttk.Frame(win,padding=16); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='本地资产库储存位置',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='演员、场景、商品素材、AI生成并入库的素材都会保存到这里。项目工程和成片仍保存在项目目录，两者分开。',wraplength=700).pack(anchor='w',pady=(4,12))
        var=tk.StringVar(value=str(self.library_root))
        row=ttk.Frame(frm); row.pack(fill='x')
        ttk.Entry(row,textvariable=var).pack(side='left',fill='x',expand=True)
        def choose():
            p=filedialog.askdirectory(title='选择资产库硬盘文件夹')
            if p: var.set(p)
        ttk.Button(row,text='选择硬盘目录',command=choose).pack(side='left',padx=8)
        status=tk.StringVar(value=f'当前资产数量：{len(self.lib.all())}')
        ttk.Label(frm,textvariable=status).pack(anchor='w',pady=10)
        def save_location():
            p=Path(var.get().strip()).expanduser()
            if not str(p): return messagebox.showerror('位置错误','请选择有效的硬盘目录。')
            try:
                p.mkdir(parents=True,exist_ok=True)
                # 新目录先建立索引；已有旧库不会被偷偷删除。
                LocalLibrary(p).ensure_defaults()
                LIBRARY_CONFIG.parent.mkdir(parents=True,exist_ok=True)
                LIBRARY_CONFIG.write_text(json.dumps({'path':str(p)},ensure_ascii=False,indent=2),encoding='utf-8')
                self.library_root=p; self.lib=LocalLibrary(p); self.lib.ensure_defaults()
                self.store.library_root=p; self.refresh_assets()
                status.set(f'已切换：{p} · {len(self.lib.all())} 个资产')
                messagebox.showinfo('已保存','资产库位置已切换。旧资产不会自动删除；如需搬迁，请先复制/移动原资产库。')
            except Exception as e:
                messagebox.showerror('保存失败',str(e))
        ttk.Button(frm,text='保存并切换',command=save_location).pack(anchor='e',pady=8)

    def ui(self):
        top=ttk.Frame(self,padding=16); top.pack(fill='x')
        ttk.Label(top,text='AI 商品广告工厂',font=('Microsoft YaHei UI',22,'bold')).pack(side='left')
        self.gpu_text=tk.StringVar(value='检测本地 GPU…'); ttk.Label(top,textvariable=self.gpu_text).pack(side='right')
        setup=ttk.LabelFrame(self,text='① 商品与广告策略',padding=12); setup.pack(fill='x',padx=16,pady=8)
        ttk.Label(setup,text='商品链接').grid(row=0,column=0,sticky='w'); self.url=tk.StringVar(); ttk.Entry(setup,textvariable=self.url,width=72).grid(row=0,column=1,columnspan=3,sticky='ew',padx=8)
        ttk.Label(setup,text='广告强度').grid(row=1,column=0,sticky='w'); self.level=tk.IntVar(value=2); ttk.Combobox(setup,textvariable=self.level,values=[1,2,3,4,5],state='readonly',width=8).grid(row=1,column=1,sticky='w')
        ttk.Label(setup,text='本次预算（¥）').grid(row=1,column=2,sticky='e'); self.budget=tk.StringVar(value='3'); ttk.Entry(setup,textvariable=self.budget,width=10).grid(row=1,column=3,sticky='w',padx=8)
        ttk.Label(setup,text='留空/自动：交给AI判断；手动选择仅作为约束').grid(row=1,column=2,columnspan=2,sticky='w')
        ttk.Label(setup,text='本次任务').grid(row=2,column=0,sticky='w'); self.task_type=tk.StringVar(value='电商短视频'); ttk.Combobox(setup,textvariable=self.task_type,values=['电商短视频','商品主图视频','广告投放视频'],state='readonly',width=18).grid(row=2,column=1,sticky='w'); ttk.Label(setup,text='每次只能选择一种任务').grid(row=2,column=2,columnspan=2,sticky='w')
        ttk.Label(setup,text='视频形式').grid(row=3,column=0,sticky='w'); self.form=tk.StringVar(value='AI自动选择'); ttk.Combobox(setup,textvariable=self.form,values=['AI自动选择']+FORMS,state='readonly',width=22).grid(row=2,column=1,sticky='w')
        ttk.Label(setup,text='创意方案数').grid(row=4,column=0,sticky='w'); self.variant_count=tk.StringVar(value='3'); ttk.Combobox(setup,textvariable=self.variant_count,values=['1','3'],state='readonly',width=8).grid(row=3,column=1,sticky='w'); ttk.Label(setup,text='3 = 同一商品自动生成三种明显不同的广告打法').grid(row=3,column=2,columnspan=3,sticky='w')
        ttk.Label(setup,text='素材来源').grid(row=5,column=0,sticky='w'); self.footage_mode=tk.StringVar(value='AI生成视频'); ttk.Combobox(setup,textvariable=self.footage_mode,values=['AI生成视频','用户拍摄素材'],state='readonly',width=16).grid(row=4,column=1,sticky='w',pady=(4,2))
        self.footage_folder=tk.StringVar(value=''); ttk.Entry(setup,textvariable=self.footage_folder,width=36).grid(row=5,column=2,sticky='w',padx=4); ttk.Button(setup,text='选择素材文件夹',command=self.choose_footage_folder).grid(row=4,column=3,sticky='e')
        ttk.Label(setup,text='用户拍摄素材：输入链接后 AI 分析产品 → 指定文件夹放入你拍好的视频 → AI 思考剪辑方案 → 本地 FFmpeg 出片（不调用视频生成服务）',foreground='#666').grid(row=6,column=0,columnspan=5,sticky='w',pady=(2,0))
        ttk.Button(setup,text='创建广告项目',command=self.create).grid(row=2,column=3,sticky='e'); ttk.Button(setup,text='📹 实拍分析报告',command=self.footage_analysis_report).grid(row=2,column=5,sticky='e',padx=8); ttk.Button(setup,text='📋 补素材任务',command=self.footage_gap_tasks_report).grid(row=2,column=6,sticky='e',padx=8); ttk.Button(setup,text='🔄 重新分析实拍素材',command=self.reanalyze_footage).grid(row=2,column=7,sticky='e',padx=8); ttk.Button(setup,text='🕘 分析历史',command=self.footage_reanalysis_history_report).grid(row=2,column=8,sticky='e',padx=8); ttk.Button(setup,text='打开已有项目',command=self.load_project).grid(row=2,column=2,sticky='e',padx=8); ttk.Button(setup,text='⚙ 模型设置',command=self.model_settings).grid(row=0,column=3,sticky='e'); ttk.Button(setup,text='🔎 系统状态',command=self.system_status).grid(row=1,column=3,sticky='e'); ttk.Button(setup,text='📊 AI调用记录',command=self.usage_view).grid(row=2,column=4,sticky='e',padx=8); ttk.Button(setup,text='🎬 视频生成设置',command=self.video_provider_settings).grid(row=0,column=4,sticky='e',padx=8); ttk.Button(setup,text='🧩 素材生成设置',command=self.asset_generation_settings).grid(row=1,column=4,sticky='e',padx=8)
        main=ttk.Panedwindow(self,orient='horizontal'); main.pack(fill='both',expand=True,padx=16,pady=8)
        left=ttk.Frame(main,padding=8); right=ttk.Frame(main,padding=8); main.add(left,weight=3); main.add(right,weight=2)
        ttk.Label(left,text='② 分镜生产链',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.shots=ttk.Treeview(left,columns=('v','status','actor','scene'),show='tree headings',height=17)
        for c,t,w in [('v','版本',70),('status','状态',90),('actor','演员',150),('scene','场景',150)]: self.shots.heading(c,text=t); self.shots.column(c,width=w)
        self.shots.column('#0',width=300); self.shots.pack(fill='both',expand=True,pady=8); self.shots.bind('<<TreeviewSelect>>',self.show_shot)
        bar=ttk.Frame(left); bar.pack(fill='x'); ttk.Button(bar,text='切换创意方案',command=self.switch_variant).pack(side='left'); ttk.Button(bar,text='生成本镜头',command=self.generate_shot).pack(side='left',padx=8); ttk.Button(bar,text='重新生成本镜头',command=self.regen_shot).pack(side='left',padx=8); ttk.Button(bar,text='▶ 本地硬件后处理',command=self.postprocess_selected).pack(side='left',padx=8); ttk.Button(bar,text='生成最终成片',command=self.final_render).pack(side='right',padx=8); ttk.Button(bar,text='保存项目',command=self.save).pack(side='right')
        ttk.Label(right,text='③ 本地资产库',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.assets=ttk.Treeview(right,columns=('kind','source','path'),show='tree headings',height=13)
        for c,t,w in [('kind','类型',80),('source','来源',90),('path','本地文件',300)]: self.assets.heading(c,text=t); self.assets.column(c,width=w)
        self.assets.column('#0',width=180); self.assets.pack(fill='both',expand=True,pady=8)
        ab=ttk.Frame(right); ab.pack(fill='x'); ttk.Button(ab,text='＋上传演员',command=lambda:self.upload('演员')).pack(side='left'); ttk.Button(ab,text='＋上传场景',command=lambda:self.upload('场景')).pack(side='left',padx=5); ttk.Button(ab,text='＋上传产品素材',command=lambda:self.upload('产品图')).pack(side='left'); ttk.Button(ab,text='＋上传BGM',command=lambda:self.upload('BGM')).pack(side='left',padx=5); ttk.Button(ab,text='刷新资产库',command=self.refresh_assets).pack(side='right')
        self.detail=tk.StringVar(value='等待创建项目'); ttk.Label(right,textvariable=self.detail,justify='left',wraplength=470).pack(fill='x',pady=10); ttk.Button(right,text='编辑当前分镜',command=self.edit_shot).pack(anchor='w',pady=4)
        self.cost=tk.StringVar(value='成本：尚未计算'); ttk.Label(right,textvariable=self.cost,font=('Microsoft YaHei UI',12,'bold')).pack(anchor='w')
        ttk.Label(self,text='本地存储：本机磁盘  |  资产库：永久复用  |  云端生成：仅在需要时调用',relief='sunken',anchor='w',padding=8).pack(fill='x',side='bottom')



    @ui_action
    def footage_analysis_report(self):
        """显示当前项目的实拍视觉分析、废片归档和口播转写结果。"""
        if not self.project:
            return messagebox.showinfo('提示', '请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        analysis=plan.get('footage_visual_analysis') or {}
        clips=analysis.get('clips') if isinstance(analysis, dict) else []
        clips=clips if isinstance(clips, list) else []
        archive=plan.get('footage_archive') or {}
        records=archive.get('records') if isinstance(archive, dict) else []
        records=records if isinstance(records, list) else []
        transcripts=plan.get('footage_transcripts') or []
        win=tk.Toplevel(self); win.title('实拍素材分析报告'); win.geometry('1080x700'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='实拍素材分析报告',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        archived=sum(1 for x in records if x.get('archived'))
        usable=sum(1 for x in clips if x.get('usable') is not False)
        recommended=analysis.get('recommended_duration_seconds','未提供') if isinstance(analysis,dict) else '未提供'
        coverage=plan.get('footage_coverage') or {}
        summary=(f'视觉分析：{len(clips)} 个｜当前可用：{usable} 个｜已归档废片：{archived} 个｜'
                 f'口播转写：{len(transcripts)} 个｜AI建议时长：{recommended} 秒｜'
                 f'卖点覆盖：{coverage.get("coverage_score", "未审计")}%｜开场候选：{coverage.get("opening_candidate") or "未找到"}')
        ttk.Label(frm,text=summary).pack(anchor='w',pady=(4,10))
        if isinstance(analysis,dict) and analysis.get('global_summary'):
            ttk.Label(frm,text='AI总体判断：'+str(analysis['global_summary']),wraplength=1020,justify='left').pack(anchor='w',pady=(0,10))
        missing=coverage.get('missing_key_shots', []) if isinstance(coverage,dict) else []
        missing_points=coverage.get('missing_selling_points', []) if isinstance(coverage,dict) else []
        gap_text='；'.join(str(x.get('need','')) for x in missing if isinstance(x,dict)) or '无'
        point_text='、'.join(map(str,missing_points)) or '无'
        ttk.Label(frm,text=f'覆盖审计：缺失关键镜头={gap_text}｜缺失卖点={point_text}',wraplength=1020,justify='left').pack(anchor='w',pady=(0,8))
        tree=ttk.Treeview(frm,columns=('source','rank','sel','score','usable','duplicate','take','reason','tags','ranges','speech'),show='headings')
        heads=[('source','素材',140),('rank','素材排名',70),('sel','综合分',70),('score','AI评分',60),('usable','是否可用',70),('duplicate','重复组',100),('take','最佳版本',80),('reason','判断原因',230),('tags','画面标签',180),('ranges','推荐片段',150),('speech','口播质量',90)]
        for col,title,width in heads:
            tree.heading(col,text=title); tree.column(col,width=width,anchor='w')
        tree.pack(fill='both',expand=True)
        for item in clips:
            ranges=item.get('best_ranges',[])
            ranges_text='；'.join(f"{float(x.get('start',0)):.1f}-{float(x.get('start',0))+float(x.get('duration',0)):.1f}s" for x in ranges if isinstance(x,dict))
            tree.insert('', 'end', values=(item.get('source','-'),item.get('material_rank','-'),item.get('selection_score','-'),item.get('score','-'),'是' if item.get('usable') is not False else '否',item.get('duplicate_group') or '-', '是' if item.get('best_take') else '否',str(item.get('reason','')), '、'.join(map(str,item.get('visual_tags',[]))),ranges_text,item.get('speech_quality','-')))
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=(10,0))

    @ui_action
    def footage_gap_tasks_report(self):
        """显示已确定的补拍/补素材任务；不产生新的 AI 调用。"""
        if not self.project:
            return messagebox.showinfo('提示', '请先创建或打开一个项目。')
        tasks_data=self.project.creative_plan.get('footage_gap_tasks') or {}
        tasks=tasks_data.get('tasks', []) if isinstance(tasks_data, dict) else []
        win=tk.Toplevel(self); win.title('补素材任务清单'); win.geometry('1120x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='补素材任务清单',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text=f"当前缺口任务：{len(tasks)} 个｜来源覆盖率：{tasks_data.get('source_coverage_score','未审计')}%｜不会在这里自动拍摄或生成").pack(anchor='w',pady=(4,10))
        tree=ttk.Treeview(frm,columns=('id','type','priority','need','point','action','acceptance'),show='headings')
        for c,t,w in [('id','任务',80),('type','处理方式',80),('priority','优先级',70),('need','缺口',180),('point','关联卖点',120),('action','怎么补',280),('acceptance','验收标准',300)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both',expand=True)
        for x in tasks:
            tree.insert('', 'end', values=(x.get('task_id','-'),x.get('type','-'),x.get('priority','-'),x.get('need','-'),x.get('related_selling_point','-'),x.get('shoot_or_generate','-'),x.get('acceptance','-')))
        ttk.Label(frm,text='闭环下一步：完成这些任务后，把新增素材放回原素材文件夹，再执行“重新分析实拍素材”，系统会重新进入视觉分析→素材排名→覆盖审计→分镜复核。',wraplength=1050,justify='left').pack(anchor='w',pady=10)
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e')
 
    @ui_action
    def reanalyze_footage(self):
        if not self._ui_execution_gate(): return
        """用户补充素材后，重新进入视觉分析→排名→覆盖审计→分镜复核闭环。"""
        if not self.project:
            return messagebox.showinfo('提示', '请先创建一个实拍素材项目。')
        if self.footage_mode.get().strip() != '用户拍摄素材':
            return messagebox.showinfo('提示', '请先把“素材来源”切换为“用户拍摄素材”。')
        folder=Path(self.project.footage_folder or self.footage_folder.get().strip()).expanduser()
        if not folder.exists() or not folder.is_dir():
            return messagebox.showerror('素材文件夹无效','当前项目的实拍素材文件夹不存在，请重新选择。')
        if not messagebox.askyesno('重新分析实拍素材',
            '将重新扫描当前文件夹中的视频，并重新执行视觉分析、废片归档、口播转写（如已配置）、素材排名、卖点覆盖审计和剪辑方案复核。是否继续？'):
            return
        try:
            from .footage import scan_footage, FootageError, validate_footage_plan, audit_footage_coverage, audit_final_footage_plan
            clips=scan_footage(folder)
            usable=[c for c in clips if c.duration>0]
            if not usable:
                return messagebox.showerror('没有可分析素材','当前文件夹中没有可解析的视频素材。')
            info=self.project.product_info or {}
            constraints=self._creative_constraints()
            analysis_dir=PROJECTS/self.project.id/'footage-analysis'
            manifest=build_visual_manifest(usable,analysis_dir,max_frames_per_clip=4)
            # 先留档上一轮状态，再覆盖本轮分析字段；失败时用户仍可追溯历史方案。
            previous_snapshot = {
                'footage_visual_analysis': self.project.creative_plan.get('footage_visual_analysis'),
                'footage_coverage': self.project.creative_plan.get('footage_coverage'),
                'footage_gaps': self.project.creative_plan.get('footage_gaps'),
                'footage_gap_tasks': self.project.creative_plan.get('footage_gap_tasks'),
                'footage_selection_audit': self.project.creative_plan.get('footage_selection_audit'),
                'footage_plan': self.project.creative_plan.get('footage_plan'),
            }
            if any(v is not None for v in previous_snapshot.values()):
                from .footage import append_footage_reanalysis_history
                history_path = append_footage_reanalysis_history(PROJECTS/self.project.id, previous_snapshot)
                self.project.creative_plan.setdefault('footage_reanalysis_history', []).append(str(history_path))
            analysis=self.model_router.analyze_footage(info,self.project.creative_plan,manifest,constraints)
            self.project.creative_plan['footage_visual_analysis']=analysis

            waste_root=folder.parent/'05_废片库'
            protected_paths = {s.source_file for s in (self.project.shots or []) if getattr(s, 'source_file', None)}
            for item in (self.project.creative_plan.get('footage_plan') or []):
                if isinstance(item, dict) and item.get('source'):
                    protected_paths.add(str(item['source']))
            usable,waste_records=archive_analyzed_waste(clips,analysis,waste_root,self.project.id,protected_paths=protected_paths)
            self.project.creative_plan['footage_archive']={
                'archive_root':str(waste_root/self.project.id),
                'records':waste_records,
            }
            if not usable:
                raise RuntimeError('重新分析后没有剩余可用实拍素材；明确不可用素材已归档到 05_废片库。')

            speech_transcripts=[]
            speech_profile=self.model_router.route('口播转写')
            if speech_profile.enabled and (speech_profile.api_key or speech_profile.provider == 'local_openai') and speech_profile.transcription_enabled:
                transcript_dir=PROJECTS/self.project.id/'transcripts'
                for clip in usable:
                    try:
                        audio_path=extract_audio(Path(clip.path),transcript_dir/(Path(clip.path).stem+'.wav'))
                        speech_transcripts.append({'source':clip.name,'transcript':self.model_router.transcribe_footage_audio(audio_path,speech_profile)})
                    except Exception as speech_error:
                        speech_transcripts.append({'source':clip.name,'error':str(speech_error)})
            self.project.creative_plan['footage_transcripts']=speech_transcripts

            coverage=audit_footage_coverage(analysis,self.project.creative_plan)
            self.project.creative_plan['footage_coverage']=coverage
            gaps=classify_footage_gaps(coverage,self.project.creative_plan,generation_connected=False)
            self.project.creative_plan['footage_gaps']=gaps
            gap_tasks=build_footage_gap_tasks(coverage,gaps,self.project.creative_plan)
            self.project.creative_plan['footage_gap_tasks']=gap_tasks

            raw_plan=self.model_router.plan_footage(
                info,self.project.creative_plan,[c.to_public() for c in usable],constraints,
                footage_analysis=analysis,footage_coverage=coverage,
            )
            plan_items,warnings=validate_footage_plan(raw_plan,usable)
            final_audit=audit_final_footage_plan(plan_items,analysis,coverage)
            self.project.creative_plan['footage_selection_audit']=final_audit
            self._apply_footage_plan(final_audit['plan'])
            self.project.creative_plan['footage_plan']=final_audit['plan']
            self.project.footage_folder=str(folder)
            self.store.save(self.project)

            self.detail.set(
                f'实拍素材已重新分析：{len(usable)} 个可用素材｜'
                f'覆盖率 {coverage.get("coverage_score",100):.1f}%｜'
                f'缺口任务 {gap_tasks.get("task_count",0)} 个｜'
                f'最终方案 {len(final_audit.get("plan",[]))} 个镜头'
            )
            messagebox.showinfo(
                '重新分析完成',
                f'已重新进入完整闭环。\n\n'
                f'可用素材：{len(usable)} 个\n'
                f'卖点覆盖率：{coverage.get("coverage_score",100):.1f}%\n'
                f'缺口任务：{gap_tasks.get("task_count",0)} 个\n'
                f'最终镜头：{len(final_audit.get("plan",[]))} 个\n\n'
                '新增素材已经重新进入素材池；如果仍有缺口，可继续补拍后再次点击本按钮。'
            )
        except Exception as e:
            messagebox.showerror('重新分析失败',str(e))

    @ui_action
    def footage_reanalysis_history_report(self):
        """查看连续补拍/重新分析过程中保存的历史方案，不触发新的 AI 调用。"""
        if not self.project:
            return messagebox.showinfo('提示', '请先创建一个实拍素材项目。')
        history = self.project.creative_plan.get('footage_reanalysis_history') or []
        if not history:
            return messagebox.showinfo('暂无历史', '当前项目还没有重新分析历史。首次重新分析不会产生历史快照，从第二次开始自动保存。')
        win = tk.Toplevel(self); win.title('实拍重新分析历史'); win.geometry('980x680'); win.transient(self)
        frm = ttk.Frame(win, padding=14); frm.pack(fill='both', expand=True)
        ttk.Label(frm, text='实拍重新分析历史', font=('Microsoft YaHei UI', 18, 'bold')).pack(anchor='w')
        ttk.Label(frm, text='这里只读取已经保存的历史快照，不会再次调用 AI。', foreground='#666').pack(anchor='w', pady=(2, 10))
        tree = ttk.Treeview(frm, columns=('file','coverage','shots','gaps'), show='headings', height=18)
        for c,t,w in [('file','历史快照',430),('coverage','覆盖率',100),('shots','镜头数',90),('gaps','缺口任务',100)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both', expand=True)
        details = tk.Text(frm, height=10, wrap='word'); details.pack(fill='x', pady=10)
        entries=[]
        for raw in history:
            p=Path(str(raw)).expanduser()
            if not p.exists(): continue
            try:
                data=json.loads(p.read_text(encoding='utf-8'))
            except Exception as exc:
                data={'_error': str(exc)}
            coverage=(data.get('footage_coverage') or {})
            gaps=(data.get('footage_gap_tasks') or {})
            plan=data.get('footage_plan') or []
            entries.append((p,data))
            tree.insert('', 'end', values=(p.name, f"{coverage.get('coverage_score','-')}%", len(plan), gaps.get('task_count','-')))
        def show_selected(_event=None):
            sel=tree.selection()
            if not sel: return
            idx=tree.index(sel[0]); p,data=entries[idx]
            details.delete('1.0','end')
            details.insert('end', f'文件：{p}\n')
            details.insert('end', f'覆盖率：{(data.get("footage_coverage") or {}).get("coverage_score","-")}%\n')
            details.insert('end', f'缺口任务：{(data.get("footage_gap_tasks") or {}).get("task_count","-")}\n')
            details.insert('end', f'历史镜头数：{len(data.get("footage_plan") or [])}\n\n')
            details.insert('end', json.dumps(data.get('footage_selection_audit') or {}, ensure_ascii=False, indent=2)[:12000])
        tree.bind('<<TreeviewSelect>>', show_selected)
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e')

    @ui_action
    def system_status(self):
        """Show whether advertised capabilities are actually configured and usable."""
        win=tk.Toplevel(self); win.title('系统状态 · 功能是否真正启用'); win.geometry('900x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='系统状态',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='这里显示的是本机实际检测结果，不是“代码里已经写了”就算启用。').pack(anchor='w',pady=(2,12))
        tree=ttk.Treeview(frm,columns=('status','detail'),show='headings',height=22)
        tree.heading('status',text='状态'); tree.heading('detail',text='检测结果 / 当前配置')
        tree.column('status',width=100,anchor='center'); tree.column('detail',width=680)
        tree.pack(fill='both',expand=True)
        def add(group,name,ok,detail,warn=False):
            state='🟢 已启用' if ok else ('🟡 已接入但未完整配置' if warn else '🔴 未启用')
            tree.insert('', 'end', values=(state, f'{group}｜{name}：{detail}'))
        gpu=detect_gpu()
        profile=detect_hardware(); add('本地硬件','硬件能力',bool(profile.gpus) or profile.execution_mode == 'cloud_first',format_hardware(profile))
        cap=CapabilityRouter(ROOT, profile)
        def mode_label(d): return {'local':'本地','cloud':'云端','unavailable':'不可用'}.get(d.target,d.target)
        llm=cap.decide_llm(); add('本地/云端能力调度','创意大模型',True,f"当前：{mode_label(llm)}｜{llm.reason}")
        asset=cap.decide_asset('演员'); add('本地/云端能力调度','素材生成',True,f"当前：{mode_label(asset)}｜{asset.reason}")
        video=cap.decide_video(); add('本地/云端能力调度','视频生成',True,f"当前：{mode_label(video)}｜{video.reason}")
        ff=ffmpeg_available(); nv=has_nvenc() if ff else False
        add('本地后处理','FFmpeg',ff,'ffmpeg + ffprobe 已找到' if ff else '未找到 ffmpeg/ffprobe，请安装并加入 PATH')
        add('本地后处理','NVENC 硬件编码',nv,'h264_nvenc 可用' if nv else '不可用，将退回 CPU 编码',warn=ff and not nv)
        profiles=self.model_router.profiles(); enabled=[p for p in profiles if p.enabled]
        keyed=[p for p in enabled if p.api_key or p.provider == 'local_openai']
        default=self.model_router.get(self.model_router.data['default_model'])
        add('AI创意引擎','模型池',bool(enabled),f'{len(enabled)} 个启用模型；默认：{default.name}')
        add('AI创意引擎','模型调用凭据',bool(keyed),f'{len(keyed)} 个模型可实际调用' if keyed else '没有可实际调用的模型，请配置 API Key 或本地模型')
        routed=sum(1 for fn in FUNCTIONS if self.model_router.route(fn).enabled)
        add('AI创意引擎','10项功能独立路由',routed==len(FUNCTIONS),f'{routed}/{len(FUNCTIONS)} 个功能有启用模型')
        for fn in FUNCTIONS:
            p=self.model_router.route(fn); ready=p.enabled and (bool(p.api_key) or p.provider == 'local_openai')
            add('模型路由',fn,ready,f'→ {p.name} / {p.model}',warn=p.enabled and not ready)
        browser=_find_agent_browser()
        add('商品采集','浏览器回退采集',bool(browser),browser or '未检测到 agent-browser；直接HTTP失败时无法使用浏览器回退')
        forbidden=ROOT/'forbidden_terms.txt'
        add('合规','禁止词库',forbidden.exists(),str(forbidden) if forbidden.exists() else '未创建 forbidden_terms.txt')
        add('资产库','本地永久资产库',self.lib.root.exists(),f'{self.lib.root} · {len(self.lib.all())} 个资产 · 独立资产库硬盘目录')
        vp=load_video_provider(ROOT/'video-provider.json')
        video_ready=not isinstance(vp, __import__('ad_studio.providers',fromlist=['UnconfiguredProvider']).UnconfiguredProvider)
        add('生产链','镜头生成',video_ready,'REST 视频 Provider 已配置，可真实请求生成并下载镜头' if video_ready else '当前仍为未配置状态；生成按钮不会伪造云端成片',warn=not video_ready)
        add('云端生成','视频 Provider',video_ready,'配置文件：'+str(ROOT/'video-provider.json') if video_ready else '未配置 video-provider.json',warn=not video_ready)
        add('本地硬件后处理','画幅适配 / 裁切 / 缩放',ff,'9:16 / 1:1 / 16:9 已接入 FFmpeg，本机执行' if ff else '等待 FFmpeg')
        add('本地硬件后处理','硬件编码',bool(ff and (nv or has_nvenc())),f'自动选择可用硬件编码器：{gpu.get("encoders",[])}' if ff and gpu.get('encoders') else '无可用硬件编码器，将使用 CPU 编码',warn=ff and not gpu.get('encoders'))
        add('本地硬件后处理','AI自动构图/节奏/转场',True,'创意引擎为每镜头输出主体坐标、速度、转场，由本机按检测到的硬件能力执行')
        add('本地成片加工','AI字幕位置/样式',True,'分镜决定字幕安全区和样式，本地FFmpeg烧录')
        add('本地成片加工','AI BGM强度',True,'分镜决定BGM强弱；有人声时保持低音量')
        add('本地硬件后处理','逐镜头版本化',True,'每个镜头独立保存 postprocessed/project/shot/v版本，换镜头不重做其他镜头')
        add('本地成片加工','字幕生成',True,'使用本机字幕引擎生成 SRT，并可烧录到镜头')
        add('本地成片加工','人声/BGM混音',ff,'人声保留、BGM自动压低；BGM从本地资产库读取' if ff else '等待 FFmpeg')
        add('生产链','最终成片拼接',ff,'本地 FFmpeg concat 可用' if ff else '等待 FFmpeg')
        add('用户素材剪辑','素材扫描',ff,'指定文件夹内视频用 ffprobe 探测时长/分辨率，自动过滤不可解析文件' if ff else '等待 FFmpeg')
        add('用户素材剪辑','素材裁剪出片',ff,'AI 素材剪辑导演规划镜头 → 本地 FFmpeg 按起止秒裁剪拼接（不调用视频生成）' if ff else '等待 FFmpeg')
        add('云端生成','人物/场景/关键视频镜头',False,'云端生成 Adapter 尚未接入，不会偷偷产生云端费用',warn=True)
        add('云端生成','高质量配音',False,'语音 Provider 尚未接入',warn=True)
        ttk.Label(frm,text='🟢 可直接使用   🟡 有框架但尚未完全接通   🔴 当前不可用',font=('Microsoft YaHei UI',10,'bold')).pack(anchor='w',pady=(10,4))
        btn=ttk.Frame(frm); btn.pack(fill='x')
        ttk.Button(btn,text='重新检测',command=lambda:(win.destroy(),self.system_status())).pack(side='right')
        ttk.Button(btn,text='打开模型设置',command=self.model_settings).pack(side='right',padx=8)

    @ui_action
    def model_settings(self):
        win=tk.Toplevel(self); win.title('AI 模型池与功能路由'); win.geometry('820x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='多模型池',font=('Microsoft YaHei UI',16,'bold')).pack(anchor='w')
        ttk.Label(frm,text='默认 GPT；不同功能可以分别指定不同模型。API Key 和模型单价只保存在本机。').pack(anchor='w',pady=(2,10))

        profiles=self.model_router.profiles()
        selected=tk.StringVar(value=profiles[0].id if profiles else '')
        ttk.Label(frm,text='模型').pack(anchor='w')
        model_box=ttk.Combobox(frm,textvariable=selected,values=[p.id for p in profiles],state='readonly')
        model_box.pack(fill='x',pady=4)

        fields=ttk.Frame(frm); fields.pack(fill='x',pady=4)
        name=tk.StringVar(); provider=tk.StringVar(value='openai_compatible'); base=tk.StringVar(); model=tk.StringVar(); key=tk.StringVar(); in_price=tk.StringVar(value='0'); out_price=tk.StringVar(value='0'); vision=tk.BooleanVar(value=False); transcription=tk.BooleanVar(value=False)
        for row,label,var in [(0,'名称',name),(1,'提供方式',provider),(2,'Base URL',base),(3,'模型 ID',model),(4,'API Key',key),(5,'输入 ¥/1K',in_price),(6,'输出 ¥/1K',out_price)]:
            ttk.Label(fields,text=label,width=12).grid(row=row,column=0,sticky='w',pady=3)
            ttk.Entry(fields,textvariable=var,show='*' if label=='API Key' else '').grid(row=row,column=1,sticky='ew',padx=8,pady=3)
        fields.columnconfigure(1,weight=1)
        ttk.Checkbutton(fields,text='支持图片/视频帧分析（实拍素材视觉分析必需）',variable=vision).grid(row=7,column=1,sticky='w',padx=8,pady=5)
        ttk.Checkbutton(fields,text='支持语音转写（实拍口播分析必需）',variable=transcription).grid(row=8,column=1,sticky='w',padx=8,pady=5)

        def load_profile(_=None):
            try:p=self.model_router.get(selected.get())
            except Exception:return
            name.set(p.name); provider.set(p.provider); base.set(p.base_url); model.set(p.model); key.set(p.api_key); in_price.set(str(p.input_price_rmb_per_1k)); out_price.set(str(p.output_price_rmb_per_1k)); vision.set(bool(getattr(p,'vision_enabled',False))); transcription.set(bool(getattr(p,'transcription_enabled',False)))

        def test_selected():
            ok,msg=self.model_router.test_connection(selected.get())
            messagebox.showinfo('模型连接测试', ('🟢 连接成功\n' if ok else '🔴 连接失败\n') + msg)
        def save_profile():
            mid=selected.get() or f'model-{len(self.model_router.profiles())+1}'
            p=ModelProfile(mid,name.get().strip() or mid,provider.get().strip() or 'openai_compatible',base.get().strip(),model.get().strip(),key.get().strip(),True,float(in_price.get() or 0),float(out_price.get() or 0),vision.get(),transcription.get())
            self.model_router.add_or_update(p); self.model_router.set_default(mid)
            selected.set(mid); model_box['values']=[x.id for x in self.model_router.profiles()]
            messagebox.showinfo('已保存','模型已加入本机模型池，并设为默认模型。')

        def new_profile():
            mid=f'model-{len(self.model_router.profiles())+1}'
            p=ModelProfile(mid,f'模型 {len(self.model_router.profiles())+1}')
            self.model_router.add_or_update(p); selected.set(mid); model_box['values']=[x.id for x in self.model_router.profiles()]; load_profile()

        model_box.bind('<<ComboboxSelected>>',load_profile); load_profile()
        btn=ttk.Frame(frm); btn.pack(fill='x',pady=8)
        ttk.Button(btn,text='＋新增模型',command=new_profile).pack(side='left'); ttk.Button(btn,text='保存模型并设为默认',command=save_profile).pack(side='left',padx=8); ttk.Button(btn,text='🔌 测试当前模型',command=test_selected).pack(side='left',padx=8)

        ttk.Label(frm,text='功能 → 模型',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w',pady=(14,6))
        route_frame=ttk.Frame(frm); route_frame.pack(fill='both',expand=True)
        route_vars={}
        ids=[p.id for p in self.model_router.profiles()]
        for i,function in enumerate(FUNCTIONS):
            ttk.Label(route_frame,text=function,width=18).grid(row=i,column=0,sticky='w',pady=3)
            v=tk.StringVar(value=self.model_router.route(function).id); route_vars[function]=v
            ttk.Combobox(route_frame,textvariable=v,values=ids,state='readonly',width=28).grid(row=i,column=1,sticky='w',padx=8)

        def save_routes():
            for function,v in route_vars.items():
                if v.get(): self.model_router.set_route(function,v.get())
            messagebox.showinfo('已保存','功能路由已保存。以后可以让不同功能使用不同模型。')
            win.destroy()

        ttk.Button(frm,text='保存全部功能路由',command=save_routes).pack(anchor='e',pady=10)

    @ui_action
    def video_provider_settings(self):
        win=tk.Toplevel(self); win.title('云端视频生成 Provider'); win.geometry('760x520'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='云端视频生成',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='这里配置真实视频生成服务。不同供应商 API 不完全相同，目前采用通用 REST 适配器；没有配置就不会产生云端调用。',wraplength=700).pack(anchor='w',pady=(2,12))
        cfg_path=ROOT/'video-provider.json'
        data={}
        if cfg_path.exists():
            try:data=json.loads(cfg_path.read_text(encoding='utf-8')).get('video_provider',{})
            except Exception:data={}
        vars={k:tk.StringVar(value=str(data.get(k,''))) for k in ('name','endpoint','model','api_key','status_endpoint','poll_interval','cost_per_shot_rmb')}
        for row,(label,key) in enumerate([('供应商名称','name'),('生成 Endpoint','endpoint'),('模型 ID','model'),('API Key','api_key'),('任务查询 Endpoint','status_endpoint'),('轮询间隔秒','poll_interval'),('每镜头价格 ¥','cost_per_shot_rmb')]):
            ttk.Label(frm,text=label,width=16).grid(row=row,column=0,sticky='w',pady=5)
            ttk.Entry(frm,textvariable=vars[key],show='*' if key=='api_key' else '').grid(row=row,column=1,sticky='ew',pady=5,padx=8)
        frm.columnconfigure(1,weight=1)
        status=tk.StringVar(value='检测中…'); ttk.Label(frm,textvariable=status).grid(row=4,column=1,sticky='w',pady=8)
        def save():
            payload={'video_provider':{k:v.get().strip() for k,v in vars.items()}}
            cfg_path.parent.mkdir(parents=True,exist_ok=True); cfg_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
            status.set('🟢 已保存到本机：'+str(cfg_path)); self.detail.set('视频 Provider 配置已保存；请在系统状态中重新检测。')
        def test():
            endpoint=vars['endpoint'].get().strip(); key=vars['api_key'].get().strip()
            if not endpoint or not key: status.set('🔴 Endpoint / API Key 未填写'); return
            status.set('🟡 配置已填写。通用适配器将在首次真实生成时验证供应商响应格式。')
        btn=ttk.Frame(frm); btn.grid(row=5,column=0,columnspan=2,sticky='e',pady=14)
        ttk.Button(btn,text='检查配置',command=test).pack(side='left',padx=5); ttk.Button(btn,text='保存',command=save).pack(side='left',padx=5)
        ttk.Label(frm,text='注意：保存配置 ≠ 已经验证供应商 API。只有真实生成成功后，系统才会显示镜头“已生成”。',wraplength=700).grid(row=6,column=0,columnspan=2,sticky='w',pady=12)

    @ui_action
    def asset_generation_settings(self):
        win=tk.Toplevel(self); win.title('自动素材生成设置'); win.geometry('760x560'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='演员 / 场景 / 商品素材自动生成',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='本地素材库优先；本地没有合适素材时，才调用这里配置的云端生成服务。生成结果自动保存回本地素材库。',wraplength=700).pack(anchor='w',pady=(2,12))
        path=ROOT/'asset-generation.json'; data={}
        if path.exists():
            try:data=json.loads(path.read_text(encoding='utf-8'))
            except Exception:data={}
        vars={}
        for kind in ('演员','场景','商品素材'):
            cfg=data.get(kind,{})
            box=ttk.LabelFrame(frm,text=kind,padding=10); box.pack(fill='x',pady=5)
            vars[kind]={}
            for row,(label,key) in enumerate((('Endpoint','endpoint'),('模型 ID','model'),('API Key','api_key'),('单次生成价格 ¥','price_rmb'),('供应商','provider'))):
                ttk.Label(box,text=label,width=15).grid(row=row,column=0,sticky='w',pady=3)
                v=tk.StringVar(value=str(cfg.get(key,''))); vars[kind][key]=v
                ttk.Entry(box,textvariable=v,show='*' if key=='api_key' else '').grid(row=row,column=1,sticky='ew',padx=6)
            box.columnconfigure(1,weight=1)
        def save():
            payload={k:{key:v.get().strip() for key,v in d.items()} for k,d in vars.items()}
            path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
            messagebox.showinfo('已保存','素材生成配置已保存到本机。')
        ttk.Button(frm,text='保存',command=save).pack(anchor='e',pady=12)
        ttk.Label(frm,text='注意：配置保存后并不代表供应商 API 已验证；首次实际生成时才会验证返回格式。',wraplength=700).pack(anchor='w')

    @ui_action
    def usage_view(self):
        win=tk.Toplevel(self); win.title('AI调用记录 · 本机成本账本'); win.geometry('1080x620'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        summary=self.model_router.usage_summary()
        ttk.Label(frm,text='AI调用记录',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text=f"累计调用：{summary['calls']}  成功：{summary['success']}  失败：{summary['failed']}  Token：{summary['tokens']:,}  已记录模型成本：¥{summary['estimated_cost_rmb']:.4f}").pack(anchor='w',pady=(2,10))
        ttk.Label(frm,text='成本为模型返回 Token × 本机配置单价；未配置单价的模型显示 ¥0，不代表供应商永久免费。').pack(anchor='w',pady=(0,8))
        tree=ttk.Treeview(frm,columns=('time','function','model','provider','status','tokens','cost','duration'),show='headings')
        for col,title,w in [('time','时间',135),('function','功能',120),('model','实际模型',180),('provider','提供方式',100),('status','状态',70),('tokens','Token',90),('cost','估算成本',90),('duration','耗时',80)]:
            tree.heading(col,text=title); tree.column(col,width=w)
        tree.pack(fill='both',expand=True)
        for x in self.model_router.recent_usage(150):
            tree.insert('', 'end', values=(x.get('time',''),x.get('function',''),x.get('model_name',''),x.get('provider',''),x.get('status',''),x.get('total_tokens',0),f"¥{float(x.get('estimated_cost_rmb',0)):.4f}",f"{int(x.get('duration_ms',0))}ms"))
        ttk.Button(frm,text='刷新',command=lambda:(win.destroy(),self.usage_view())).pack(anchor='e',pady=8)

    def refresh_gpu(self):
        g=detect_gpu(); self.gpu_text.set(('🟢 '+g.get('name','NVIDIA')+' · '+g.get('mode','CPU')) if g.get('available') else '⚪ 未检测到 NVIDIA GPU · CPU模式')

    def _show_cost_breakdown(self,c):
        lines=[f"项目预估：¥{c['总计']:.2f}",f"本地处理/FFmpeg：¥{c['本地']:.2f}",f"云端任务：¥{c['云端']:.2f}"]
        for item in c.get('明细',[]):
            if item['数量']: lines.append(f"  {item['项目']}：{item['数量']} × ¥{item['单价']:.2f} = ¥{item['小计']:.2f}")
        actual=round(sum(float(getattr(s,'actual_cost_rmb',0) or 0) for s in (self.project.shots if self.project else [])),4)
        estimate=float(c.get('总计',0) or 0)
        pending=max(0.0,estimate-actual)
        lines += [f'已实际发生：¥{actual:.2f}',f'按当前计划尚未发生：¥{pending:.2f}']
        self.cost.set(' | '.join(lines))

    def _creative_constraints(self):
        return {
            'platform': self.project.platform if self.project else '自动识别',
            'ad_level': self.level.get(),
            'video_form': self.form.get(),
            'task_type': self.task_type.get(),
            'task_rules': {'电商短视频':'突出卖点、节奏与转化；允许AI决定合理时长。','商品主图视频':'优先展示商品本体、核心细节和购买决策信息；避免无关剧情。','广告投放视频':'以投放转化和可测试性为核心；优先强钩子、清晰卖点、CTA与可区分版本。'}[self.task_type.get()],
            'task_policy': TASK_TYPE_POLICIES[self.task_type.get()],
            'allowed_video_forms': FORMS,
            'reusable_actors': [a.__dict__ for a in self.lib.reusable('演员')],
            'reusable_scenes': [a.__dict__ for a in self.lib.reusable('场景')],
            'reusable_product_assets': [a.__dict__ for a in self.lib.reusable('产品图')],
            'forbidden_terms_file': str(ROOT/'forbidden_terms.txt'),
        }

    def _plan_dict(self, plan):
        return {
            'product_summary': plan.product_summary, 'product_type': plan.product_type,
            'selling_points': plan.selling_points, 'target_audience': plan.target_audience,
            'pain_points': plan.pain_points, 'usage_scenes': plan.usage_scenes,
            'positioning': plan.positioning, 'ad_level': plan.ad_level,
            'video_form': plan.video_form, 'duration_seconds': plan.duration_seconds,
            'strategy': plan.strategy, 'hook': plan.hook, 'script': plan.script,
            'shots': [x.__dict__ for x in plan.shots],
            'task_type': self.project.creative_plan.get('task_type', self.task_type.get()) if self.project else self.task_type.get(),
            'task_validation': raw.get('task_validation', {}),
            'task_policy': raw.get('task_policy', TASK_TYPE_POLICIES.get(self.task_type.get(), {})),
            'variant_test_axis': raw.get('variant_test_axis', {}),
            'variant_set_audit': raw.get('variant_set_audit', {}),
        }

    def _activate_plan(self, raw, info):
        existing_variants=self.project.creative_plan.get('creative_variants',[]) if self.project else []
        existing_count=self.project.creative_plan.get('variant_count',len(existing_variants)) if self.project else 1
        plan=validate_plan(validate_task_type_plan(raw, self._creative_constraints()))
        self.project.form=plan.video_form
        self.project.product_name=info.name
        data=self._plan_dict(plan)
        if existing_variants:
            data['creative_variants']=existing_variants
            data['variant_count']=existing_count
        data['variant_index']=int(raw.get('_variant_index',1))
        data['variant_label']=raw.get('_variant_label',f"方案{data['variant_index']}｜{plan.video_form}")
        self.project.creative_plan=data
        self.project.shots=[
            __import__('ad_studio.models',fromlist=['Shot']).Shot(
                id=f'shot-{x.index:02d}', index=x.index,
                title=x.objective or f'镜头{x.index}', visual=x.visual, script=x.dialogue,
                composition=x.composition, focus_x=x.focus_x, focus_y=x.focus_y,
                subtitle_position=x.subtitle_position, subtitle_style=x.subtitle_style,
                pacing=x.pacing, speed=x.speed, bgm_intensity=x.bgm_intensity,
                bgm_volume=x.bgm_volume, transition=x.transition,
            ) for x in plan.shots
        ]
        self.active_variant_index=int(raw.get('_variant_index',1))
        cache=self.project.creative_plan.get('variant_shot_cache', {}) if self.project else {}
        saved=cache.get(str(self.active_variant_index), [])
        if saved:
            by_index={int(x.get('index', -1)): x for x in saved}
            for shot in self.project.shots:
                old=by_index.get(shot.index)
                if old:
                    for key,value in old.items():
                        if key != 'id' and hasattr(shot,key):
                            setattr(shot,key,value)
        return plan

    @ui_action
    def _cache_active_variant(self):
        if not self.project:return
        cache=self.project.creative_plan.setdefault('variant_shot_cache', {})
        cache[str(self.active_variant_index)]=[dict(s.__dict__) for s in self.project.shots]

    def _record_variant_output(self, path):
        if not self.project:return
        outputs=self.project.creative_plan.setdefault('variant_outputs', {})
        outputs[str(self.active_variant_index)]={'variant_index':self.active_variant_index,'variant_label':self.project.creative_plan.get('variant_label',f'方案{self.active_variant_index}'),'path':str(path),'status':'已输出'}

    @ui_action
    def switch_variant(self):
        if not self.project:return messagebox.showinfo('提示','先创建或打开一个包含多个创意方案的项目。')
        variants=self.project.creative_plan.get('creative_variants',[])
        if len(variants)<=1:return messagebox.showinfo('提示','当前项目只有一个创意方案。创建项目时将“创意方案数”设为3即可生成多种打法。')
        win=tk.Toplevel(self); win.title('切换创意方案'); win.geometry('760x430'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='同一商品的不同广告打法',font=('Microsoft YaHei UI',17,'bold')).pack(anchor='w')
        box=tk.Listbox(frm,height=10); box.pack(fill='both',expand=True,pady=10)
        for i,v in enumerate(variants,1):
            box.insert('end',f"{i}. {v.get('_variant_label',v.get('video_form','AI方案'))}｜{v.get('strategy','')[:90]}")
        box.selection_set(max(0,self.active_variant_index-1))
        def apply():
            sel=box.curselection()
            if not sel:return
            self._cache_active_variant()
            raw=variants[sel[0]]
            info=__import__('ad_studio.product_parser',fromlist=['ProductInfo']).ProductInfo(**self.project.product_info)
            self._activate_plan(raw,info)
            self.project.cost_estimate={}
            self.refresh_shots(); self.detail.set(f"已切换：{raw.get('_variant_label','方案')}。当前方案可单独生成/重新生成。")
            self.cost.set('成本：已切换方案，重新确认当前方案成本后生成。')
            self.store.save(self.project); win.destroy()
        ttk.Button(frm,text='切换到选中方案',command=apply).pack(anchor='e')

    @ui_action
    def create(self):
        if not self._ui_execution_gate(): return
        url=self.url.get().strip()
        if not url:return messagebox.showinfo('提示','请先输入商品链接。')
        level=self.level.get(); form=self.form.get(); task_type=self.task_type.get()
        try:
            budget=float(self.budget.get().strip())
            if budget<0: raise ValueError
            variant_count=max(1,min(3,int(self.variant_count.get())))
        except ValueError:
            return messagebox.showerror('参数格式错误','请输入有效的预算和创意方案数。')
        info=parse_product_url(url)
        footage_mode=self.footage_mode.get().strip()
        clips=None; usable=[]; folder=None
        if footage_mode=='用户拍摄素材':
            folder=Path(self.footage_folder.get().strip()).expanduser()
            if not folder.exists() or not folder.is_dir():
                return messagebox.showerror('素材文件夹无效','请先选择存放拍摄素材的文件夹（点击“选择素材文件夹”）。')
            from .footage import scan_footage, FootageError
            try:
                clips=scan_footage(folder)
            except FootageError as exc:
                return messagebox.showerror('素材扫描失败',str(exc))
            usable=[c for c in clips if c.duration>0]
            if not usable:
                return messagebox.showerror('没有可用素材',f'文件夹中没有可解析的视频素材。\n已跳过无法解析的文件：{len(clips)} 个。')
        if not info.fetched and info.error:
            if not messagebox.askyesno('商品解析未完成',f'当前无法直接读取商品页面。\n\n原因：{info.error}\n\n仍可创建项目，稍后可手动补充商品信息。是否继续？'):
                return
        self.detail.set(f'商品资料采集：{info.name} · {info.platform}\n来源：{info.source or "未完成"}\n{info.description[:180] or "未读取到商品描述"}')
        self.project=new_project(url,level,form if form!='AI自动选择' else 'AI自动选择')
        self.model_router.set_project_context(self.project.id)
        self.project.product_info=info.to_dict()
        self.project.creative_plan['task_type']=task_type
        try:
            constraints=self._creative_constraints()
            raw_plans=self.model_router.create_plans(info.to_dict(),constraints,variant_count) if variant_count>1 else [self.model_router.create_plan(info.to_dict(),constraints)]
            for i,raw in enumerate(raw_plans,1):
                raw['_variant_index']=int(raw.get('_variant_index',i))
                raw['_variant_label']=raw.get('_variant_label',f"方案{i}｜{raw.get('video_form','AI创意方案')}")
            plan=self._activate_plan(raw_plans[0],info)
            self.project.creative_plan['creative_variants']=raw_plans
            self.project.creative_plan['variant_count']=variant_count
            if footage_mode=='用户拍摄素材':
                self.project.footage_folder=str(folder)
                try:
                    analysis_dir=PROJECTS/self.project.id/'footage-analysis'
                    manifest=build_visual_manifest(usable,analysis_dir,max_frames_per_clip=4)
                    analysis=self.model_router.analyze_footage(
                        info.to_dict(), self.project.creative_plan, manifest, constraints
                    )
                    self.project.creative_plan['footage_visual_analysis']=analysis
                    # 视觉分析完成后，自动把明确不可用素材移入 05_废片库；只有成功移动的素材才从后续剪辑候选中剔除。
                    waste_root=folder.parent/'05_废片库'
                    usable, waste_records=archive_analyzed_waste(clips, analysis, waste_root, self.project.id)
                    self.project.creative_plan['footage_archive'] = {
                        'archive_root': str(waste_root/self.project.id),
                        'records': waste_records,
                    }
                    if not usable:
                        raise RuntimeError('AI视觉分析后没有剩余可用实拍素材；不可用素材已归档到 05_废片库。')
                    speech_transcripts=[]
                    speech_profile=self.model_router.route('口播转写')
                    if speech_profile.enabled and (speech_profile.api_key or speech_profile.provider == 'local_openai') and speech_profile.transcription_enabled:
                        transcript_dir=PROJECTS/self.project.id/'transcripts'
                        for clip in usable:
                            audio_path=extract_audio(Path(clip.path), transcript_dir/(Path(clip.path).stem+'.wav'))
                            try:
                                speech_transcripts.append({'source':clip.name,'transcript':self.model_router.transcribe_footage_audio(audio_path,speech_profile)})
                            except Exception as speech_error:
                                speech_transcripts.append({'source':clip.name,'error':str(speech_error)})
                    self.project.creative_plan['footage_transcripts']=speech_transcripts
                    from .footage import validate_footage_plan, audit_footage_coverage, audit_final_footage_plan
                    coverage=audit_footage_coverage(analysis, self.project.creative_plan)
                    self.project.creative_plan['footage_coverage']=coverage
                    gaps=classify_footage_gaps(coverage, self.project.creative_plan, generation_connected=False)
                    self.project.creative_plan['footage_gaps']=gaps
                    gap_tasks=build_footage_gap_tasks(coverage, gaps, self.project.creative_plan)
                    self.project.creative_plan['footage_gap_tasks']=gap_tasks
                    raw_footage_plan=self.model_router.plan_footage(
                        info.to_dict(), self.project.creative_plan,
                        [c.to_public() for c in usable], constraints,
                        footage_analysis=analysis,
                        footage_coverage=coverage,
                    )
                    plan_items,warnings=validate_footage_plan(raw_footage_plan,usable)
                    final_audit=audit_final_footage_plan(plan_items, analysis, coverage)
                    self.project.creative_plan['footage_selection_audit']=final_audit
                    plan_items=final_audit['plan']
                    self._apply_footage_plan(plan_items)
                    self.project.creative_plan['footage_plan']=plan_items
                except Exception as fe:
                    self.project=None
                    messagebox.showerror('素材剪辑规划失败',str(fe))
                    return
        except Exception as e:
            self.project=None
            messagebox.showerror('创意引擎未配置',str(e))
            return

        if footage_mode=='用户拍摄素材':
            c={'本地':0.0,'云端':0.0,'总计':0.0,'预算':budget,'超预算':False,'创意方案数':variant_count,
               '明细':[{'项目':'用户素材本地剪辑','数量':len(plan.shots),'单价':0.0,'小计':0.0,'计费方式':'本地FFmpeg裁剪'}],
               '计价说明':'素材剪辑模式：只使用你放入指定文件夹的拍摄素材，不调用视频/素材生成服务；费用仅包含 AI 分析与本地处理（当前配置均为 ¥0）。'}
            self.project.cost_estimate=c; self._show_cost_breakdown(c)
            clips_note='\n'.join(f"  {x.name}：{x.duration:.1f}s · {x.width}x{x.height}" for x in usable)
            warnings_note=('（已自动截断越界时长：' + '；'.join(warnings) + '）') if warnings else ''
            detail='\n'.join([
                f"任务类型：{task_type}",f"商品：{info.name}",f"素材文件夹：{folder}",f"扫描到可用素材：{len(usable)} 个（跳过无法解析 {len(clips)-len(usable)} 个）",
                '素材清单：',clips_note,'',
                f"视觉分析：已观察 {len(analysis.get('clips', [])) if isinstance(analysis, dict) else 0} 个素材；自动归档废片：{sum(1 for x in self.project.creative_plan.get('footage_archive', {}).get('records', []) if x.get('archived'))} 个；口播转写：{len(speech_transcripts)} 个素材。",
                f"卖点覆盖率：{coverage.get('coverage_score', 100):.1f}%｜开场候选：{coverage.get('opening_candidate') or '未找到'}｜缺失关键镜头：{'、'.join(x.get('need','') for x in coverage.get('missing_key_shots', [])) or '无'}",
                f"素材缺口处理：{'；'.join(x.get('need','')+'→'+x.get('action','') for x in gaps.get('key_shot_gaps', [])) or '无'}｜缺失卖点：{'、'.join(x.get('name','') for x in gaps.get('selling_point_gaps', [])) or '无'}",
                f"本次生成创意方案：{variant_count} 个（当前先展示方案1）",f"AI选择视频形式：{plan.video_form}",f"AI策略：{plan.strategy}",'',
                'AI 剪辑方案：',*[f"  镜头{x['index']:02d}｜{x['source']}｜{x['start']:.1f}s 起｜{x['duration']:.1f}s｜{x.get('objective','')}" for x in plan_items],
                *(f'⚠ {warnings_note}' if warnings_note else ''),'',
                '素材剪辑模式预计费用：¥0（本地 FFmpeg 裁剪，无视频生成费）',f"本次预算：¥{budget:.2f}",c['计价说明'],'',
                '素材剪辑不会调用视频生成服务；是否现在创建？'
            ])
        else:
            vp=load_video_provider(ROOT/'video-provider.json')
            rate=float(getattr(vp,'cost_per_shot_rmb',0.72)) if hasattr(vp,'cost_per_shot_rmb') else 0.72
            c=estimate_cost(len(plan.shots), {'cloud_video_per_shot': rate})
            asset_est=estimate_asset_generation(self.lib,ROOT,[x.__dict__ for x in plan.shots])
            c['资产生成']=asset_est
            asset_total=float(asset_est.get('总计',0.0))
            if asset_total:
                c['云端']=round(float(c.get('云端',0.0))+asset_total,2)
                c['总计']=round(float(c.get('本地',0.0))+float(c['云端']),2)
                c['明细'].append({'项目':'演员/场景/商品素材自动生成','数量':asset_est.get('数量',0),'单价':0.0,'小计':asset_total,'计费方式':'按缺失资产配置价格'})
            c['预算']=budget; c['超预算']=c['总计']>budget; c['创意方案数']=variant_count; self.project.cost_estimate=c; self._show_cost_breakdown(c)
            detail='\n'.join([
                f"任务类型：{task_type}",f"商品：{info.name}",f"本次生成创意方案：{variant_count} 个（当前先展示方案1）",f"AI判断广告强度：{plan.ad_level}",
                f"AI选择视频形式：{plan.video_form}",f"预计时长：{plan.duration_seconds}秒",f"AI策略：{plan.strategy}",f"AI钩子：{plan.hook}",'',
                f"当前方案开始前预计成本：¥{c['总计']:.2f}",f"本地处理/FFmpeg：¥{c['本地']:.2f}",f"视频生成费用：¥{rate*len(plan.shots):.2f}",f"演员生成费用：¥{sum(x['小计'] for x in asset_est['明细'] if x['类型']=='演员'):.2f}",f"场景生成费用：¥{sum(x['小计'] for x in asset_est['明细'] if x['类型']=='场景'):.2f}",f"商品素材生成费用：¥{sum(x['小计'] for x in asset_est['明细'] if x['类型']=='商品素材'):.2f}",f"云端任务：¥{c['云端']:.2f}",
                *[f"{x['项目']}：{x['数量']} × ¥{x['单价']:.2f} = ¥{x['小计']:.2f}" for x in c['明细'] if x['数量']],
                '',f"本次预算：¥{c['预算']:.2f}",('⚠ 预计超过本次预算。' if c['超预算'] else '✓ 预计不超过本次预算。'),c['计价说明'],
                '说明：多个创意方案是同一商品的不同广告打法；云端视频/素材费用按当前选中的方案单独计算。','',
                '超过预算不会自动降质、换模型或减少镜头。是否现在开始？'
            ])
        if not messagebox.askyesno('AI创意与项目预算确认',detail):
            self.project=None; self.detail.set('已取消项目创建，尚未产生生成费用。'); return
        self.store.save(self.project); save_product(info,ROOT,self.project.id); self.refresh_shots()
        if footage_mode=='用户拍摄素材':
            self.detail.set(f"素材剪辑方案已确认：{info.name} → {len(plan.shots)}镜头。素材文件夹：{folder}。可逐个「生成本镜头」裁剪，或直接「生成最终成片」。")
        else:
            self.detail.set(f"AI创意方案已确认：{info.name} → {plan.video_form} → {len(plan.shots)}镜头；共{variant_count}种方案，可用‘切换创意方案’查看。")

    def refresh_shots(self):
        for x in self.shots.get_children(): self.shots.delete(x)
        if self.project:
            for s in self.project.shots: self.shots.insert('', 'end',iid=s.id,text=f'{s.index:02d}  {s.title}',values=(f'v{s.version}',s.status,s.actor_id or '自动匹配',s.scene_id or '自动匹配'))

    def selected(self):
        sel=self.shots.selection(); return next((x for x in self.project.shots if x.id==sel[0]),None) if self.project and sel else None

    def show_shot(self,_=None):
        s=self.selected()
        if s:
            head=f'镜头 {s.index} · v{s.version} · {s.status}\n'
            if getattr(s,'clip_source','ai_generated')=='filmed':
                src=Path(s.source_file).name if s.source_file else '(未指定素材)'
                head+=f'素材来源：用户拍摄素材 ｜ {src} ｜ {s.source_start:.1f}s 起 ｜ 时长 {s.source_duration:.1f}s（本地裁剪）\n'
            self.detail.set(
                head+'\n'
                f'画面：{s.visual}\n\n文案：{s.script}\n\n'
                f'AI构图：{getattr(s, "composition", "主体清晰居中")}  '
                f'主体坐标：({getattr(s, "focus_x", 0.5):.2f},{getattr(s, "focus_y", 0.5):.2f})\n'
                f'节奏：{getattr(s, "pacing", "标准")} · 速度：{getattr(s, "speed", 1.0):.2f}x · '
                f'转场：{getattr(s, "transition", "硬切")}\n'
                f'字幕：{getattr(s, "subtitle_position", "底部安全区")} / {getattr(s, "subtitle_style", "白字黑边")}\n'
                f'BGM：{getattr(s, "bgm_intensity", "低")} · 音量 {getattr(s, "bgm_volume", 0.16):.2f}'
            )

    @ui_action
    def generate_shot(self):
        if not self._ui_execution_gate(): return
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择一个镜头。')
        try:
            s.status='生成中…'; self.store.save(self.project); self.refresh_shots()
            self.update_idletasks()
            if getattr(s,'clip_source','ai_generated')=='filmed':
                src=Path(s.source_file).name if s.source_file else '(未指定素材)'
                self.detail.set(f'镜头 {s.index} 正在从拍摄素材裁剪…（{src}，{s.source_start:.1f}s 起，{s.source_duration:.1f}s）')
                out=self.store.render_footage_shot(self.project,s)
                self.refresh_shots(); self.detail.set(f'镜头 {s.index} 已从拍摄素材裁剪 v{s.version}：{out}')
            else:
                decision=CapabilityRouter(ROOT).decide_video()
                mode={'local':'本地','cloud':'云端','unavailable':'不可用'}.get(decision.target,decision.target)
                self.detail.set(f'镜头 {s.index} 正在{mode}生成…')
                out=self.store.render_shot(self.project,s,config_root=ROOT)
                self.refresh_shots(); self.cost.set(f'项目实际成本 ¥{self.project.actual_cost_rmb:.4f} · 预估 ¥{self.project.cost_estimate.get("总计",0):.2f}'); self.detail.set(f'镜头 {s.index} 已由{mode}生成 v{s.version}：{out} · 项目实际累计 ¥{self.project.actual_cost_rmb:.4f}')
        except Exception as e:
            s.status='生成失败'; self.store.save(self.project); self.refresh_shots()
            self.detail.set(f'镜头 {s.index} 生成失败：{e}')
            messagebox.showerror('镜头生成失败',str(e))

    @ui_action
    def regen_shot(self):
        if not self._ui_execution_gate(): return
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择要重新生成的镜头。')
        old=s.version; mark_regenerate(self.project,self.project.shots.index(s)); self.store.save(self.project); self.refresh_shots(); self.detail.set(f'镜头 {s.index}：v{old} → v{s.version}。其他镜头版本保持不变。')

    @ui_action
    def edit_shot(self):
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择一个镜头。')
        win=tk.Toplevel(self); win.title(f'编辑镜头 {s.index}'); win.geometry('620x520'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='镜头标题').pack(anchor='w'); title=tk.StringVar(value=s.title); ttk.Entry(frm,textvariable=title).pack(fill='x',pady=4)
        ttk.Label(frm,text='画面描述').pack(anchor='w'); visual=tk.Text(frm,height=7); visual.pack(fill='x',pady=4); visual.insert('1.0',s.visual)
        ttk.Label(frm,text='口播/文案').pack(anchor='w'); script=tk.Text(frm,height=7); script.pack(fill='x',pady=4); script.insert('1.0',s.script)
        actors=self.lib.reusable('演员'); scenes=self.lib.reusable('场景'); actor_names=['自动匹配']+[a.name for a in actors]; scene_names=['自动匹配']+[a.name for a in scenes]; actor_map={a.name:a.id for a in actors}; scene_map={a.name:a.id for a in scenes}
        cur_actor=next((a.name for a in actors if a.id==s.actor_id),'自动匹配'); cur_scene=next((a.name for a in scenes if a.id==s.scene_id),'自动匹配'); av=tk.StringVar(value=cur_actor); sv=tk.StringVar(value=cur_scene)
        ttk.Label(frm,text='演员').pack(anchor='w'); ttk.Combobox(frm,textvariable=av,values=actor_names,state='readonly').pack(fill='x',pady=4); ttk.Label(frm,text='场景').pack(anchor='w'); ttk.Combobox(frm,textvariable=sv,values=scene_names,state='readonly').pack(fill='x',pady=4)
        def apply():
            s.title=title.get().strip() or s.title; s.visual=visual.get('1.0','end').strip(); s.script=script.get('1.0','end').strip(); s.actor_id=actor_map.get(av.get()); s.scene_id=scene_map.get(sv.get()); s.status='需重生成'; s.video_path=None; s.version+=1; self.store.save(self.project); self.refresh_shots(); self.show_shot(); win.destroy()
        ttk.Button(frm,text='保存修改并生成新版本',command=apply).pack(anchor='e',pady=10)

    @ui_action
    def load_project(self):
        files=sorted(PROJECTS.glob('project-*.json'), key=lambda p:p.stat().st_mtime, reverse=True)
        if not files:return messagebox.showinfo('提示','本地还没有已保存的广告项目。')
        win=tk.Toplevel(self); win.title('打开已有项目'); win.geometry('560x360'); win.transient(self); frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True); ttk.Label(frm,text='本机广告项目').pack(anchor='w'); box=tk.Listbox(frm,height=12); box.pack(fill='both',expand=True,pady=8)
        for p in files: box.insert('end',p.stem)
        def open_selected():
            sel=box.curselection()
            if not sel:return
            project=self.store.load(files[sel[0]].stem)
            if not project:return messagebox.showerror('打开失败','项目文件无法读取。')
            self.project=project; self.model_router.set_project_context(project.id); self.url.set(''); self.level.set(project.level); self.form.set(project.form); self.refresh_shots(); c=project.cost_estimate; self.cost.set(f"项目预估 ¥{c.get('总计',0):.2f} · 云端 ¥{c.get('云端',0):.2f} · 已保存 {len(project.shots)} 个镜头" if c else f'已保存 {len(project.shots)} 个镜头'); self.detail.set(f'已恢复项目：{project.product_name} · {project.platform} · {project.form}'); win.destroy()
        ttk.Button(frm,text='打开',command=open_selected).pack(anchor='e')

    @ui_action
    def upload(self,kind):
        p=filedialog.askopenfilename(title=f'选择{kind}文件')
        if p:self.lib.add_file(p,Path(p).stem,kind); self.refresh_assets()

    @ui_action
    def choose_footage_folder(self):
        p=filedialog.askdirectory(title='选择拍摄素材文件夹（放入你拍好的视频）')
        if p: self.footage_folder.set(p)

    def _apply_footage_plan(self, items):
        """把素材剪辑导演的方案落到项目镜头上：每个镜头指定素材文件+起止时间。"""
        by_index={int(x['index']):x for x in items}
        for s in self.project.shots:
            item=by_index.get(s.index)
            if not item: continue
            s.clip_source='filmed'
            folder=self.project.footage_folder or self.footage_folder.get()
            s.source_file=str(Path(folder)/item['source'])
            s.source_start=item['start']
            s.source_duration=item['duration']
            s.source_ranges=item.get('ranges', [[item['start'], item['start'] + item['duration']]])
            s.title=item.get('objective') or s.title
            s.visual=item.get('visual') or s.visual
            s.script=item.get('script') or s.script
            s.composition=item.get('composition', s.composition)
            s.focus_x=item.get('focus_x', s.focus_x)
            s.focus_y=item.get('focus_y', s.focus_y)
            s.subtitle_position=item.get('subtitle_position', s.subtitle_position)
            s.subtitle_style=item.get('subtitle_style', s.subtitle_style)
            s.pacing=item.get('pacing', s.pacing)
            s.speed=item.get('speed', s.speed)
            s.bgm_intensity=item.get('bgm_intensity', s.bgm_intensity)
            s.bgm_volume=item.get('bgm_volume', s.bgm_volume)
            s.transition=item.get('transition', s.transition)
            s.status='待剪辑'
            s.video_path=None

    def refresh_assets(self):
        for x in self.assets.get_children(): self.assets.delete(x)
        for a in self.lib.all(): self.assets.insert('', 'end',text=a.name,values=(a.kind,a.source,a.path or ''))

    @ui_action
    def postprocess_selected(self):
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择一个已经生成的真实镜头。')
        try:
            out=self.store.postprocess_shot(self.project,s,self.aspect.get())
            self.refresh_shots(); self.show_shot()
            self.detail.set(f'镜头 {s.index} 已完成本地后处理：{out}')
        except Exception as e:
            s.status='后处理失败'; self.store.save(self.project); self.refresh_shots()
            messagebox.showerror('本地后处理失败',str(e))

    @ui_action
    def finish_selected(self):
        s=self.selected()
        if not s or not s.video_path:return messagebox.showinfo('提示','先选择一个已经生成的真实镜头。')
        win=tk.Toplevel(self); win.title(f'镜头 {s.index} · 本地成片加工'); win.geometry('620x430'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='字幕',font=('Microsoft YaHei UI',13,'bold')).pack(anchor='w')
        script=tk.Text(frm,height=7); script.pack(fill='both',expand=True,pady=6); script.insert('1.0',s.script)
        bgms=self.lib.reusable('BGM'); names=['不添加BGM']+[a.name for a in bgms]; bm=tk.StringVar(value=names[0])
        ttk.Label(frm,text='BGM').pack(anchor='w'); ttk.Combobox(frm,textvariable=bm,values=names,state='readonly').pack(fill='x',pady=5)
        def run():
            try:
                from .subtitles import write_srt
                from .postprocess import burn_subtitles, mix_audio
                base=Path(s.video_path); folder=self.store.root/'postprocessed'/self.project.id/s.id
                folder.mkdir(parents=True,exist_ok=True)
                srt=write_srt(script.get('1.0','end').strip(),folder/f'v{s.version}.srt',duration=3)
                subout=folder/f'v{s.version}-sub.mp4'
                burn_subtitles(base,subout,srt,getattr(s,'subtitle_position','底部安全区'),getattr(s,'subtitle_style','白字黑边'))
                chosen=next((a for a in bgms if a.name==bm.get()),None); final=subout
                if chosen and chosen.path and getattr(s,'bgm_intensity','低') != '无':
                    audioout=folder/f'v{s.version}-audio.mp4'; mix_audio(subout,audioout,Path(chosen.path),getattr(s,'bgm_volume',0.16)); final=audioout
                s.video_path=str(final); s.status='本地成片加工完成'; self.store.save(self.project); self.refresh_shots(); self.show_shot()
                self.detail.set(f'镜头 {s.index} 已完成字幕/音频加工：{final}'); win.destroy()
            except Exception as e: messagebox.showerror('本地成片加工失败',str(e))
        ttk.Button(frm,text='执行：字幕 + BGM/人声处理',command=run).pack(anchor='e',pady=8)

    @ui_action
    def final_render(self):
        if not self._ui_execution_gate(): return
        if not self.project:return messagebox.showinfo('提示','先创建项目。')
        try:
            out=self.store.build_final(self.project,self.aspect.get(),variant_index=self.active_variant_index)
            self._record_variant_output(out)
            self._cache_active_variant()
            self.store.save(self.project)
            self.detail.set(f'方案{self.active_variant_index} 最终成片已独立输出：{out}')
            messagebox.showinfo('完成',f'方案{self.active_variant_index} 最终广告已生成\n{out}')
        except Exception as e: messagebox.showerror('暂不能成片',str(e))

    def save(self):
        if not self.project:return messagebox.showinfo('提示','当前没有项目可保存。')
        self.store.save(self.project); self.detail.set(f'项目已保存：{self.project.id}')
