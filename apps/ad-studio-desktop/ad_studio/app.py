from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil
import subprocess
from .library import LocalLibrary
from .engine import FORMS, new_project, mark_regenerate, estimate_cost
from .gpu import detect_gpu
from .production import ProductionStore
from .product_parser import parse_product_url, save_product
from .creative_engine import CreativeEngine
from .model_router import ModelRouter, ModelProfile, FUNCTIONS
from .browser_skill import _find_agent_browser
from .ffmpeg import available as ffmpeg_available, has_nvenc


class UnconfiguredCreativeLLM:
    def create_plan(self, product, constraints):
        raise RuntimeError(
            "尚未配置创意大模型。请在设置中接入 GPT、Claude、Gemini、国内模型或本地模型后再生成广告策略。"
        )


ROOT=Path(__file__).resolve().parents[1]/'data'/'ad-studio'
PROJECTS=ROOT/'projects'


class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title('AI 商品广告工厂 · 本地版'); self.geometry('1180x760'); self.minsize(980,650)
        self.lib=LocalLibrary(ROOT); self.lib.ensure_defaults(); self.store=ProductionStore(PROJECTS); self.project=None
        self.model_router=ModelRouter(ROOT/'model-config.json')
        self.creative_engine=CreativeEngine(self.model_router)
        self.ui(); self.refresh_assets(); self.refresh_gpu()

    def ui(self):
        top=ttk.Frame(self,padding=16); top.pack(fill='x')
        ttk.Label(top,text='AI 商品广告工厂',font=('Microsoft YaHei UI',22,'bold')).pack(side='left')
        self.gpu_text=tk.StringVar(value='检测本地 GPU…'); ttk.Label(top,textvariable=self.gpu_text).pack(side='right')
        setup=ttk.LabelFrame(self,text='① 商品与广告策略',padding=12); setup.pack(fill='x',padx=16,pady=8)
        ttk.Label(setup,text='商品链接').grid(row=0,column=0,sticky='w'); self.url=tk.StringVar(); ttk.Entry(setup,textvariable=self.url,width=72).grid(row=0,column=1,columnspan=3,sticky='ew',padx=8)
        ttk.Label(setup,text='广告强度').grid(row=1,column=0,sticky='w'); self.level=tk.IntVar(value=2); ttk.Combobox(setup,textvariable=self.level,values=[1,2,3,4,5],state='readonly',width=8).grid(row=1,column=1,sticky='w')
        ttk.Label(setup,text='留空/自动：交给AI判断；手动选择仅作为约束').grid(row=1,column=2,columnspan=2,sticky='w')
        ttk.Label(setup,text='视频形式').grid(row=2,column=0,sticky='w'); self.form=tk.StringVar(value='AI自动选择'); ttk.Combobox(setup,textvariable=self.form,values=['AI自动选择']+FORMS,state='readonly',width=22).grid(row=2,column=1,sticky='w')
        ttk.Button(setup,text='创建广告项目',command=self.create).grid(row=2,column=3,sticky='e'); ttk.Button(setup,text='打开已有项目',command=self.load_project).grid(row=2,column=2,sticky='e',padx=8); ttk.Button(setup,text='⚙ 模型设置',command=self.model_settings).grid(row=0,column=3,sticky='e'); ttk.Button(setup,text='🔎 系统状态',command=self.system_status).grid(row=1,column=3,sticky='e')
        main=ttk.Panedwindow(self,orient='horizontal'); main.pack(fill='both',expand=True,padx=16,pady=8)
        left=ttk.Frame(main,padding=8); right=ttk.Frame(main,padding=8); main.add(left,weight=3); main.add(right,weight=2)
        ttk.Label(left,text='② 分镜生产链',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.shots=ttk.Treeview(left,columns=('v','status','actor','scene'),show='tree headings',height=17)
        for c,t,w in [('v','版本',70),('status','状态',90),('actor','演员',150),('scene','场景',150)]: self.shots.heading(c,text=t); self.shots.column(c,width=w)
        self.shots.column('#0',width=300); self.shots.pack(fill='both',expand=True,pady=8); self.shots.bind('<<TreeviewSelect>>',self.show_shot)
        bar=ttk.Frame(left); bar.pack(fill='x'); ttk.Button(bar,text='生成本镜头',command=self.generate_shot).pack(side='left'); ttk.Button(bar,text='重新生成本镜头',command=self.regen_shot).pack(side='left',padx=8); ttk.Button(bar,text='生成最终成片',command=self.final_render).pack(side='right',padx=8); ttk.Button(bar,text='保存项目',command=self.save).pack(side='right')
        ttk.Label(right,text='③ 本地资产库',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.assets=ttk.Treeview(right,columns=('kind','source','path'),show='tree headings',height=13)
        for c,t,w in [('kind','类型',80),('source','来源',90),('path','本地文件',300)]: self.assets.heading(c,text=t); self.assets.column(c,width=w)
        self.assets.column('#0',width=180); self.assets.pack(fill='both',expand=True,pady=8)
        ab=ttk.Frame(right); ab.pack(fill='x'); ttk.Button(ab,text='＋上传演员',command=lambda:self.upload('演员')).pack(side='left'); ttk.Button(ab,text='＋上传场景',command=lambda:self.upload('场景')).pack(side='left',padx=5); ttk.Button(ab,text='＋上传产品素材',command=lambda:self.upload('产品图')).pack(side='left'); ttk.Button(ab,text='刷新资产库',command=self.refresh_assets).pack(side='right')
        self.detail=tk.StringVar(value='等待创建项目'); ttk.Label(right,textvariable=self.detail,justify='left',wraplength=470).pack(fill='x',pady=10); ttk.Button(right,text='编辑当前分镜',command=self.edit_shot).pack(anchor='w',pady=4)
        self.cost=tk.StringVar(value='成本：尚未计算'); ttk.Label(right,textvariable=self.cost,font=('Microsoft YaHei UI',12,'bold')).pack(anchor='w')
        ttk.Label(self,text='本地存储：本机磁盘  |  资产库：永久复用  |  云端生成：仅在需要时调用',relief='sunken',anchor='w',padding=8).pack(fill='x',side='bottom')



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
        add('本地硬件','NVIDIA GPU',gpu.get('available'),f"{gpu.get('name','未检测到')} · {gpu.get('vram_mb','?')}MB · {gpu.get('mode','CPU')}")
        ff=ffmpeg_available(); nv=has_nvenc() if ff else False
        add('本地后处理','FFmpeg',ff,'ffmpeg + ffprobe 已找到' if ff else '未找到 ffmpeg/ffprobe，请安装并加入 PATH')
        add('本地后处理','NVENC 硬件编码',nv,'h264_nvenc 可用' if nv else '不可用，将退回 CPU 编码',warn=ff and not nv)
        profiles=self.model_router.profiles(); enabled=[p for p in profiles if p.enabled]
        keyed=[p for p in enabled if p.api_key or p.provider == 'local_openai']
        default=self.model_router.get(self.model_router.data['default_model'])
        add('AI创意引擎','模型池',bool(enabled),f'{len(enabled)} 个启用模型；默认：{default.name}')
        add('AI创意引擎','模型调用凭据',bool(keyed),f'{len(keyed)} 个模型可实际调用' if keyed else '没有可实际调用的模型，请配置 API Key 或本地模型')
        routed=sum(1 for fn in FUNCTIONS if self.model_router.route(fn).enabled)
        add('AI创意引擎','9项功能独立路由',routed==len(FUNCTIONS),f'{routed}/{len(FUNCTIONS)} 个功能有启用模型')
        for fn in FUNCTIONS:
            p=self.model_router.route(fn); ready=p.enabled and (bool(p.api_key) or p.provider == 'local_openai')
            add('模型路由',fn,ready,f'→ {p.name} / {p.model}',warn=p.enabled and not ready)
        browser=_find_agent_browser()
        add('商品采集','浏览器回退采集',bool(browser),browser or '未检测到 agent-browser；直接HTTP失败时无法使用浏览器回退')
        forbidden=ROOT/'forbidden_terms.txt'
        add('合规','禁止词库',forbidden.exists(),str(forbidden) if forbidden.exists() else '未创建 forbidden_terms.txt')
        add('资产库','本地永久资产库',self.lib.root.exists(),f'{self.lib.root} · {len(self.lib.all())} 个资产')
        add('生产链','镜头生成',False,'当前仍是 FFmpeg 占位镜头；真正的视频生成 Provider 尚未接入',warn=True)
        add('生产链','最终成片拼接',ff,'本地 FFmpeg concat 可用' if ff else '等待 FFmpeg')
        add('云端生成','人物/场景/关键视频镜头',False,'云端生成 Adapter 尚未接入，不会偷偷产生云端费用',warn=True)
        add('云端生成','高质量配音',False,'语音 Provider 尚未接入',warn=True)
        ttk.Label(frm,text='🟢 可直接使用   🟡 有框架但尚未完全接通   🔴 当前不可用',font=('Microsoft YaHei UI',10,'bold')).pack(anchor='w',pady=(10,4))
        btn=ttk.Frame(frm); btn.pack(fill='x')
        ttk.Button(btn,text='重新检测',command=lambda:(win.destroy(),self.system_status())).pack(side='right')
        ttk.Button(btn,text='打开模型设置',command=self.model_settings).pack(side='right',padx=8)

    def model_settings(self):
        win=tk.Toplevel(self); win.title('AI 模型池与功能路由'); win.geometry('820x680'); win.transient(self)
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        ttk.Label(frm,text='多模型池',font=('Microsoft YaHei UI',16,'bold')).pack(anchor='w')
        ttk.Label(frm,text='默认 GPT；不同功能可以分别指定不同模型。API Key 只保存在本机。').pack(anchor='w',pady=(2,10))

        profiles=self.model_router.profiles()
        selected=tk.StringVar(value=profiles[0].id if profiles else '')
        ttk.Label(frm,text='模型').pack(anchor='w')
        model_box=ttk.Combobox(frm,textvariable=selected,values=[p.id for p in profiles],state='readonly')
        model_box.pack(fill='x',pady=4)

        fields=ttk.Frame(frm); fields.pack(fill='x',pady=4)
        name=tk.StringVar(); provider=tk.StringVar(value='openai_compatible'); base=tk.StringVar(); model=tk.StringVar(); key=tk.StringVar()
        for row,label,var in [(0,'名称',name),(1,'提供方式',provider),(2,'Base URL',base),(3,'模型 ID',model),(4,'API Key',key)]:
            ttk.Label(fields,text=label,width=12).grid(row=row,column=0,sticky='w',pady=3)
            ttk.Entry(fields,textvariable=var,show='*' if label=='API Key' else '').grid(row=row,column=1,sticky='ew',padx=8,pady=3)
        fields.columnconfigure(1,weight=1)

        def load_profile(_=None):
            try:p=self.model_router.get(selected.get())
            except Exception:return
            name.set(p.name); provider.set(p.provider); base.set(p.base_url); model.set(p.model); key.set(p.api_key)

        def save_profile():
            mid=selected.get() or f'model-{len(self.model_router.profiles())+1}'
            p=ModelProfile(mid,name.get().strip() or mid,provider.get().strip() or 'openai_compatible',base.get().strip(),model.get().strip(),key.get().strip())
            self.model_router.add_or_update(p); self.model_router.set_default(mid)
            selected.set(mid); model_box['values']=[x.id for x in self.model_router.profiles()]
            messagebox.showinfo('已保存','模型已加入本机模型池，并设为默认模型。')

        def new_profile():
            mid=f'model-{len(self.model_router.profiles())+1}'
            p=ModelProfile(mid,f'模型 {len(self.model_router.profiles())+1}')
            self.model_router.add_or_update(p); selected.set(mid); model_box['values']=[x.id for x in self.model_router.profiles()]; load_profile()

        model_box.bind('<<ComboboxSelected>>',load_profile); load_profile()
        btn=ttk.Frame(frm); btn.pack(fill='x',pady=8)
        ttk.Button(btn,text='＋新增模型',command=new_profile).pack(side='left'); ttk.Button(btn,text='保存模型并设为默认',command=save_profile).pack(side='left',padx=8)

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

    def refresh_gpu(self):
        g=detect_gpu(); self.gpu_text.set(('🟢 '+g.get('name','NVIDIA')+' · '+g.get('mode','CPU')) if g.get('available') else '⚪ 未检测到 NVIDIA GPU · CPU模式')

    def _show_cost_breakdown(self,c):
        lines=[f"项目预估：¥{c['总计']:.2f}",f"本地4050/FFmpeg：¥{c['本地']:.2f}",f"云端任务：¥{c['云端']:.2f}"]
        for item in c.get('明细',[]):
            if item['数量']: lines.append(f"  {item['项目']}：{item['数量']} × ¥{item['单价']:.2f} = ¥{item['小计']:.2f}")
        self.cost.set(' | '.join(lines))

    def _creative_constraints(self):
        return {
            'platform': self.project.platform if self.project else '自动识别',
            'ad_level': self.level.get(),
            'video_form': self.form.get(),
            'allowed_video_forms': FORMS,
            'reusable_actors': [a.__dict__ for a in self.lib.reusable('演员')],
            'reusable_scenes': [a.__dict__ for a in self.lib.reusable('场景')],
            'reusable_product_assets': [a.__dict__ for a in self.lib.reusable('产品图')],
            'forbidden_terms_file': str(ROOT/'forbidden_terms.txt'),
        }

    def create(self):
        url=self.url.get().strip()
        if not url:return messagebox.showinfo('提示','请先输入商品链接。')
        level=self.level.get(); form=self.form.get()
        info=parse_product_url(url)
        if not info.fetched and info.error:
            if not messagebox.askyesno('商品解析未完成',f'当前无法直接读取商品页面。\n\n原因：{info.error}\n\n仍可创建项目，稍后可手动补充商品信息。是否继续？'):
                return
        self.detail.set(f'商品资料采集：{info.name} · {info.platform}\n来源：{info.source or "未完成"}\n{info.description[:180] or "未读取到商品描述"}')
        self.project=new_project(url,level,form if form!='AI自动选择' else 'AI自动选择')
        self.project.product_info=info.to_dict()
        try:
            constraints=self._creative_constraints()
            plan=self.creative_engine.plan(info.to_dict(),constraints)
        except Exception as e:
            self.project=None
            messagebox.showerror('创意引擎未配置',str(e))
            return

        self.project.form=plan.video_form
        self.project.product_name=info.name
        self.project.shots=[
            __import__('ad_studio.models',fromlist=['Shot']).Shot(
                id=f'shot-{x.index:02d}', index=x.index,
                title=x.objective or f'镜头{x.index}',
                visual=x.visual, script=x.dialogue,
            ) for x in plan.shots
        ]
        c=estimate_cost(len(plan.shots)); self.project.cost_estimate=c; self._show_cost_breakdown(c)
        detail='\n'.join([
            f"商品：{info.name}",f"平台：{info.platform}",f"AI判断广告强度：{plan.ad_level}",
            f"AI选择视频形式：{plan.video_form}",f"预计时长：{plan.duration_seconds}秒",
            f"AI策略：{plan.strategy}",f"AI钩子：{plan.hook}",'',
            f"开始项目前预计成本：¥{c['总计']:.2f}",f"本地4050/FFmpeg：¥{c['本地']:.2f}",f"云端任务：¥{c['云端']:.2f}",
            *[f"{x['项目']}：{x['数量']} × ¥{x['单价']:.2f} = ¥{x['小计']:.2f}" for x in c['明细'] if x['数量']],
            '',f"预算线：¥{c['预算']:.2f}",c['计价说明'],'','超过预算不会自动降质、换模型或减少镜头。是否现在开始？'
        ])
        if not messagebox.askyesno('AI创意与项目预算确认',detail):
            self.project=None; self.detail.set('已取消项目创建，尚未产生生成费用。'); return
        self.store.save(self.project); save_product(info,ROOT,self.project.id); self.refresh_shots()
        self.detail.set(f'AI创意方案已确认：{info.name} → {plan.video_form} → {len(plan.shots)}镜头 → 等待生成。')

    def refresh_shots(self):
        for x in self.shots.get_children(): self.shots.delete(x)
        if self.project:
            for s in self.project.shots: self.shots.insert('', 'end',iid=s.id,text=f'{s.index:02d}  {s.title}',values=(f'v{s.version}',s.status,s.actor_id or '自动匹配',s.scene_id or '自动匹配'))

    def selected(self):
        sel=self.shots.selection(); return next((x for x in self.project.shots if x.id==sel[0]),None) if self.project and sel else None

    def show_shot(self,_=None):
        s=self.selected()
        if s:self.detail.set(f'镜头 {s.index}\n{s.title}\n\n画面：{s.visual}\n\n文案：{s.script}\n\n版本：v{s.version}  状态：{s.status}')

    def generate_shot(self):
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择一个镜头。')
        try:
            out=self.store.render_placeholder_shot(self.project,s); self.refresh_shots(); self.detail.set(f'镜头 {s.index} 已生成 v{s.version}。本地FFmpeg输出：{out}')
        except Exception as e:
            s.status='生成失败'; self.store.save(self.project); messagebox.showerror('镜头生成失败',str(e))

    def regen_shot(self):
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择要重新生成的镜头。')
        old=s.version; mark_regenerate(self.project,self.project.shots.index(s)); self.store.save(self.project); self.refresh_shots(); self.detail.set(f'镜头 {s.index}：v{old} → v{s.version}。其他镜头版本保持不变。')

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
            self.project=project; self.url.set(''); self.level.set(project.level); self.form.set(project.form); self.refresh_shots(); c=project.cost_estimate; self.cost.set(f"项目预估 ¥{c.get('总计',0):.2f} · 云端 ¥{c.get('云端',0):.2f} · 已保存 {len(project.shots)} 个镜头" if c else f'已保存 {len(project.shots)} 个镜头'); self.detail.set(f'已恢复项目：{project.product_name} · {project.platform} · {project.form}'); win.destroy()
        ttk.Button(frm,text='打开',command=open_selected).pack(anchor='e')

    def upload(self,kind):
        p=filedialog.askopenfilename(title=f'选择{kind}文件')
        if p:self.lib.add_file(p,Path(p).stem,kind); self.refresh_assets()

    def refresh_assets(self):
        for x in self.assets.get_children(): self.assets.delete(x)
        for a in self.lib.all(): self.assets.insert('', 'end',text=a.name,values=(a.kind,a.source,a.path or ''))

    def final_render(self):
        if not self.project:return messagebox.showinfo('提示','先创建项目。')
        try:
            out=self.store.build_final(self.project); self.detail.set(f'最终成片已输出：{out}'); messagebox.showinfo('完成',f'最终广告已生成\n{out}')
        except Exception as e: messagebox.showerror('暂不能成片',str(e))

    def save(self):
        if not self.project:return messagebox.showinfo('提示','当前没有项目可保存。')
        self.store.save(self.project); self.detail.set(f'项目已保存：{self.project.id}')
