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
from .product_parser import parse_product_url, save_product, save_product_library, load_product_library, merge_product_library, ProductInfo
from .creative_engine import CreativeEngine, validate_plan, validate_task_type_plan, TASK_TYPE_POLICIES
from .model_router import ModelRouter, ModelProfile, FUNCTIONS, audit_ad_variant_set, build_creative_test_plan, audit_creative_factual_consistency, audit_storyboard_fact_consistency, audit_visual_fact_consistency
from .browser_skill import _find_agent_browser
from .ffmpeg import available as ffmpeg_available, has_nvenc
from .providers import load_video_provider
from .footage import build_visual_manifest, footage_analysis_public, archive_analyzed_waste, classify_footage_gaps, build_footage_gap_tasks
from .hybrid_router import route_footage_gap_tasks
from .transcription import extract_audio
from .ui_contract import verify_ui_action_contract, UIContractError, ui_action
from .models import Shot
from .workflow_modes import AUTO, SEMI_AUTO, USER_CONTROLLED, WORKFLOW_MODES, decide_action, get_project_workflow_mode, invalidate_storyboard_approval, preserve_output_history, preserve_workflow_state, set_project_workflow_mode


def _restore_variant_shot_cache(base_shots, saved_shots):
    """恢复某个广告方案的完整镜头列表，保留人工纳入的额外镜头。

    原始分镜镜头使用稳定 id（如 shot-01）；AI 补镜头等额外镜头可能
    插入后改变 index，因此不能只按 index 恢复，否则切换方案后会丢失
    已通过人工复核的补镜头。
    """
    if not saved_shots:
        return list(base_shots)
    base_by_id = {str(getattr(shot, "id", "")): shot for shot in base_shots}
    restored = []
    for saved in saved_shots:
        if not isinstance(saved, dict):
            continue
        shot_id = str(saved.get("id", ""))
        if shot_id in base_by_id:
            shot = base_by_id[shot_id]
            for key, value in saved.items():
                if key != "id" and hasattr(shot, key):
                    setattr(shot, key, value)
            restored.append(shot)
        else:
            # 非原始分镜镜头（例如已通过复核的 AI 补镜头）完整保留。
            restored.append(Shot(**saved))
    return restored


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

    def _workflow_mode_value(self):
        """Map the Chinese UI label to the persisted, stable mode identifier."""
        labels = {
            "AI 全自动": AUTO,
            "AI 半自动": SEMI_AUTO,
            "用户控制 / AI 辅助": USER_CONTROLLED,
        }
        if hasattr(self, "workflow_mode"):
            value = str(self.workflow_mode.get() or "").strip()
            return labels.get(value, value if value in WORKFLOW_MODES else SEMI_AUTO)
        return get_project_workflow_mode(self.project) if self.project else SEMI_AUTO

    def _workflow_mode_label(self, mode):
        return {
            AUTO: "AI 全自动",
            SEMI_AUTO: "AI 半自动",
            USER_CONTROLLED: "用户控制 / AI 辅助",
        }.get(mode, "AI 半自动")

    def _authorize_workflow_action(self, action, title="操作确认"):
        """Apply workflow-mode confirmation policy without replacing safety gates."""
        decision = decide_action(self._workflow_mode_value(), action)
        if decision.allowed:
            return True
        if not decision.requires_confirmation:
            messagebox.showwarning(title, decision.reason)
            return False
        approved = messagebox.askyesno(
            title,
            f"{decision.reason}\n\n操作：{action}\n工作模式：{decision.mode}\n\n是否确认继续？"
        )
        if not approved:
            self.detail.set(f"已取消：{action}")
            return False
        # Consent is scoped to this single action; it is not stored as a blanket approval.
        return decide_action(decision.mode, action, user_approved=True).allowed

    def _confirm_budget_overrun(self, estimate, remaining, title="预算超限确认"):
        """Warn with exact amounts and require explicit consent instead of silently blocking."""
        decision = decide_action(self._workflow_mode_value(), "budget_overrun")
        if not decision.requires_confirmation:
            return decision.allowed
        approved = messagebox.askyesno(
            title,
            f"本次预计还需 ¥{float(estimate):.2f}，当前剩余预算 ¥{float(remaining):.2f}。"
            f"预计超出 ¥{max(0.0, float(estimate) - float(remaining)):.2f}。\n\n"
            "系统不会自动降质、换模型或减少镜头。是否仍要继续？"
        )
        if not approved:
            self.detail.set("用户取消了超预算操作；未开始本次生成。")
            return False
        return decide_action(decision.mode, "budget_overrun", user_approved=True).allowed

    def _ensure_storyboard_approval(self):
        """Require one approval per active variant in semi-auto/user-controlled modes."""
        if not self.project:
            return False
        mode = self._workflow_mode_value()
        if mode == AUTO:
            return True
        plan = self.project.creative_plan
        approvals = plan.setdefault("workflow_approvals", {})
        key = str(int(self.active_variant_index or 1))
        if approvals.get(key) is True:
            return True
        shots = list(self.project.shots or [])
        summary = "\\n".join(
            f"{shot.index}. {shot.title} — {str(shot.visual or '')[:110]}"
            for shot in shots[:18]
        )
        if len(shots) > 18:
            summary += f"\\n……其余 {len(shots) - 18} 个镜头"
        prompt = (
            f"当前方案：{self.active_variant_index}\\n"
            f"工作模式：{self._workflow_mode_label(mode)}\\n"
            f"分镜数量：{len(shots)}\\n\\n{summary}\\n\\n"
            "请先检查分镜。确认后才允许开始生成当前方案的镜头；拒绝则暂停，不会调用视频生成服务。"
        )
        if not messagebox.askyesno("确认分镜后继续", prompt):
            self.detail.set(f"方案{self.active_variant_index} 尚未批准分镜；本次生成已暂停。")
            return False
        approvals[key] = True
        self.store.save(self.project)
        return True

    def _choose_initial_plan(self, plans):
        """In user-controlled mode, let the user select the initial AI proposal."""
        if not plans:
            return None
        if len(plans) == 1:
            return 0 if messagebox.askyesno(
                "确认创意方案",
                f"AI 当前只提出一套方案：{plans[0].get('_variant_label', plans[0].get('video_form', '创意方案'))}。\\n是否明确选择这套方案？"
            ) else None
        win = tk.Toplevel(self)
        win.title("选择初始创意方案")
        win.geometry("760x430")
        win.transient(self)
        win.grab_set()
        frm = ttk.Frame(win, padding=14)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="AI 已生成候选方案，请选择本项目先使用哪一套。", wraplength=700).pack(anchor="w")
        box = tk.Listbox(frm, height=12)
        box.pack(fill="both", expand=True, pady=10)
        for i, plan in enumerate(plans, 1):
            label = plan.get("_variant_label", plan.get("video_form", f"方案{i}"))
            strategy = str(plan.get("strategy", ""))[:100]
            box.insert("end", f"{i}. {label}｜{strategy}")
        box.selection_set(0)
        selected = {"index": None}
        def confirm():
            indexes = box.curselection()
            if not indexes:
                messagebox.showinfo("请选择方案", "请先选择一套创意方案。", parent=win)
                return
            selected["index"] = int(indexes[0])
            win.destroy()
        def cancel():
            win.destroy()
        actions = ttk.Frame(frm)
        actions.pack(fill="x")
        ttk.Button(actions, text="使用选中方案", command=confirm).pack(side="right")
        ttk.Button(actions, text="取消创建", command=cancel).pack(side="right", padx=8)
        self.wait_window(win)
        return selected["index"]

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
        ttk.Label(setup,text='AI 工作模式').grid(row=7,column=0,sticky='w',pady=(6,0))
        self.workflow_mode=tk.StringVar(value='AI 半自动')
        ttk.Combobox(setup,textvariable=self.workflow_mode,values=['AI 全自动','AI 半自动','用户控制 / AI 辅助'],state='readonly',width=28).grid(row=7,column=1,sticky='w',pady=(6,0))
        ttk.Label(setup,text='全自动 / 半自动 / 用户控制·AI辅助；云端费用、超预算等授权仍需明确确认',foreground='#666').grid(row=7,column=2,columnspan=5,sticky='w',pady=(6,0))
        ttk.Button(setup,text='创建广告项目',command=self.create).grid(row=2,column=3,sticky='e'); ttk.Button(setup,text='📹 实拍分析报告',command=self.footage_analysis_report).grid(row=2,column=5,sticky='e',padx=8); ttk.Button(setup,text='📋 补素材任务',command=self.footage_gap_tasks_report).grid(row=2,column=6,sticky='e',padx=8); ttk.Button(setup,text='🤖 执行AI补镜头',command=self.generate_hybrid_gap_shots).grid(row=2,column=10,sticky='e',padx=8); ttk.Button(setup,text='🔍 AI补镜头复核',command=self.review_hybrid_gap_shots).grid(row=2,column=11,sticky='e',padx=8); ttk.Button(setup,text='🔄 重新分析实拍素材',command=self.reanalyze_footage).grid(row=2,column=7,sticky='e',padx=8); ttk.Button(setup,text='🕘 分析历史',command=self.footage_reanalysis_history_report).grid(row=2,column=8,sticky='e',padx=8); ttk.Button(setup,text='打开已有项目',command=self.load_project).grid(row=2,column=2,sticky='e',padx=8); ttk.Button(setup,text='📚 商品资料库',command=self.product_library_settings).grid(row=0,column=5,sticky='e',padx=8); ttk.Button(setup,text='⚙ 模型设置',command=self.model_settings).grid(row=0,column=3,sticky='e'); ttk.Button(setup,text='🔎 系统状态',command=self.system_status).grid(row=1,column=3,sticky='e'); ttk.Button(setup,text='🧪 创意版本矩阵',command=self.variant_matrix_report).grid(row=2,column=9,sticky='e',padx=8); ttk.Button(setup,text='🧠 创意方案分析',command=self.creative_variant_analysis_report).grid(row=2,column=12,sticky='e',padx=8); ttk.Button(setup,text='🧪 创意测试方案',command=self.creative_test_plan_report).grid(row=2,column=14,sticky='e',padx=8); ttk.Button(setup,text='🛡 创意事实检查',command=self.creative_fact_check_report).grid(row=2,column=15,sticky='e',padx=8); ttk.Button(setup,text='🎬 分镜事实复核',command=self.storyboard_fact_check_report).grid(row=2,column=16,sticky='e',padx=8); ttk.Button(setup,text='🎥 成片视觉复核',command=self.visual_fact_check_report).grid(row=2,column=17,sticky='e',padx=8); ttk.Button(setup,text='📥 真实投放数据（可选）',command=self.variant_performance_entry).grid(row=2,column=13,sticky='e',padx=8); ttk.Button(setup,text='📊 AI调用记录',command=self.usage_view).grid(row=2,column=4,sticky='e',padx=8); ttk.Button(setup,text='🎬 视频生成设置',command=self.video_provider_settings).grid(row=0,column=4,sticky='e',padx=8); ttk.Button(setup,text='🧩 素材生成设置',command=self.asset_generation_settings).grid(row=1,column=4,sticky='e',padx=8)
        main=ttk.Panedwindow(self,orient='horizontal'); main.pack(fill='both',expand=True,padx=16,pady=8)
        left=ttk.Frame(main,padding=8); right=ttk.Frame(main,padding=8); main.add(left,weight=3); main.add(right,weight=2)
        ttk.Label(left,text='② 分镜生产链',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.shots=ttk.Treeview(left,columns=('v','status','actor','scene'),show='tree headings',height=17)
        for c,t,w in [('v','版本',70),('status','状态',90),('actor','演员',150),('scene','场景',150)]: self.shots.heading(c,text=t); self.shots.column(c,width=w)
        self.shots.column('#0',width=300); self.shots.pack(fill='both',expand=True,pady=8); self.shots.bind('<<TreeviewSelect>>',self.show_shot)
        bar=ttk.Frame(left); bar.pack(fill='x'); ttk.Button(bar,text='切换创意方案',command=self.switch_variant).pack(side='left'); ttk.Button(bar,text='生成本镜头',command=self.generate_shot).pack(side='left',padx=8); ttk.Button(bar,text='重新生成本镜头',command=self.regen_shot).pack(side='left',padx=8); ttk.Button(bar,text='▶ 本地硬件后处理',command=self.postprocess_selected).pack(side='left',padx=8); ttk.Button(bar,text='生成最终成片',command=self.final_render).pack(side='right',padx=8); ttk.Button(bar,text='📦 成片交付中心',command=self.final_delivery_center).pack(side='right',padx=8); ttk.Button(bar,text='批量输出已完成版本',command=self.batch_final_render).pack(side='right',padx=8); ttk.Button(bar,text='⚡ 一键生成全部版本',command=self.batch_generate_variants).pack(side='right',padx=8); ttk.Button(bar,text='保存项目',command=self.save).pack(side='right')
        ttk.Label(right,text='③ 本地资产库',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.assets=ttk.Treeview(right,columns=('kind','source','path'),show='tree headings',height=13)
        for c,t,w in [('kind','类型',80),('source','来源',90),('path','本地文件',300)]: self.assets.heading(c,text=t); self.assets.column(c,width=w)
        self.assets.column('#0',width=180); self.assets.pack(fill='both',expand=True,pady=8)
        ab=ttk.Frame(right); ab.pack(fill='x'); ttk.Button(ab,text='＋上传演员',command=lambda:self.upload('演员')).pack(side='left'); ttk.Button(ab,text='＋上传场景',command=lambda:self.upload('场景')).pack(side='left',padx=5); ttk.Button(ab,text='＋上传产品素材',command=lambda:self.upload('产品图')).pack(side='left'); ttk.Button(ab,text='＋上传BGM',command=lambda:self.upload('BGM')).pack(side='left',padx=5); ttk.Button(ab,text='刷新资产库',command=self.refresh_assets).pack(side='right')
        self.detail=tk.StringVar(value='等待创建项目'); ttk.Label(right,textvariable=self.detail,justify='left',wraplength=470).pack(fill='x',pady=10); ttk.Button(right,text='编辑当前分镜',command=self.edit_shot).pack(anchor='w',pady=4)
        self.cost=tk.StringVar(value='成本：尚未计算'); ttk.Label(right,textvariable=self.cost,font=('Microsoft YaHei UI',12,'bold')).pack(anchor='w')
        ttk.Label(self,text='本地存储：本机磁盘  |  资产库：永久复用  |  云端生成：仅在需要时调用',relief='sunken',anchor='w',padding=8).pack(fill='x',side='bottom')



    def _final_delivery_repair_routes(self, gate, media_check):
        """把最终交付问题映射回真正产生问题的环节，不自动掩盖风险。"""
        routes=[]
        for reason in gate.get('reasons', []) if isinstance(gate, dict) else []:
            text=str(reason)
            if any(x in text for x in ('商品资料未支持的卖点','命中用户禁用词','高风险绝对化表达')):
                routes.append({'issue':text,'route':'创意事实检查','action':'修改创意方案或商品资料/禁用词后重新检查'})
            elif 'AI生成镜头尚未通过人工复核' in text:
                routes.append({'issue':text,'route':'AI补镜头复核','action':'通过或拒绝该AI补镜头；通过后重新检查'})
            elif any(x in text for x in ('商品可能被遮挡','画面可能模糊','画面可能抖动','素材已被视觉分析判定为不可用')):
                routes.append({'issue':text,'route':'成片视觉复核','action':'返回实际素材/分镜调整，修复后重新检查'})
            else:
                routes.append({'issue':text,'route':'分镜生产链','action':'检查对应镜头并重新生成/裁剪'})
        if isinstance(media_check,dict) and not media_check.get('valid',False):
            reason=str(media_check.get('reason') or '媒体质检未通过')
            routes.append({'issue':reason,'route':'最终成片输出','action':'修复输出文件、画幅或镜头后重新检查'})
        unique=[]; seen=set()
        for item in routes:
            key=(item['issue'],item['route'])
            if key not in seen:
                seen.add(key); unique.append(item)
        return unique

    def _run_final_delivery_recheck(self):
        """只重新执行已有资料的确定性检查，不重新生成素材、不调用广告平台。"""
        if not self.project:
            return None
        plan=self.project.creative_plan or {}
        variants=plan.get('creative_variants') or []
        if variants:
            raw_forbidden=plan.get('forbidden_terms') or plan.get('forbidden_words') or []
            if isinstance(raw_forbidden,str):
                raw_forbidden=[x.strip() for x in raw_forbidden.replace('，',',').split(',') if x.strip()]
            plan['creative_fact_audit']=audit_creative_factual_consistency(self.project.product_info or {},variants,raw_forbidden)
            plan['storyboard_fact_audit']=audit_storyboard_fact_consistency(self.project.product_info or {},variants)
        visual=plan.get('footage_visual_analysis') or {}
        variant_plans=plan.get('variant_footage_plans') or {}
        if visual:
            plan['visual_fact_audit']=audit_visual_fact_consistency(self.project.product_info or {},visual,variant_plans)
        self.store.save(self.project)
        gate=self.store.final_render_gate(self.project)
        variant=max(1,int(self.active_variant_index or 1))
        aspect=self.aspect.get() if hasattr(self,'aspect') else '9:16'
        history=self.store.final_output_history(self.project)
        key=f'{variant}|{aspect}'
        row=next((x for x in history if x.get('key')==key),None)
        output=Path(row['output_path']) if row and row.get('output_path') else self.store.root/'final'/self.project.id/f'final-{aspect.replace(":", "x")}-v{variant}.mp4'
        media=self.store.inspect_final_output(output,aspect)
        routes=self._final_delivery_repair_routes(gate,media)
        return {'gate':gate,'media_check':media,'repair_routes':routes,'output_path':str(output),'variant_index':variant,'aspect':aspect,'delivery_ready':bool(gate.get('allowed')) and bool(media.get('valid'))}

    @ui_action
    def final_delivery_center(self):
        """最终成片交付中心：历史、总检查、问题回退和一键重新检查。"""
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        result=self._run_final_delivery_recheck()
        win=tk.Toplevel(self); win.title('最终成片交付中心'); win.geometry('1220x780'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='最终成片交付中心',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        status=tk.StringVar()
        ttk.Label(frm,textvariable=status,font=('Microsoft YaHei UI',13,'bold')).pack(anchor='w',pady=(4,8))
        tree=ttk.Treeview(frm,columns=('key','status','aspect','duration','shots','created','exists','path'),show='headings',height=8)
        for c,t,w in [('key','方案·画幅',100),('status','交付状态',90),('aspect','画幅',70),('duration','时长',70),('shots','镜头数',70),('created','创建时间',170),('exists','文件',60),('path','成片路径',480)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='x',pady=(0,8))
        issues=tk.Text(frm,height=16); issues.pack(fill='both',expand=True,pady=(4,8))
        def render(result):
            status.set('🟢 可以交付' if result['delivery_ready'] else '🔴 暂不能交付')
            for item in tree.get_children(): tree.delete(item)
            for row in self.store.final_output_history(self.project):
                tree.insert('', 'end', values=(row['key'],row['delivery_status'],row['aspect'],f"{row['duration_seconds']}s",row['shot_count'],row.get('created_at',''), '存在' if row['exists'] else '缺失',row['output_path']))
            issues.config(state='normal'); issues.delete('1.0','end')
            issues.insert('end',f"当前检查：方案{result['variant_index']}｜{result['aspect']}\n")
            issues.insert('end',f"安全闸门：{'通过' if result['gate']['allowed'] else '拦截'}\n")
            issues.insert('end',f"媒体质检：{'通过' if result['media_check']['valid'] else '失败'}｜{result['media_check'].get('reason','')}\n")
            issues.insert('end',f"成片路径：{result['output_path']}\n\n")
            routes=result.get('repair_routes') or []
            if routes:
                issues.insert('end','【问题 → 正确修复环节】\n')
                for i,r in enumerate(routes,1):
                    issues.insert('end',f"{i}. {r['issue']}\n   → {r['route']}：{r['action']}\n")
            else:
                issues.insert('end','【问题 → 正确修复环节】\n当前没有发现需要修复的问题。\n')
            issues.insert('end','\n【数据边界】\n本中心只重新检查项目已有资料、已有视觉分析和实际输出文件；不会生成投放数据，不会猜测投放平台，也不会自动生成新的素材。')
            issues.config(state='disabled')
        render(result)
        bar=ttk.Frame(frm); bar.pack(fill='x')
        def recheck():
            latest=self._run_final_delivery_recheck()
            if latest:
                render(latest)
                self.detail.set('最终交付检查已重新执行：'+('可以交付' if latest['delivery_ready'] else '存在需要修复的问题'))
        ttk.Button(bar,text='🔄 一键重新检查',command=recheck).pack(side='left')
        ttk.Button(bar,text='🛡 返回创意事实检查',command=self.creative_fact_check_report).pack(side='left',padx=6)
        ttk.Button(bar,text='🎥 返回成片视觉复核',command=self.visual_fact_check_report).pack(side='left',padx=6)
        ttk.Button(bar,text='🔍 返回AI补镜头复核',command=self.review_hybrid_gap_shots).pack(side='left',padx=6)
        ttk.Button(bar,text='关闭',command=win.destroy).pack(side='right')

    @ui_action
    def variant_matrix_report(self):
        """展示广告投放多版本的测试轴、差异和独立成片；只读取项目已有数据。"""
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        variants=plan.get('creative_variants') or []
        audit=plan.get('variant_set_audit') or {}
        outputs=plan.get('variant_outputs') or {}
        performance=plan.get('variant_performance') or {}
        win=tk.Toplevel(self); win.title('投放版本矩阵'); win.geometry('1180x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='广告投放版本矩阵',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        task=plan.get('task_type','未指定')
        score=audit.get('diversity_score','未审计')
        ttk.Label(frm,text=f'任务类型：{task}｜版本数：{len(variants)}｜版本差异度：{score}｜本窗口不调用新 AI',wraplength=1120).pack(anchor='w',pady=(4,10))
        tree=ttk.Treeview(frm,columns=('version','axis','hook','selling','proof','cta','output','status','metrics'),show='headings')
        heads=[('version','版本',70),('axis','测试轴',110),('hook','Hook/钩子',180),('selling','核心卖点',180),('proof','证明方式',160),('cta','CTA',150),('output','成片路径',210),('status','状态',80),('metrics','投放数据',220)]
        for col,title,width in heads:
            tree.heading(col,text=title); tree.column(col,width=width,anchor='w')
        tree.pack(fill='both',expand=True)
        for i,v in enumerate(variants,1):
            axis=v.get('variant_test_axis') or {}
            out=outputs.get(str(i),{}) if isinstance(outputs,dict) else {}
            hook=v.get('hook','')
            selling=v.get('strategy','') or (v.get('selling_points') or [''])[0]
            proof=v.get('video_form','') or v.get('proof','')
            cta=v.get('cta','') or v.get('script','')[-80:]
            path=out.get('path','未生成')
            status=out.get('status','未输出')
            m=performance.get(str(i),{}) if isinstance(performance,dict) else {}
            metrics_text=(f"CTR {float(m.get('ctr',0))*100:.2f}%｜CVR {float(m.get('cvr',0))*100:.2f}%｜ROAS {float(m.get('roas',0)):.2f}" if m else '未回写')
            tree.insert('', 'end', values=(f'方案{i}',axis.get('name','未指定'),str(hook)[:80],str(selling)[:80],str(proof)[:70],str(cta)[:70],path,status,metrics_text))
        detail=tk.Text(frm,height=8); detail.pack(fill='x',pady=(10,6))
        detail.insert('1.0','版本差异审计：\n')
        for pair in audit.get('pairs',[]):
            detail.insert('end',f"方案{pair.get('a')} ↔ 方案{pair.get('b')}：{'、'.join(pair.get('different_fields',[])) or '无差异'}\n")
        detail.config(state='disabled')
        ttk.Label(frm,text='说明：这是投放前的创意版本矩阵，不代表真实投放数据；真实点击率、转化率等需要进入广告平台后再比较。',foreground='#666',wraplength=1120).pack(anchor='w')
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=(8,0))

    @ui_action
    def creative_variant_analysis_report(self):
        """投放前分析多版本创意差异；不假设渠道、不生成平台数据、不自动选择投放平台。"""
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        variants=plan.get('creative_variants') or []
        if not variants:
            return messagebox.showinfo('提示','当前项目还没有多版本创意。')

        def text_value(value):
            if isinstance(value, list):
                return '、'.join(str(x) for x in value if x)
            if isinstance(value, dict):
                return '、'.join(f'{k}:{v}' for k,v in value.items() if v)
            return str(value or '').strip()

        fields=[
            ('variant_test_axis','测试轴'),
            ('hook','Hook/开场'),
            ('strategy','核心策略'),
            ('selling_points','核心卖点'),
            ('video_form','视频形式'),
            ('proof','证明方式'),
            ('cta','行动引导'),
            ('target_audience','目标人群'),
            ('pain_points','用户痛点'),
        ]
        rows=[]
        for i,v in enumerate(variants,1):
            row={'方案':f'方案{i}'}
            axis=v.get('variant_test_axis') or {}
            for key,label in fields:
                value=axis.get('name') if key=='variant_test_axis' and isinstance(axis,dict) else v.get(key,'')
                if key=='proof' and not value:
                    value=v.get('video_form','')
                if key=='cta' and not value:
                    value=v.get('script','')[-100:]
                if key=='selling_points' and not value:
                    value=v.get('selling_point','')
                row[label]=text_value(value)
            rows.append(row)

        pair_lines=[]
        for a in range(len(rows)):
            for b in range(a+1,len(rows)):
                diffs=[label for _,label in fields if rows[a][label] != rows[b][label] and (rows[a][label] or rows[b][label])]
                pair_lines.append(f"{rows[a]['方案']} ↔ {rows[b]['方案']}：{'、'.join(diffs) if diffs else '没有识别到明显差异'}")

        # 只根据创意本身生成可解释结论；没有真实投放数据时绝不宣称“胜出”。
        axis_values=[r['测试轴'] for r in rows if r['测试轴']]
        unique_axes=list(dict.fromkeys(axis_values))
        data_note='当前没有使用任何广告平台数据。下面的判断只回答“创意有什么不同、下一轮应该继续测试什么”。'
        if len(unique_axes) == 1 and len(rows) > 1:
            data_note += ' 多个方案的测试轴相同，建议下一轮先拉开测试轴，否则很难判断哪一种创意逻辑更有效。'
        elif len(unique_axes) > 1:
            data_note += f' 当前识别到 {len(unique_axes)} 种不同测试轴。'

        performance=plan.get('variant_performance') or {}
        performance_note='尚未回写真实投放数据，因此不评选投放胜出方案。'
        if isinstance(performance,dict) and any(isinstance(x,dict) and x for x in performance.values()):
            performance_note='检测到已回写的真实投放数据；这些数据仅作为附加参考，不改变本报告的投放前创意判断。'

        win=tk.Toplevel(self); win.title('创意方案分析'); win.geometry('1180x760'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='多版本创意分析（投放前）',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text=data_note,wraplength=1120,foreground='#555').pack(anchor='w',pady=(4,4))
        ttk.Label(frm,text=performance_note,wraplength=1120,foreground='#555').pack(anchor='w',pady=(0,10))

        tree=ttk.Treeview(frm,columns=('version','axis','hook','strategy','selling','proof','cta','audience'),show='headings')
        heads=[
            ('version','方案',70),('axis','测试轴',120),('hook','Hook/开场',180),
            ('strategy','核心策略',170),('selling','核心卖点',180),('proof','证明方式',150),
            ('cta','行动引导',150),('audience','目标人群',150)
        ]
        for col,title,width in heads:
            tree.heading(col,text=title); tree.column(col,width=width,anchor='w')
        tree.pack(fill='both',expand=True)
        for r in rows:
            tree.insert('', 'end', values=tuple(r[x] for x in ['方案','测试轴','Hook/开场','核心策略','核心卖点','证明方式','行动引导','目标人群']))

        detail=tk.Text(frm,height=10)
        detail.pack(fill='x',pady=(10,6))
        detail.insert('1.0','【方案之间的结构差异】\n')
        detail.insert('end','\n'.join(pair_lines) or '没有可比较的方案。')
        detail.insert('end','\n\n【下一轮创意测试建议】\n')
        suggestions=[]
        if len(rows)>=2:
            suggestions.append('保留当前表现形式中真正不同的创意轴，不要只改字幕、颜色或镜头顺序来制造“假差异”。')
        missing_axis=sum(1 for r in rows if not r['测试轴'])
        if missing_axis:
            suggestions.append(f'有 {missing_axis} 个方案没有明确测试轴；下一轮应给每个方案写清楚“这版到底在验证什么”。')
        if any(not r['证明方式'] for r in rows):
            suggestions.append('至少保留一版强化产品证据/使用证明的创意，用来验证“说出来”与“证明出来”的差别。')
        if any(not r['Hook/开场'] for r in rows):
            suggestions.append('补齐开场钩子差异：下一轮应明确每版前几秒要让用户停下来的不同理由。')
        if not suggestions:
            suggestions.append('当前结构化差异已经比较完整；下一轮优先围绕现有测试轴继续做更强、更极端的对照，而不是随机改元素。')
        detail.insert('end','\n'.join(f'• {x}' for x in suggestions))
        detail.config(state='disabled')

        ttk.Label(frm,text='重要：本报告不会猜测你要投抖音、淘宝、拼多多、小红书或京东，也不会凭空生成点击率、转化率、ROI 等数据。真正投放后，只有你提供对应平台的真实数据，系统才进入投放结果分析。',wraplength=1120,foreground='#666').pack(anchor='w',pady=(2,8))
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e')

    @ui_action
    def creative_test_plan_report(self):
        """显示投放前创意测试方案；只定义测试目的和观察项，不生成真实结果。"""
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        variants=plan.get('creative_variants') or []
        if not variants:
            return messagebox.showinfo('提示','当前项目还没有多版本创意。')
        test_plan=build_creative_test_plan(variants,plan.get('variant_set_audit') or {})
        plan['creative_test_plan']=test_plan
        self.store.save(self.project)
        win=tk.Toplevel(self); win.title('创意测试方案'); win.geometry('1120x720'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='创意测试方案（投放前）',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='先把“这几版到底要验证什么”写清楚；这里不猜投放平台，也不填写虚假效果数据。',foreground='#555',wraplength=1050).pack(anchor='w',pady=(4,10))
        tree=ttk.Treeview(frm,columns=('version','purpose','axis','design','status'),show='headings')
        for c,t,w in [('version','方案',70),('purpose','测试目的',260),('axis','主要测试轴',150),('design','版本设计',520),('status','结果状态',120)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both',expand=True)
        for item in test_plan.get('variants',[]):
            d=item.get('version_design') or {}
            design='；'.join(f'{k}：{v}' for k,v in d.items() if v)
            axis=item.get('primary_test_axis') or {}
            tree.insert('', 'end', values=(f"方案{item.get('variant_index')}",item.get('test_purpose','-'),axis.get('name','未明确'),design or '未提取',item.get('result_status','待真实投放数据')))
        detail=tk.Text(frm,height=9); detail.pack(fill='x',pady=(10,6))
        detail.insert('1.0','【需要观察的真实结果】\n')
        for item in test_plan.get('variants',[]):
            detail.insert('end',f"方案{item.get('variant_index')}：\n")
            for target in item.get('observation_targets',[]): detail.insert('end',f"  • {target}\n")
        detail.insert('end','\n【下一轮建议】\n')
        for item in test_plan.get('next_round_recommendations',[]): detail.insert('end',f"• {item}\n")
        detail.insert('end','\n数据边界：'+str(test_plan.get('data_boundary','')))
        detail.config(state='disabled')
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=(8,0))

    @ui_action
    def creative_fact_check_report(self):
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        variants=plan.get('creative_variants') or []
        if not variants:
            return messagebox.showinfo('提示','当前项目还没有多版本创意。')
        raw_forbidden=plan.get('forbidden_terms') or plan.get('forbidden_words') or []
        if isinstance(raw_forbidden,str): raw_forbidden=[x.strip() for x in raw_forbidden.replace('，',',').split(',') if x.strip()]
        audit=audit_creative_factual_consistency(self.project.product_info or {},variants,raw_forbidden)
        plan['creative_fact_audit']=audit
        self.store.save(self.project)
        win=tk.Toplevel(self); win.title('创意事实与质量检查'); win.geometry('1180x720'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='创意事实与质量检查（投放前）',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='只检查已有商品资料和用户维护的禁用词；没有证据的内容不会被AI当成事实。画面/字幕一致性标记为待复核。',foreground='#555',wraplength=1120).pack(anchor='w',pady=(4,10))
        tree=tk.Text(frm,height=28); tree.pack(fill='both',expand=True)
        for x in audit['variants']:
            tree.insert('end',f"方案{x['variant_index']}｜{x['product_fact_status']}\n")
            tree.insert('end',f"  未被商品资料支持的卖点：{'、'.join(x['unsupported_selling_points']) or '无'}\n")
            tree.insert('end',f"  禁用词命中：{'、'.join(x['forbidden_term_hits']) or '无'}\n")
            tree.insert('end',f"  高风险绝对化表达：{'、'.join(x['absolute_or_high_risk_claims']) or '无'}\n")
            tree.insert('end',f"  商品主体是否被遮挡：{x['product_subject_obscured']}\n")
            tree.insert('end',f"  画面与商品事实：{x['visual_fact_match']}\n")
            tree.insert('end',f"  字幕与商品事实：{x['subtitle_product_consistency']}\n\n")
        tree.config(state='disabled')
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=8)

    @ui_action
    def storyboard_fact_check_report(self):
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        variants=(self.project.creative_plan or {}).get('creative_variants') or []
        if not variants:
            return messagebox.showinfo('提示','当前项目还没有多版本创意。')
        audit=audit_storyboard_fact_consistency(self.project.product_info or {},variants)
        self.project.creative_plan['storyboard_fact_audit']=audit
        self.store.save(self.project)
        win=tk.Toplevel(self); win.title('分镜事实复核'); win.geometry('1180x760'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='分镜与商品事实复核（投放前）',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='文字层只做资料对应；商品外观、遮挡、功能演示和字幕画面一致性必须看实际分镜/成片，系统不会假装已经看过。',foreground='#555',wraplength=1120).pack(anchor='w',pady=(4,10))
        tree=tk.Text(frm,height=30); tree.pack(fill='both',expand=True)
        for v in audit['variants']:
            tree.insert('end',f"方案{v['variant_index']}｜镜头数：{v['shot_count']}\n")
            for x in v['shots']:
                tree.insert('end',f"  镜头{x['shot_index']}｜资料对应：{'、'.join(x['covered_facts']) or '无'}｜事实状态：{x['fact_status']}\n")
                tree.insert('end',f"    商品主体：{x['product_focus']}｜遮挡：{x['obscured']}｜外观一致：{x['appearance_fidelity']}｜功能一致：{x['function_fidelity']}｜字幕画面一致：{x['subtitle_visual_consistency']}\n")
        tree.config(state='disabled')
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=8)

    @ui_action
    def visual_fact_check_report(self):
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}
        analysis=plan.get('footage_visual_analysis') or {}
        variant_plans=plan.get('variant_footage_plans') or {}
        if not analysis:
            return messagebox.showinfo('暂无视觉分析','当前项目还没有关键帧视觉分析结果。请先分析实拍素材。')
        audit=audit_visual_fact_consistency(self.project.product_info or {},analysis,variant_plans)
        plan['visual_fact_audit']=audit
        self.store.save(self.project)
        win=tk.Toplevel(self); win.title('成片视觉事实复核'); win.geometry('1220x760'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='成片视觉事实复核',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='以下结果来自实拍素材关键帧的视觉模型分析，并映射到实际剪辑方案；“需复核”不会被自动当成通过。',foreground='#555',wraplength=1160).pack(anchor='w',pady=(4,10))
        tree=ttk.Treeview(frm,columns=('variant','source','status','tags','points','risk','reason'),show='headings')
        for c,t,w in [('variant','方案',70),('source','素材',170),('status','状态',120),('tags','视觉标签',190),('points','对应卖点',180),('risk','风险',230),('reason','视觉判断',260)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both',expand=True)
        for v in audit['variants']:
            for x in v['shots']:
                tree.insert('', 'end', values=(v['variant_index'],x['source'],x['risk_status'],'、'.join(x['visual_tags']) or '无','、'.join(x['covered_selling_points']) or '无','；'.join(x['risks']) or '无',x['reason']))
        ttk.Button(frm,text='关闭',command=win.destroy).pack(anchor='e',pady=8)

    def _variant_metrics(self, raw):
        """根据人工/平台回写的原始投放数据计算统一指标；不自动调用广告平台。"""
        raw = raw if isinstance(raw, dict) else {}
        impressions = max(0, int(raw.get('impressions', 0) or 0))
        clicks = max(0, int(raw.get('clicks', 0) or 0))
        conversions = max(0, int(raw.get('conversions', 0) or 0))
        spend = max(0.0, float(raw.get('spend_rmb', 0) or 0))
        revenue = max(0.0, float(raw.get('revenue_rmb', 0) or 0))
        ctr = clicks / impressions if impressions else 0.0
        cvr = conversions / clicks if clicks else 0.0
        cpc = spend / clicks if clicks else 0.0
        cpa = spend / conversions if conversions else 0.0
        roas = revenue / spend if spend else 0.0
        return {
            'impressions': impressions, 'clicks': clicks, 'conversions': conversions,
            'spend_rmb': round(spend, 4), 'revenue_rmb': round(revenue, 4),
            'ctr': round(ctr, 6), 'cvr': round(cvr, 6),
            'cpc_rmb': round(cpc, 4), 'cpa_rmb': round(cpa, 4), 'roas': round(roas, 6),
        }

    @ui_action
    def _record_variant_performance(self, project, variant_index, payload):
        """只写入用户明确提供的投放原始数据；系统不连接平台、不验证真实性。"""
        import datetime
        metrics=project.creative_plan.setdefault('variant_performance', {})
        provenance=project.creative_plan.setdefault('variant_performance_provenance', {})
        payload=dict(payload or {})
        payload['updated_at']=datetime.datetime.now().isoformat(timespec='seconds')
        metrics[str(int(variant_index))]=payload
        provenance[str(int(variant_index))]={
            'source_type':'user_provided',
            'statement':'用户提供的平台数据；系统不验证真实性',
            'verification_status':'unverified',
            'updated_at':payload['updated_at'],
        }
        return payload

    def variant_performance_entry(self):
        """人工回写真实投放结果；只记录数据，不自动投放、不伪造平台数据。"""
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        variants=self.project.creative_plan.get('creative_variants') or []
        if not variants:
            return messagebox.showinfo('提示','当前项目没有多版本创意。')
        win=tk.Toplevel(self); win.title('回写投放数据'); win.geometry('720x560'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='回写真实投放数据',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='这里只记录你从广告平台获得的数据，不会自动创建广告、修改广告账户或虚构结果。保存后会自动计算 CTR / CVR / CPC / CPA / ROAS。',wraplength=680,foreground='#555').pack(anchor='w',pady=(3,12))
        labels=[('版本','variant'),('曝光量','impressions'),('点击量','clicks'),('转化量','conversions'),('消耗（¥）','spend_rmb'),('成交金额（¥）','revenue_rmb')]
        vars={}
        for row,(label,key) in enumerate(labels):
            ttk.Label(frm,text=label,width=16).grid(row=row,column=0,sticky='w',pady=6)
            if key=='variant':
                v=tk.StringVar(value=f'方案{self.active_variant_index}')
                box=ttk.Combobox(frm,textvariable=v,values=[f"方案{i}" for i in range(1,len(variants)+1)],state='readonly')
                box.grid(row=row,column=1,sticky='ew',padx=8,pady=6); vars[key]=v
            else:
                v=tk.StringVar(value='0'); ttk.Entry(frm,textvariable=v).grid(row=row,column=1,sticky='ew',padx=8,pady=6); vars[key]=v
        frm.columnconfigure(1,weight=1)
        result=tk.StringVar(value='尚未计算')
        ttk.Label(frm,textvariable=result,wraplength=680).grid(row=7,column=0,columnspan=2,sticky='w',pady=10)
        def save_metrics():
            try:
                idx=int(vars['variant'].get().replace('方案',''))
                payload=self._variant_metrics({k:vars[k].get() for k in ('impressions','clicks','conversions','spend_rmb','revenue_rmb')})
            except (TypeError,ValueError) as exc:
                return messagebox.showerror('数据格式错误',f'请填写有效的数字：{exc}')
            payload=self._record_variant_performance(self.project, idx, payload)
            self.store.save(self.project)
            result.set(f"方案{idx}｜CTR {payload['ctr']*100:.2f}%｜CVR {payload['cvr']*100:.2f}%｜CPC ¥{payload['cpc_rmb']:.2f}｜CPA ¥{payload['cpa_rmb']:.2f}｜ROAS {payload['roas']:.2f}")
            messagebox.showinfo('已保存','投放数据已写入当前项目的版本矩阵。')
        def load_selected(_=None):
            try: idx=int(vars['variant'].get().replace('方案',''))
            except ValueError: return
            old=(self.project.creative_plan.get('variant_performance') or {}).get(str(idx),{})
            for key in ('impressions','clicks','conversions','spend_rmb','revenue_rmb'):
                vars[key].set(str(old.get(key,0)))
            if old:
                result.set(f"方案{idx}｜CTR {float(old.get('ctr',0))*100:.2f}%｜CVR {float(old.get('cvr',0))*100:.2f}%｜CPC ¥{float(old.get('cpc_rmb',0)):.2f}｜CPA ¥{float(old.get('cpa_rmb',0)):.2f}｜ROAS {float(old.get('roas',0)):.2f}")
        ttk.Button(frm,text='读取当前版本数据',command=load_selected).grid(row=8,column=0,sticky='w',pady=8)
        ttk.Button(frm,text='保存并计算',command=save_metrics).grid(row=8,column=1,sticky='e',pady=8)
        vars['variant'].trace_add('write',lambda *_: load_selected())
        load_selected()

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
        def show_reason(event=None):
            sel=tree.selection()
            if not sel: return
            vals=tree.item(sel[0],'values')
            detail.delete('1.0','end')
            detail.insert('1.0',
                f"素材：{vals[0]}\n排名：{vals[1]}｜综合分：{vals[2]}｜AI评分：{vals[3]}\n"
                f"可用：{vals[4]}｜重复组：{vals[5]}｜最佳Take：{vals[6]}\n"
                f"AI判断：{vals[7]}\n画面标签：{vals[8]}\n推荐片段：{vals[9]}\n口播质量：{vals[10]}")
        detail=tk.Text(frm,height=7); detail.pack(fill='x',pady=(8,4))
        tree.bind('<<TreeviewSelect>>',show_reason)
        ttk.Label(frm,text='选中素材后，下方会显示 AI 为什么保留/淘汰它，以及推荐使用哪一段。',foreground='#666').pack(anchor='w')
        def show_timeline():
            plans=plan.get('variant_footage_plans') or {}
            if not plans and plan.get('footage_plan'):
                plans={str(plan.get('variant_index',1)): plan.get('footage_plan')}
            if not plans:
                return messagebox.showinfo('暂无剪辑方案','当前项目还没有保存实拍剪辑方案。')
            tw=tk.Toplevel(win); tw.title('实拍剪辑决策时间线'); tw.geometry('1180x680'); tw.transient(win)
            tf=ttk.Frame(tw,padding=14); tf.pack(fill='both',expand=True)
            ttk.Label(tf,text='实拍剪辑决策时间线',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
            ttk.Label(tf,text='这里展示 AI 最终决定“用哪条素材、哪一段、为什么这样排”的已保存结果，不会重新调用 AI。',foreground='#666').pack(anchor='w',pady=(3,8))
            vb=tk.StringVar(value=sorted(plans.keys(),key=lambda x:int(x))[0])
            selector=ttk.Combobox(tf,textvariable=vb,state='readonly',values=[f"{k}｜{(plan.get('creative_variants') or [{}])[int(k)-1].get('_variant_label','方案'+k) if int(k)-1 < len(plan.get('creative_variants') or []) else '方案'+k}" for k in sorted(plans,key=lambda x:int(x))],width=40)
            selector.pack(anchor='w',pady=(0,8))
            tree2=ttk.Treeview(tf,columns=('seq','source','ranges','duration','objective','visual','reason'),show='headings')
            for c,t,w in [('seq','镜头','55'),('source','素材','150'),('ranges','使用片段','150'),('duration','时长','70'),('objective','镜头目的','180'),('visual','画面/构图','250'),('reason','决策依据','250')]: tree2.heading(c,text=t); tree2.column(c,width=w,anchor='w')
            tree2.pack(fill='both',expand=True)
            detail2=tk.Text(tf,height=6); detail2.pack(fill='x',pady=(8,0))
            def fill_timeline(*_):
                tree2.delete(*tree2.get_children()); detail2.delete('1.0','end')
                key=vb.get().split('｜',1)[0]; items=plans.get(key,[]) if isinstance(plans.get(key),list) else []
                for i,item in enumerate(items,1):
                    ranges=item.get('ranges') or [[item.get('start',0),item.get('start',0)+item.get('duration',0)]]
                    rt='；'.join(f"{float(a):.1f}-{float(b):.1f}s" for a,b in ranges)
                    tree2.insert('', 'end', values=(i,item.get('source','-'),rt,f"{float(item.get('duration',0)):.1f}s",item.get('objective','-'),item.get('visual','-'),item.get('reason','-')))
                if items:
                    detail2.insert('1.0','说明：每个镜头的“使用片段”可能由多段范围组成，用于删除口播废话、停顿和重复内容；顺序就是最终剪辑顺序。')
            selector.bind('<<ComboboxSelected>>',fill_timeline); fill_timeline()
            ttk.Button(tf,text='关闭',command=tw.destroy).pack(anchor='e',pady=(8,0))
        ttk.Button(frm,text='🎬 查看实拍剪辑决策时间线',command=show_timeline).pack(anchor='e',pady=(4,0))
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
        completion=tasks_data.get('completion_audit') or {}
        hybrid_summary=tasks_data.get('hybrid_resolution') or {}
        counts=hybrid_summary.get('counts') or {}
        ttk.Label(frm,text=f"当前缺口任务：{len(tasks)} 个｜来源覆盖率：{tasks_data.get('source_coverage_score','未审计')}%｜本轮验收：完成 {completion.get('completed_count',0)}｜仍缺失 {completion.get('still_missing_count',0)}｜待复核 {completion.get('review_count',0)}｜下一步：补拍 {counts.get('继续补拍',0)}｜AI补镜头 {counts.get('AI补镜头',0)}｜人工确认 {counts.get('需要人工确认',0)}").pack(anchor='w',pady=(4,10))
        tree=ttk.Treeview(frm,columns=('id','status','type','priority','need','point','resolution','action','acceptance'),show='headings')
        for c,t,w in [('id','任务',80),('status','状态',80),('type','处理方式',80),('priority','优先级',70),('need','缺口',180),('point','关联卖点',120),('resolution','下一步',110),('action','怎么补',260),('acceptance','验收标准',300)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both',expand=True)
        for x in tasks:
            tree.insert('', 'end', values=(x.get('task_id','-'),x.get('status','待处理'),x.get('type','-'),x.get('priority','-'),x.get('need','-'),x.get('related_selling_point','-'),x.get('recommended_resolution','-'),x.get('shoot_or_generate','-'),x.get('acceptance','-')))
        ttk.Label(frm,text='闭环下一步：完成这些任务后，把新增素材放回原素材文件夹，再执行“重新分析实拍素材”，系统会重新进入视觉分析→素材排名→覆盖审计→分镜复核，并自动比较新旧分镜。',wraplength=1050,justify='left').pack(anchor='w',pady=10)
        def show_task(event=None):
            sel=tree.selection()
            if not sel:return
            task=tasks[tree.index(sel[0])]
            detail.delete('1.0','end')
            detail.insert('1.0',
                f"任务：{task.get('task_id','-')}｜优先级：{task.get('priority','-')}\n"
                f"缺口：{task.get('need','-')}\n关联卖点：{task.get('related_selling_point','-') or '无'}\n"
                f"为什么需要：{task.get('why','-')}\n判断依据：{task.get('reason','-')}\n\n"
                f"➡️ 下一步：{task.get('recommended_resolution','-')}\n{task.get('resolution_reason','-')}\n\n📱 怎么拍/怎么补：\n{task.get('shoot_or_generate','-')}\n\n"
                f"✅ 合格标准：\n{task.get('acceptance','-')}")
        detail=tk.Text(frm,height=10); detail.pack(fill='x',pady=(6,8))
        tree.bind('<<TreeviewSelect>>',show_task)
        ttk.Label(frm,text='选中任务后，可以直接照着“怎么拍”和“合格标准”补素材；完成后放回原素材文件夹，再重新分析。',foreground='#666',wraplength=1050,justify='left').pack(anchor='w')
        change_audit=(self.project.creative_plan.get('footage_selection_audit') or {}).get('change_audit') or {}
        if change_audit.get('changed'):
            ttk.Label(frm,text=f"🎬 分镜已自动重规划：新增 {len(change_audit.get('added_shots',[]))} 个镜头｜移除 {len(change_audit.get('removed_shots',[]))} 个镜头｜新增覆盖卖点：{'、'.join(change_audit.get('newly_covered_selling_points',[])) or '无'}",foreground='#333',wraplength=1050,justify='left').pack(anchor='w',pady=(0,6))
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
            from .footage import scan_footage, FootageError, validate_footage_plan, audit_footage_coverage, audit_final_footage_plan, audit_footage_gap_completion, merge_gap_task_acceptance, audit_footage_plan_change
            clips=scan_footage(folder)
            usable=[c for c in clips if c.duration>0]
            if not usable:
                return messagebox.showerror('没有可分析素材','当前文件夹中没有可解析的视频素材。')
            info=self.project.product_info or {}
            constraints=self._creative_constraints()
            analysis_dir=PROJECTS/self.project.id/'footage-analysis'
            manifest=build_visual_manifest(usable,analysis_dir,max_frames_per_clip=4)
            # 先留档上一轮状态，再覆盖本轮分析字段；失败时用户仍可追溯历史方案。
            previous_variant_gap_tasks = self.project.creative_plan.get('variant_footage_gap_tasks') or {}
            previous_variant_plans = self.project.creative_plan.get('variant_footage_plans') or {}
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
            try:
                video_provider=load_video_provider(ROOT/'video-provider.json')
                generation_connected=bool(video_provider.configured())
                generation_rate=float(getattr(video_provider,'cost_per_shot_rmb',0.0) or 0.0)
            except Exception:
                generation_connected=False
                generation_rate=0.0
            budget_total=float((self.project.cost_estimate or {}).get('预算',0) or 0)
            actual_cost=float(getattr(self.project,'actual_cost_rmb',0.0) or 0.0)
            budget_remaining=max(0.0,budget_total-actual_cost) if budget_total > 0 else 0.0
            hybrid=route_footage_gap_tasks(
                gap_tasks.get('tasks',[]),
                generation_connected=generation_connected,
                budget_remaining_rmb=budget_remaining,
                cost_per_ai_shot_rmb=generation_rate,
            )
            gap_tasks['hybrid_resolution']=hybrid
            self.project.creative_plan['footage_hybrid_resolution']=hybrid
            # 任务清单保留原有“待补拍/待补素材/待生成”语义，同时附加下一步执行建议。
            resolved_by_id={str(x.get('task_id')):x for x in hybrid.get('tasks',[]) if isinstance(x,dict)}
            for task in gap_tasks.get('tasks',[]):
                decision=resolved_by_id.get(str(task.get('task_id')), {})
                for key in ('recommended_resolution','generation_allowed','estimated_cost_rmb','resolution_reason'):
                    if key in decision:
                        task[key]=decision[key]
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
    def generate_hybrid_gap_shots(self):
        """执行已获准的 AI 补镜头任务；不自动处理商品事实/真人证据缺口。"""
        if not self._ui_execution_gate(): return
        if not self.project:
            return messagebox.showinfo('提示','请先创建或打开一个项目。')
        tasks=(self.project.creative_plan.get('footage_gap_tasks') or {}).get('tasks') or []
        active_variant_index=int(getattr(self,'active_variant_index',1) or 1)
        approved=[x for x in tasks if isinstance(x,dict) and x.get('recommended_resolution')=='AI补镜头' and x.get('generation_allowed') and int(x.get('variant_index',active_variant_index) or active_variant_index)==active_variant_index]
        if not approved:
            return messagebox.showinfo('没有可执行任务','当前没有经过路由器批准的“AI补镜头”任务。商品/真人证据缺口仍需补拍。')
        try:
            provider=load_video_provider(ROOT/'video-provider.json')
            if not provider.configured():
                raise RuntimeError('视频生成 Provider 尚未真实配置，不能执行 AI 补镜头。')
            rate=float(getattr(provider,'cost_per_shot_rmb',0.72) or 0.72)
        except Exception as exc:
            return messagebox.showerror('AI补镜头不可用',str(exc))
        budget=float((self.project.cost_estimate or {}).get('预算',0) or 0)
        actual=float(getattr(self.project,'actual_cost_rmb',0.0) or 0.0)
        remaining=max(0.0,budget-actual) if budget>0 else 0.0
        pending=[x for x in approved if not x.get('generated_path') or not Path(str(x.get('generated_path'))).exists()]
        if not pending:
            return messagebox.showinfo('无需生成','当前所有已批准的 AI 补镜头任务都已有生成文件。')
        # The video call can also generate missing actor/scene/product assets inside render_shot.
        # Include those potential cloud costs before authorization; unknown configured prices need
        # a separate explicit warning instead of silently being treated as free.
        asset_estimate=0.0
        unknown_asset_prices=[]
        try:
            asset_config_path=ROOT/'asset-generation.json'
            asset_config=json.loads(asset_config_path.read_text(encoding='utf-8')) if asset_config_path.exists() else {}
            library=LocalLibrary(getattr(self.store,'library_root',ROOT/'library'))
            for kind in ('演员','场景','商品素材'):
                if library.best_match(kind,[]):
                    continue
                cfg=asset_config.get(kind) or asset_config.get('asset_generation') or {}
                endpoint=str(cfg.get('endpoint') or '').strip()
                local_endpoint=cfg.get('local') is True or '127.0.0.1' in endpoint.lower() or 'localhost' in endpoint.lower()
                configured=bool(endpoint) and (bool(cfg.get('api_key')) or local_endpoint)
                if not configured or local_endpoint:
                    continue
                try:
                    price=float(cfg.get('price_rmb',0.0) or 0.0)
                except (TypeError,ValueError):
                    price=0.0
                if price>0:
                    # Conservative: account for each pending task potentially retrying a missing asset.
                    asset_estimate+=price*len(pending)
                else:
                    unknown_asset_prices.append(kind)
        except Exception as exc:
            return messagebox.showerror('AI补镜头成本预估失败',f'无法可靠读取缺失素材成本配置，已停止云端生成：{exc}')
        estimate=round(len(pending)*rate+asset_estimate,4)
        if unknown_asset_prices:
            unknown_text='、'.join(unknown_asset_prices)
            if not messagebox.askyesno('素材生成价格未配置',f'以下云端素材生成服务未配置有效单价：{unknown_text}。本次费用预估不包含这些潜在费用。是否仍继续进入预算确认？'):
                return
        if budget>0 and estimate>remaining:
            if not self._confirm_budget_overrun(estimate,remaining,'AI补镜头预算超限确认'): return
        if not self._authorize_workflow_action('cloud_generation','云端 AI 补镜头授权'): return
        Shot=__import__('ad_studio.models',fromlist=['Shot']).Shot
        results=[]; failures=[]
        for n,task in enumerate(pending,1):
            task_id=str(task.get('task_id') or f'GAP-AI-{n:03d}')
            idx=9000+n
            shot=Shot(
                id=f'hybrid-{task_id.lower().replace("_","-")}',
                index=idx,
                title=f'AI补镜头｜{task.get("need","辅助画面")}',
                visual=str(task.get('need') or '补充通用辅助画面'),
                script=str(task.get('related_selling_point') or ''),
                status='待生成',
                generated_from_request=f'实拍缺口任务 {task_id}：{task.get("reason","")}',
            )
            try:
                out=self.store.render_shot(self.project,shot,config_root=ROOT)
                task['generated_path']=str(out)
                task['status']='AI补镜头已生成'
                task['generation_cost_rmb']=round(float(getattr(shot,'actual_cost_rmb',rate) or 0),4)
                results.append(f'{task_id}：{out}')
            except Exception as exc:
                task['status']='AI补镜头生成失败'
                task['generation_error']=str(exc)
                failures.append(f'{task_id}：{exc}')
        self.project.creative_plan['footage_gap_tasks']['tasks']=tasks
        self.project.creative_plan['hybrid_generated_shots']=[
            {'task_id':str(x.get('task_id')), 'path':str(x.get('generated_path')), 'status':x.get('status')}
            for x in tasks if x.get('generated_path')
        ]
        self.store.save(self.project)
        self.detail.set(f'AI补镜头完成：成功 {len(results)} 个｜失败 {len(failures)} 个；已生成素材不会自动冒充商品证据或自动插入最终分镜。')
        msg=f'成功生成：{len(results)} 个\n失败：{len(failures)} 个'
        if results: msg+='\n\n'+'\n'.join(results[:8])
        if failures: msg+='\n\n失败明细：\n'+'\n'.join(failures[:8])
        messagebox.showinfo('AI补镜头结果',msg)

    @ui_action
    def review_hybrid_gap_shots(self):
        """人工复核已经真实生成的 AI 补镜头；只有明确通过后才进入当前方案分镜。"""
        if not self._ui_execution_gate(): return
        if not self.project: return messagebox.showinfo('提示','请先创建或打开一个项目。')
        plan=self.project.creative_plan or {}; task_box=plan.get('footage_gap_tasks') or {}
        tasks=task_box.get('tasks') if isinstance(task_box,dict) else []
        # 只复核当前激活版本，禁止跨版本把 AI 补镜头带入当前分镜。
        tasks=[x for x in tasks if isinstance(x,dict) and x.get('recommended_resolution')=='AI补镜头' and int(x.get('variant_index',self.active_variant_index) or self.active_variant_index)==self.active_variant_index]
        generated=[x for x in tasks if x.get('generated_path') and Path(str(x.get('generated_path'))).exists()]
        if not generated: return messagebox.showinfo('暂无待复核素材','当前没有已经真实生成、可供人工复核的 AI 补镜头。')
        win=tk.Toplevel(self); win.title('AI补镜头人工复核'); win.geometry('1120x650'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='AI补镜头人工复核',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='只有明确点击“通过并纳入当前分镜”的镜头才会进入最终成片；拒绝的镜头不会参与成片。AI补镜头不得替代商品真实性能、参数或真人口播证据。',wraplength=1050,foreground='#555').pack(anchor='w',pady=(3,10))
        tree=ttk.Treeview(frm,columns=('task','need','status','review','path'),show='headings',height=14)
        for c,t,w in [('task','任务',90),('need','补什么',260),('status','生成状态',130),('review','人工复核',130),('path','生成文件',390)]: tree.heading(c,text=t); tree.column(c,width=w,anchor='w')
        tree.pack(fill='both',expand=True); details=tk.Text(frm,height=8,wrap='word'); details.pack(fill='x',pady=8)
        def row_values(task):
            review='已通过并纳入分镜' if task.get('accepted_into_storyboard') else (task.get('review_status') or '待复核')
            return (task.get('task_id','-'),task.get('need','-'),task.get('status','-'),review,str(task.get('generated_path','-')))
        for task in generated: tree.insert('', 'end', iid=str(task.get('task_id')), values=row_values(task))
        def selected_task():
            sel=tree.selection(); return next((x for x in generated if str(x.get('task_id'))==str(sel[0])),None) if sel else None
        def show_detail(_=None):
            task=selected_task();
            if not task:return
            details.delete('1.0','end'); details.insert('end',f"任务：{task.get('task_id')}\n需求：{task.get('need','')}\n为什么需要：{task.get('why') or task.get('reason','')}\n验收标准：{task.get('acceptance','')}\n文件：{task.get('generated_path','')}\n当前复核：{task.get('review_status','待复核')}\n")
        tree.bind('<<TreeviewSelect>>',show_detail)
        def refresh_row(task):
            iid=str(task.get('task_id'));
            if tree.exists(iid): tree.item(iid,values=row_values(task))
            show_detail()
        def open_video():
            task=selected_task();
            if not task:return
            p=Path(str(task.get('generated_path','')))
            if not p.exists():return messagebox.showerror('文件不存在',str(p))
            try:
                import os
                if hasattr(os,'startfile'): os.startfile(str(p))
                else: subprocess.Popen(['xdg-open',str(p)])
            except Exception as exc: messagebox.showerror('无法打开视频',str(exc))
        def reject():
            task=selected_task();
            if not task:return
            if task.get('accepted_into_storyboard'): return messagebox.showwarning('不能拒绝','该镜头已经纳入当前分镜；如需移除，请在分镜中删除/重新规划。')
            task['review_status']='已拒绝'; task['reviewed_at']=__import__('datetime').datetime.now().isoformat(timespec='seconds'); task['accepted_into_storyboard']=False
            self.store.save(self.project); refresh_row(task)
        def accept():
            task=selected_task();
            if not task:return
            if task.get('accepted_into_storyboard'): return messagebox.showinfo('已纳入','该 AI 补镜头已经在当前分镜中。')
            p=Path(str(task.get('generated_path','')))
            if not p.exists() or p.stat().st_size<=0: return messagebox.showerror('不能纳入','生成文件不存在或为空，不能进入分镜。')
            # 有确定目标位置就插入缺口位置；无法稳定定位时才追加到末尾，避免算法猜错位置。
            target_index=task.get('target_shot_index')
            try: target_index=int(target_index) if target_index is not None else None
            except (TypeError,ValueError): target_index=None
            insert_at=find_variant_insert_position(self.project.shots,target_index)
            max_index=max([int(getattr(s,'index',0)) for s in self.project.shots] or [0])
            Shot=__import__('ad_studio.models',fromlist=['Shot']).Shot
            shot=Shot(id=f"hybrid-{task.get('task_id','gap').lower().replace('_','-')}-v{self.active_variant_index}",index=(target_index if target_index is not None else max_index+1),title=f"AI补镜头｜{task.get('need','辅助画面')}",visual=str(task.get('need') or '补充通用辅助画面'),script=str(task.get('related_selling_point') or ''),status='已复核并纳入分镜',video_path=str(p),clip_source='ai_generated',provider=str(task.get('generation_provider') or 'AI视频生成'),generated_from_request=f"实拍缺口任务 {task.get('task_id')}：{task.get('reason','')}",actual_cost_rmb=round(float(task.get('generation_cost_rmb',0) or 0),4))
            for existing in self.project.shots[insert_at:]: existing.index=int(getattr(existing,'index',0) or 0)+1
            self.project.shots.insert(insert_at,shot); task['accepted_position']=insert_at+1; task['review_status']='已通过'; task['reviewed_at']=__import__('datetime').datetime.now().isoformat(timespec='seconds'); task['accepted_into_storyboard']=True; task['accepted_shot_id']=shot.id; task['accepted_variant_index']=self.active_variant_index; task['status']='AI补镜头已生成并通过人工复核'
            # Adding a shot changes the approved storyboard. Semi-auto and user-controlled
            # modes must review the revised shot list before any further generation.
            invalidate_storyboard_approval(plan, self.active_variant_index)
            plan.setdefault('hybrid_reviewed_shots',[]).append({'task_id':task.get('task_id'),'shot_id':shot.id,'variant_index':self.active_variant_index,'path':str(p),'review_status':'已通过','accepted_at':task['reviewed_at']})
            self._cache_active_variant(); self.store.save(self.project); self.refresh_shots(); self.detail.set(f"AI补镜头 {task.get('task_id')} 已通过人工复核并纳入方案{self.active_variant_index}当前分镜。"); refresh_row(task)
            messagebox.showinfo('已纳入当前分镜',f"{task.get('task_id')} 已作为镜头 {shot.index} 纳入当前方案。现在可以继续后处理或生成最终成片。")
        btn=ttk.Frame(frm); btn.pack(fill='x',pady=(2,0)); ttk.Button(btn,text='▶ 打开视频',command=open_video).pack(side='left'); ttk.Button(btn,text='❌ 拒绝',command=reject).pack(side='left',padx=6); ttk.Button(btn,text='✅ 通过并纳入当前分镜',command=accept).pack(side='left',padx=6); ttk.Button(btn,text='关闭',command=win.destroy).pack(side='right')

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
        shot_actual=round(sum(float(getattr(s,'actual_cost_rmb',0) or 0) for s in (self.project.shots if self.project else [])),4)
        project_actual=float(getattr(self.project,'actual_cost_rmb',0.0) or 0.0) if self.project else 0.0
        # Project ledger includes temporary AI gap shots not yet accepted into storyboard.
        actual=round(max(project_actual,shot_actual),4)
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

    def _plan_dict(self, plan, raw=None):
        raw = raw or {}
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
        previous_plan=self.project.creative_plan if self.project else {}
        existing_variants=previous_plan.get('creative_variants',[]) if self.project else []
        existing_count=previous_plan.get('variant_count',len(existing_variants)) if self.project else 1
        preserved_variant_state={key: value for key, value in previous_plan.items() if key.startswith('variant_')}
        plan=validate_plan(validate_task_type_plan(raw, self._creative_constraints()))
        self.project.form=plan.video_form
        self.project.product_name=info.name
        data=self._plan_dict(plan, raw)
        if existing_variants:
            data['creative_variants']=existing_variants
            data['variant_count']=existing_count
        data.update(preserved_variant_state)
        preserve_workflow_state(previous_plan, data)
        preserve_output_history(previous_plan, data)
        data['variant_index']=int(raw.get('_variant_index',1))
        data['variant_label']=raw.get('_variant_label',f"方案{data['variant_index']}｜{plan.video_form}")
        self.project.creative_plan=data
        self.project.shots=[
            Shot(
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
        self.project.shots=_restore_variant_shot_cache(self.project.shots, saved)
        self._restore_active_variant_runtime()
        return plan

    @ui_action
    def _cache_active_variant(self):
        if not self.project:return
        plan=self.project.creative_plan
        cache=plan.setdefault('variant_shot_cache', {})
        cache[str(self.active_variant_index)]=[dict(s.__dict__) for s in self.project.shots]

        # 镜头之外的运行态也必须按方案隔离：尤其是 AI 补镜头任务。
        # 否则 A 方案生成/复核过的缺口会在切到 B 方案时继续出现在复核窗口。
        gap_tasks=plan.get('footage_gap_tasks')
        if isinstance(gap_tasks, dict):
            variant_tasks=plan.setdefault('variant_footage_gap_tasks', {})
            variant_tasks[str(self.active_variant_index)]=json.loads(json.dumps(gap_tasks, ensure_ascii=False))

        reviewed=plan.get('hybrid_reviewed_shots')
        if isinstance(reviewed, list):
            variant_reviewed=plan.setdefault('variant_hybrid_reviewed_shots', {})
            variant_reviewed[str(self.active_variant_index)]=json.loads(json.dumps(reviewed, ensure_ascii=False))

        # Persist all mutable footage-planning state, not only gap tasks/reviewed shots.
        # These fields are edited during reanalysis and gap completion; if only the
        # active fields change, switching away and back must not resurrect stale maps.
        for field, storage, expected_type in (
            ('footage_plan','variant_footage_plans',list),
            ('footage_selection_audit','variant_footage_selection_audits',dict),
            ('footage_coverage','variant_footage_coverage',dict),
            ('footage_gaps','variant_footage_gaps',dict),
        ):
            value=plan.get(field)
            if isinstance(value, expected_type):
                values=plan.setdefault(storage, {})
                values[str(self.active_variant_index)]=json.loads(json.dumps(value, ensure_ascii=False))

    def _restore_active_variant_runtime(self):
        """恢复当前方案的补素材/混合生成运行态，禁止跨方案串数据。"""
        if not self.project:
            return
        plan=self.project.creative_plan
        idx=str(self.active_variant_index)

        variant_tasks=plan.get('variant_footage_gap_tasks')
        if isinstance(variant_tasks, dict):
            if idx in variant_tasks:
                plan['footage_gap_tasks']=json.loads(json.dumps(variant_tasks[idx], ensure_ascii=False))
            elif variant_tasks:
                # If another variant has task state but this one does not, clear the
                # previous variant's active value instead of leaking it across variants.
                plan['footage_gap_tasks']={}

        variant_reviewed=plan.get('variant_hybrid_reviewed_shots')
        if isinstance(variant_reviewed, dict):
            if idx in variant_reviewed:
                plan['hybrid_reviewed_shots']=json.loads(json.dumps(variant_reviewed[idx], ensure_ascii=False))
            elif variant_reviewed:
                plan['hybrid_reviewed_shots']=[]

        # Restore variant-specific footage decisions. Once per-variant storage exists,
        # a missing entry means "no state for this variant", not "reuse another variant".
        for field, storage in (
            ('footage_plan','variant_footage_plans'),
            ('footage_selection_audit','variant_footage_selection_audits'),
            ('footage_coverage','variant_footage_coverage'),
            ('footage_gaps','variant_footage_gaps'),
        ):
            values=plan.get(storage)
            if isinstance(values, dict):
                if idx in values:
                    plan[field]=json.loads(json.dumps(values[idx], ensure_ascii=False))
                elif values:
                    plan[field]=[] if field == 'footage_plan' else {}

    def _record_variant_output(self, path):
        if not self.project:return
        outputs=self.project.creative_plan.setdefault('variant_outputs', {})
        outputs[str(self.active_variant_index)]={'variant_index':self.active_variant_index,'variant_label':self.project.creative_plan.get('variant_label',f'方案{self.active_variant_index}'),'path':str(path),'status':'已输出'}

    @ui_action
    def _restore_variant_selection(self, variant_index):
        """Restore the user's original active variant after a cancelled preflight."""
        if not self.project:
            return False
        variants=(self.project.creative_plan or {}).get('creative_variants',[])
        target=next((dict(v) for pos,v in enumerate(variants,1)
                     if int(v.get('_variant_index',pos) or pos)==int(variant_index)),None)
        if not target:
            return False
        target['_variant_index']=int(variant_index)
        target['_variant_label']=target.get('_variant_label',f'方案{variant_index}')
        # Save any partial work from the currently active variant before switching back.
        # This is safe for cancellation paths too and prevents error recovery from dropping
        # successful shots or output metadata produced earlier in the batch.
        self._cache_active_variant()
        info=__import__('ad_studio.product_parser',fromlist=['ProductInfo']).ProductInfo(**self.project.product_info)
        self._activate_plan(target,info)
        self.refresh_shots()
        self.show_shot()
        self.store.save(self.project)
        return True

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
        saved_product=load_product_library(url, ROOT)
        info=merge_product_library(info, saved_product)
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
            selected_mode=self._workflow_mode_value()
            if selected_mode == SEMI_AUTO:
                first_plan=raw_plans[0]
                summary=(f"方案：{first_plan.get('_variant_label',first_plan.get('video_form','AI创意方案'))}\\n"
                         f"策略：{str(first_plan.get('strategy',''))[:420]}\\n"
                         f"视频形式：{first_plan.get('video_form','未指定')}\\n\\n"
                         "半自动模式会先停在创意方案确认点。是否采用这套方案并继续？")
                if not messagebox.askyesno('确认 AI 创意方案',summary):
                    self.project=None
                    self.detail.set('用户未批准创意方案；已停止本次项目创建。')
                    return
            if selected_mode == USER_CONTROLLED:
                selected_index=self._choose_initial_plan(raw_plans)
                if selected_index is None:
                    self.project=None
                    self.detail.set('用户取消了创意方案选择；未继续创建项目。')
                    return
                if selected_index:
                    chosen=raw_plans.pop(selected_index)
                    raw_plans.insert(0,chosen)
                    # Re-number fresh-project variants to match their visible list order.
                    for variant_position, candidate in enumerate(raw_plans,1):
                        candidate['_variant_index']=variant_position
            plan=self._activate_plan(raw_plans[0],info)
            set_project_workflow_mode(self.project,selected_mode)
            self.project.creative_plan['creative_variants']=raw_plans
            self.project.creative_plan['variant_count']=variant_count
            # 只审计创意实验设计，不推断投放平台，也不调用任何广告平台数据。
            self.project.creative_plan['variant_set_audit']=audit_ad_variant_set(raw_plans, task_type)
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
                    # 公共视觉分析/废片归档/转写只做一次；每个创意方案独立规划自己的实拍剪辑。
                    variant_footage_plans={}
                    variant_footage_audits={}
                    variant_footage_coverage={}
                    variant_footage_gaps={}
                    variant_footage_tasks={}
                    for variant_pos, variant_raw in enumerate(raw_plans, 1):
                        self._activate_plan(variant_raw, info)
                        variant_plan_dict=dict(self.project.creative_plan)
                        coverage_v=audit_footage_coverage(analysis, variant_plan_dict)
                        gaps_v=classify_footage_gaps(coverage_v, variant_plan_dict, generation_connected=False)
                        tasks_v=build_footage_gap_tasks(coverage_v, gaps_v, variant_plan_dict)
                        # 缺口任务绑定所属创意方案，避免切换 A/B/C 版本后误复核另一版本的 AI 补镜头。
                        variant_idx=int(variant_raw.get('_variant_index',variant_pos))
                        for task in tasks_v:
                            if isinstance(task,dict):
                                task['variant_index']=variant_idx
                        previous_tasks_v=previous_variant_gap_tasks.get(str(int(variant_raw.get('_variant_index',variant_pos))), {}) if isinstance(previous_variant_gap_tasks, dict) else {}
                        completion_v=audit_footage_gap_completion(previous_tasks_v, coverage_v) if previous_tasks_v else {'task_count':0,'completed_count':0,'still_missing_count':0,'review_count':0,'tasks':[],'coverage_score':coverage_v.get('coverage_score',100.0),'method':'首次分析，无上一轮任务可验收'}
                        tasks_v=merge_gap_task_acceptance(tasks_v, completion_v)
                        raw_footage_plan=self.model_router.plan_footage(
                            info.to_dict(), variant_plan_dict,
                            [c.to_public() for c in usable], constraints,
                            footage_analysis=analysis,
                            footage_coverage=coverage_v,
                        )
                        plan_items,warnings_v=validate_footage_plan(raw_footage_plan,usable)
                        final_audit=audit_final_footage_plan(plan_items, analysis, coverage_v)
                        idx=int(variant_raw.get('_variant_index',variant_pos))
                        variant_footage_plans[str(idx)]=final_audit['plan']
                        old_plan=previous_variant_plans.get(str(idx), []) if isinstance(previous_variant_plans, dict) else []
                        final_audit['change_audit']=audit_footage_plan_change(old_plan, final_audit['plan'])
                        variant_footage_audits[str(idx)]=final_audit
                        variant_footage_coverage[str(idx)]=coverage_v
                        variant_footage_gaps[str(idx)]=gaps_v
                        variant_footage_tasks[str(idx)]=tasks_v
                    self.project.creative_plan['variant_footage_plans']=variant_footage_plans
                    self.project.creative_plan['variant_footage_selection_audits']=variant_footage_audits
                    self.project.creative_plan['variant_footage_coverage']=variant_footage_coverage
                    self.project.creative_plan['variant_footage_gaps']=variant_footage_gaps
                    self.project.creative_plan['variant_footage_gap_tasks']=variant_footage_tasks
                    first_raw=raw_plans[0]
                    self._activate_plan(first_raw, info)
                    first_idx=int(first_raw.get('_variant_index',1))
                    first_plan=variant_footage_plans.get(str(first_idx), [])
                    self._apply_footage_plan(first_plan)
                    self.project.creative_plan['footage_coverage']=variant_footage_coverage.get(str(first_idx),{})
                    self.project.creative_plan['footage_gaps']=variant_footage_gaps.get(str(first_idx),{})
                    self.project.creative_plan['footage_gap_tasks']=variant_footage_tasks.get(str(first_idx),{})
                    self.project.creative_plan['footage_selection_audit']=variant_footage_audits.get(str(first_idx),{})
                    self.project.creative_plan['footage_plan']=first_plan
                    warnings=[]
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
        self.store.save(self.project); save_product(info,ROOT,self.project.id); save_product_library(info,ROOT); self.refresh_shots()
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
        if not self._authorize_workflow_action('generate_shot','生成镜头确认'): return
        if not self._ensure_storyboard_approval(): return
        if self.project:
            set_project_workflow_mode(self.project,self._workflow_mode_value())

        filmed=getattr(s,'clip_source','ai_generated')=='filmed'
        decision=None
        if not filmed:
            decision=CapabilityRouter(ROOT).decide_video()
            # Only cloud generation incurs configured provider cost and needs cloud consent.
            # Perform the budget check before changing shot status or invoking any renderer.
            if decision.target == 'cloud':
                try:
                    provider=load_video_provider(ROOT/'video-provider.json')
                    rate=float(getattr(provider,'cost_per_shot_rmb',0.72) or 0.72)
                except Exception:
                    rate=0.72
                budget=float((self.project.cost_estimate or {}).get('预算',0) or 0)
                actual=float(getattr(self.project,'actual_cost_rmb',0.0) or 0.0)
                remaining=max(0.0,budget-actual) if budget>0 else 0.0
                if budget>0 and rate>remaining:
                    if not self._confirm_budget_overrun(rate,remaining,'单镜头生成预算超限确认'):
                        self.detail.set('用户取消了超预算单镜头生成；未调用生成服务。')
                        return
                if not self._authorize_workflow_action('cloud_generation','云端视频生成授权'):
                    self.detail.set('用户未授权云端生成；未调用视频生成服务。')
                    return

        try:
            s.status='生成中…'; self.store.save(self.project); self.refresh_shots()
            self.update_idletasks()
            if filmed:
                src=Path(s.source_file).name if s.source_file else '(未指定素材)'
                self.detail.set(f'镜头 {s.index} 正在从拍摄素材裁剪…（{src}，{s.source_start:.1f}s 起，{s.source_duration:.1f}s）')
                out=self.store.render_footage_shot(self.project,s)
                self.refresh_shots(); self.detail.set(f'镜头 {s.index} 已从拍摄素材裁剪 v{s.version}：{out}')
            else:
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
        if not self._authorize_workflow_action('regenerate_shot','重新生成镜头确认'): return
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
            s.title=title.get().strip() or s.title; s.visual=visual.get('1.0','end').strip(); s.script=script.get('1.0','end').strip(); s.actor_id=actor_map.get(av.get()); s.scene_id=scene_map.get(sv.get()); s.status='需重生成'; s.video_path=None; s.version+=1
            invalidate_storyboard_approval(self.project.creative_plan, self.active_variant_index)
            # Keep the per-variant cache aligned with edits before persistence; otherwise
            # reopening/switching variants could restore the stale pre-edit shot snapshot.
            self._cache_active_variant()
            self.store.save(self.project); self.refresh_shots(); self.show_shot(); win.destroy()
        ttk.Button(frm,text='保存修改并生成新版本',command=apply).pack(anchor='e',pady=10)

    def _restore_loaded_variant_state(self):
        """Restore the active variant's canonical shot/runtime caches after reopening a project."""
        if not self.project:
            return
        plan = self.project.creative_plan or {}
        try:
            index = int(plan.get("variant_index", 1) or 1)
        except (TypeError, ValueError):
            index = 1
        self.active_variant_index = max(1, index)
        cache = plan.get("variant_shot_cache")
        key = str(self.active_variant_index)
        # project.shots and variant_index are saved together. Prefer this active
        # snapshot because a batch may have saved a successful shot before refreshing
        # the secondary cache; only fall back to the cache when the project has no shots.
        if not self.project.shots and isinstance(cache, dict) and key in cache and isinstance(cache[key], list):
            self.project.shots = _restore_variant_shot_cache(self.project.shots, cache[key])
        # The per-variant runtime maps are authoritative whenever present; restore them
        # to avoid stale cross-variant footage state after an interrupted batch/reopen.
        self._restore_active_variant_runtime()

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
            self.project=project; self._restore_loaded_variant_state(); self.model_router.set_project_context(project.id); self.workflow_mode.set(self._workflow_mode_label(get_project_workflow_mode(project))); self.url.set(''); self.level.set(project.level); self.form.set(project.form); self.refresh_shots(); c=project.cost_estimate; self.cost.set(f"项目预估 ¥{c.get('总计',0):.2f} · 云端 ¥{c.get('云端',0):.2f} · 已保存 {len(project.shots)} 个镜头" if c else f'已保存 {len(project.shots)} 个镜头'); self.detail.set(f'已恢复项目：{project.product_name} · {project.platform} · {project.form}'); win.destroy()
        ttk.Button(frm,text='打开',command=open_selected).pack(anchor='e')

    @ui_action
    def product_library_settings(self):
        """商品资料库：维护卖点、规格、禁用词，并按商品链接持久化。"""
        folder=ROOT/'product-library'
        folder.mkdir(parents=True,exist_ok=True)
        files=sorted(folder.glob('*.json'), key=lambda p:p.stat().st_mtime, reverse=True)
        win=tk.Toplevel(self); win.title('商品资料库'); win.geometry('980x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='商品资料库',font=('Microsoft YaHei UI',18,'bold')).pack(anchor='w')
        ttk.Label(frm,text='这里维护的是用户确认过的商品事实：卖点、规格、禁用词。创建项目时会按商品链接自动引用，不会让 AI 自行补写商品事实。',wraplength=920,foreground='#555').pack(anchor='w',pady=(3,10))
        left=ttk.Frame(frm); left.pack(side='left',fill='y',padx=(0,12))
        right=ttk.Frame(frm); right.pack(side='left',fill='both',expand=True)
        box=tk.Listbox(left,width=38,height=24); box.pack(fill='y',expand=True)
        records=[]
        for p in files:
            try:
                raw=json.loads(p.read_text(encoding='utf-8')); records.append(raw)
                box.insert('end',f"{raw.get('name','未命名商品')}｜{raw.get('platform','自动识别')}")
            except Exception:
                continue
        fields={}
        for row,(label,key) in enumerate([('商品名称','name'),('商品链接','url')]):
            ttk.Label(right,text=label).grid(row=row,column=0,sticky='w',pady=4)
            v=tk.StringVar(); ttk.Entry(right,textvariable=v).grid(row=row,column=1,sticky='ew',pady=4); fields[key]=v
        ttk.Label(right,text='核心卖点（每行一个）').grid(row=2,column=0,sticky='nw',pady=4)
        selling=tk.Text(right,height=8); selling.grid(row=2,column=1,sticky='ew',pady=4)
        ttk.Label(right,text='规格/参数（JSON）').grid(row=3,column=0,sticky='nw',pady=4)
        specs=tk.Text(right,height=8); specs.grid(row=3,column=1,sticky='ew',pady=4)
        ttk.Label(right,text='禁用词（每行一个）').grid(row=4,column=0,sticky='nw',pady=4)
        forbidden=tk.Text(right,height=8); forbidden.grid(row=4,column=1,sticky='ew',pady=4)
        right.columnconfigure(1,weight=1)
        def load_selected(_=None):
            sel=box.curselection()
            if not sel:return
            raw=records[sel[0]]
            fields['name'].set(str(raw.get('name',''))); fields['url'].set(str(raw.get('url','')))
            selling.delete('1.0','end'); selling.insert('1.0','\n'.join(map(str,raw.get('selling_points') or [])))
            specs.delete('1.0','end'); specs.insert('1.0',json.dumps(raw.get('specs') or {},ensure_ascii=False,indent=2))
            forbidden.delete('1.0','end'); forbidden.insert('1.0','\n'.join(map(str,raw.get('forbidden_terms') or [])))
        def save_current():
            url=fields['url'].get().strip()
            if not url:return messagebox.showerror('保存失败','商品链接不能为空。')
            try:
                saved=load_product_library(url,ROOT) or ProductInfo(url=url,platform='自动识别')
                saved.name=fields['name'].get().strip() or saved.name
                saved.selling_points=[x.strip() for x in selling.get('1.0','end').splitlines() if x.strip()]
                saved.specs=json.loads(specs.get('1.0','end').strip() or '{}')
                saved.forbidden_terms=[x.strip() for x in forbidden.get('1.0','end').splitlines() if x.strip()]
                path=save_product_library(saved,ROOT)
                messagebox.showinfo('已保存',f'商品资料已保存到商品资料库。\n{path}')
                win.destroy()
                self.product_library_settings()
            except json.JSONDecodeError as exc:
                messagebox.showerror('规格 JSON 错误',f'规格/参数必须是合法 JSON：{exc}')
        ttk.Button(right,text='保存当前商品资料',command=save_current).grid(row=5,column=1,sticky='e',pady=10)
        box.bind('<<ListboxSelect>>',load_selected)
        if records: box.selection_set(0); load_selected()
        ttk.Button(right,text='关闭',command=win.destroy).grid(row=6,column=1,sticky='e')
    
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
        if not self._ui_execution_gate(): return
        if not self.project: return messagebox.showinfo('提示','请先创建或打开一个项目。')
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
        if not self._ui_execution_gate(): return
        if not self.project: return messagebox.showinfo('提示','请先创建或打开一个项目。')
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
    def batch_generate_variants(self):
        """一次生成全部广告版本：预算先审计，逐版本独立生成并最终出片。"""
        if not self._ui_execution_gate(): return
        if not self.project: return messagebox.showinfo('提示','先创建项目。')
        if not self._authorize_workflow_action('generate_all_variants','批量生成版本确认'): return
        variants=self.project.creative_plan.get('creative_variants',[])
        if len(variants)<=1: return messagebox.showinfo('提示','当前只有一个方案，请直接生成当前镜头。')
        # 先锁定用户当前方案；预算预审会逐方案切换，不能把“最后一次预审方案”误当成原方案。
        original_index=self.active_variant_index
        self._cache_active_variant()
        budget=float((self.project.cost_estimate or {}).get('预算',0) or 0)
        footage_mode=self.footage_mode.get().strip() if hasattr(self,'footage_mode') else ''
        try:
            from .providers import load_video_provider
            vp=load_video_provider(ROOT/'video-provider.json')
            rate=float(getattr(vp,'cost_per_shot_rmb',0.72))
        except Exception:
            rate=0.72
        missing_counts=[]; estimated=0.0; needs_cloud_video=False
        try:
            for pos,raw0 in enumerate(variants,1):
                raw=dict(raw0); raw['_variant_index']=int(raw.get('_variant_index',pos)); raw['_variant_label']=raw.get('_variant_label',f'方案{raw["_variant_index"]}')
                # 用当前项目规则恢复方案，仅用于确定镜头数量；不调用 AI。
                info=__import__('ad_studio.product_parser',fromlist=['ProductInfo']).ProductInfo(**self.project.product_info)
                self._activate_plan(raw,info)
                pending_shots=[s for s in self.project.shots if not s.video_path or not Path(s.video_path).exists()]
                missing=len(pending_shots)
                if any(getattr(s,'clip_source','ai_generated')!='filmed' for s in pending_shots):
                    needs_cloud_video=True
                missing_counts.append(missing)
                if footage_mode!='用户拍摄素材': estimated += missing*rate
                self._cache_active_variant()

        except Exception as exc:
            # Preflight switches variants too. If parsing/routing any candidate fails,
            # restore the user's original selection before returning an error.
            try:
                self._restore_variant_selection(original_index)
                self.detail.set('批量生成预审失败；已恢复原来选中的创意方案。')
            except Exception as restore_exc:
                messagebox.showerror('方案恢复失败',f'预审错误：{exc}\n恢复原方案时也发生错误：{restore_exc}')
            messagebox.showerror('批量生成预审失败',str(exc))
            return
        actual_cost=float(getattr(self.project,'actual_cost_rmb',0.0) or 0.0)
        remaining_budget=max(0.0,budget-actual_cost) if budget>0 else 0.0
        if budget>0 and estimated>remaining_budget:
            if not self._confirm_budget_overrun(estimated,remaining_budget,'一键生成预算超限确认'):
                self._restore_variant_selection(original_index)
                self.detail.set('已取消超预算批量生成；已恢复原来选中的创意方案。')
                return
        if needs_cloud_video and CapabilityRouter(ROOT).decide_video().target == 'cloud':
            if not self._authorize_workflow_action('cloud_generation','批量云端视频生成授权'):
                self._restore_variant_selection(original_index)
                self.detail.set('用户未授权云端生成；未调用云端服务，已恢复原来选中的创意方案。')
                return
        original=original_index; info=__import__('ad_studio.product_parser',fromlist=['ProductInfo']).ProductInfo(**self.project.product_info)
        done=[]; failed=[]; outputs=[]
        try:
            for pos,raw0 in enumerate(variants,1):
                raw=dict(raw0); raw['_variant_index']=int(raw.get('_variant_index',pos)); raw['_variant_label']=raw.get('_variant_label',f'方案{raw["_variant_index"]}')
                self._activate_plan(raw,info)
                if not self._ensure_storyboard_approval():
                    failed.append(f"方案{self.active_variant_index}：用户未批准分镜，已停止后续批量生成")
                    break
                for shot in self.project.shots:
                    if shot.video_path and Path(shot.video_path).exists():
                        continue
                    try:
                        shot.status='生成中…'; self.store.save(self.project); self.refresh_shots(); self.update_idletasks()
                        if shot.clip_source=='filmed':
                            self.store.render_footage_shot(self.project,shot)
                        else:
                            self.store.render_shot(self.project,shot,config_root=ROOT)
                        done.append(f'方案{self.active_variant_index}-镜头{shot.index}')
                    except Exception as exc:
                        failed.append(f'方案{self.active_variant_index}-镜头{shot.index}：{exc}')
                        shot.status='生成失败'
                        self.store.save(self.project)
                self._cache_active_variant()
                missing=[s for s in self.project.shots if not s.video_path or not Path(s.video_path).exists()]
                if not missing:
                    variant_label = str(raw.get('_variant_label') or f'方案{self.active_variant_index}')
                    try:
                        out=self.store.build_final(self.project,self.aspect.get(),variant_index=self.active_variant_index)
                        self._record_variant_output(out)
                        outputs.append(f'方案{self.active_variant_index}：{out}')
                    except Exception as exc:
                        # A finished-shot variant can still fail at final assembly/manifest persistence.
                        # Record this variant's failure and continue with the remaining variants.
                        failed.append(f'{variant_label}：最终成片输出失败：{exc}')
                        try:
                            self._cache_active_variant()
                        except Exception as cache_exc:
                            failed.append(f'{variant_label}：保存方案状态失败：{cache_exc}')
                        continue
            target=next((dict(v) for v in variants if int(v.get('_variant_index',0))==original),None)
            if target:
                target['_variant_index']=original; target['_variant_label']=target.get('_variant_label',f'方案{original}')
                self._activate_plan(target,info)
            self.store.save(self.project); self.refresh_shots(); self.show_shot()
            msg=f'生成镜头：{len(done)} 个\n最终成片：{len(outputs)} 个\n失败镜头：{len(failed)} 个'
            if failed: msg+='\n\n失败明细：\n'+'\n'.join(failed[:8])
            self.detail.set(msg.replace('\n','｜'))
            messagebox.showinfo('一键生成完成',msg)
        except Exception as exc:
            try:
                self._restore_variant_selection(original_index)
                self.detail.set('一键生成遇到错误；已恢复原来选中的创意方案。')
            except Exception as restore_exc:
                messagebox.showerror('方案恢复失败',str(restore_exc))
            messagebox.showerror('一键生成失败',str(exc))

    @ui_action
    def batch_final_render(self):
        """只批量输出已经完成镜头的广告版本；单个方案交付失败不影响其他方案。"""
        if not self._ui_execution_gate(): return
        if not self.project:
            return messagebox.showinfo('提示','先创建项目。')
        if not self._authorize_workflow_action('final_delivery','批量最终交付确认'): return
        set_project_workflow_mode(self.project,self._workflow_mode_value())
        variants=self.project.creative_plan.get('creative_variants',[])
        if len(variants)<=1:
            return messagebox.showinfo('提示','当前只有一个创意方案，请直接使用“生成最终成片”。')
        self._cache_active_variant()
        original_index=self.active_variant_index
        info=type('ProjectInfo',(),{'name':self.project.product_name or '商品'})()
        done=[]; skipped=[]; failed=[]
        try:
            for pos,raw0 in enumerate(variants,1):
                raw=dict(raw0)
                raw['_variant_index']=int(raw.get('_variant_index',pos))
                raw['_variant_label']=raw.get('_variant_label',f'方案{raw["_variant_index"]}')
                variant_label=f'方案{raw["_variant_index"]}'
                try:
                    self._activate_plan(raw,info)
                    variant_label=f'方案{self.active_variant_index}'
                    if not self._ensure_storyboard_approval():
                        skipped.append(f'{variant_label}：分镜未获批准')
                        self._cache_active_variant()
                        # 未获批准是明确的用户暂停信号，不再处理后续方案。
                        break
                    missing=[s.title for s in self.project.shots if not s.video_path or not Path(s.video_path).exists()]
                    if missing:
                        skipped.append(f'{variant_label}：缺少 {len(missing)} 个已生成镜头')
                        self._cache_active_variant()
                        continue
                    try:
                        out=self.store.build_final(self.project,self.aspect.get(),variant_index=self.active_variant_index)
                        self._record_variant_output(out)
                        self._cache_active_variant()
                        done.append(f'{variant_label}：{out}')
                    except Exception as exc:
                        failed.append(f'{variant_label}：最终成片输出失败：{exc}')
                        # 保留当前方案已存在的镜头和历史；失败方案不阻止后续方案。
                        try:
                            self._cache_active_variant()
                            self.store.save(self.project)
                        except Exception as save_exc:
                            failed.append(f'{variant_label}：保存失败状态时出错：{save_exc}')
                except Exception as exc:
                    failed.append(f'{variant_label}：方案处理异常：{exc}')
                    try:
                        self._cache_active_variant()
                        self.store.save(self.project)
                    except Exception as save_exc:
                        failed.append(f'{variant_label}：保存异常状态时出错：{save_exc}')
                    continue
        except Exception as e:
            failed.append(f'批量交付流程异常：{e}；已完成的输出记录已保留')
        finally:
            try:
                self._restore_variant_selection(original_index)
            except Exception as restore_exc:
                failed.append(f'恢复原方案失败：{restore_exc}')
            try:
                self.store.save(self.project)
                self.refresh_shots()
                self.show_shot()
            except Exception as save_exc:
                failed.append(f'保存/刷新交付结果失败：{save_exc}')
        summary='已输出：\n'+'\n'.join(done or ['无'])+'\n\n未输出：\n'+'\n'.join(skipped or ['无'])+'\n\n失败：\n'+'\n'.join(failed or ['无'])
        self.detail.set(f'批量版本输出结束：成功 {len(done)} 个，跳过 {len(skipped)} 个，失败 {len(failed)} 个')
        if failed:
            messagebox.showwarning('批量输出结果',summary)
        else:
            messagebox.showinfo('批量输出结果',summary)

    @ui_action
    def final_render(self):
        if not self._ui_execution_gate(): return
        if not self.project:return messagebox.showinfo('提示','先创建项目。')
        if not self._authorize_workflow_action('final_delivery','最终成片交付确认'): return
        set_project_workflow_mode(self.project,self._workflow_mode_value())
        if not self._ensure_storyboard_approval(): return
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
        set_project_workflow_mode(self.project,self._workflow_mode_value())
        self.store.save(self.project); self.detail.set(f'项目已保存：{self.project.id}')