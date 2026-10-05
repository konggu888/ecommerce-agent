import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from .library import LocalLibrary
from .engine import FORMS, new_project, mark_regenerate
from .engine import estimate_cost
from .gpu import detect_gpu
from .production import ProductionStore

ROOT=Path(__file__).resolve().parents[1]/'data'/'ad-studio'
PROJECTS=ROOT/'projects'

class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title('AI 商品广告工厂 · 本地版'); self.geometry('1180x760'); self.minsize(980,650)
        self.lib=LocalLibrary(ROOT); self.store=ProductionStore(PROJECTS); self.project=None; self.ui(); self.refresh_assets(); self.refresh_gpu()
    def ui(self):
        top=ttk.Frame(self,padding=16); top.pack(fill='x')
        ttk.Label(top,text='AI 商品广告工厂',font=('Microsoft YaHei UI',22,'bold')).pack(side='left')
        self.gpu_text=tk.StringVar(value='检测本地 GPU…'); ttk.Label(top,textvariable=self.gpu_text).pack(side='right')
        setup=ttk.LabelFrame(self,text='① 商品与广告策略',padding=12); setup.pack(fill='x',padx=16,pady=8)
        ttk.Label(setup,text='商品链接').grid(row=0,column=0,sticky='w'); self.url=tk.StringVar(); ttk.Entry(setup,textvariable=self.url,width=72).grid(row=0,column=1,columnspan=3,sticky='ew',padx=8)
        ttk.Label(setup,text='广告强度').grid(row=1,column=0,sticky='w'); self.level=tk.IntVar(value=2); ttk.Combobox(setup,textvariable=self.level,values=[1,2,3,4,5],state='readonly',width=8).grid(row=1,column=1,sticky='w')
        ttk.Label(setup,text='1纯种草  2轻广告  3标准广告  4强转化  5极强转化').grid(row=1,column=2,columnspan=2,sticky='w')
        ttk.Label(setup,text='视频形式').grid(row=2,column=0,sticky='w'); self.form=tk.StringVar(value=FORMS[0]); ttk.Combobox(setup,textvariable=self.form,values=FORMS,state='readonly',width=22).grid(row=2,column=1,sticky='w')
        ttk.Button(setup,text='创建广告项目',command=self.create).grid(row=2,column=3,sticky='e')
        main=ttk.Panedwindow(self,orient='horizontal'); main.pack(fill='both',expand=True,padx=16,pady=8)
        left=ttk.Frame(main,padding=8); right=ttk.Frame(main,padding=8); main.add(left,weight=3); main.add(right,weight=2)
        ttk.Label(left,text='② 分镜生产链',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.shots=ttk.Treeview(left,columns=('v','status','actor','scene'),show='tree headings',height=17)
        for c,t,w in [('v','版本',70),('status','状态',90),('actor','演员',150),('scene','场景',150)]: self.shots.heading(c,text=t); self.shots.column(c,width=w)
        self.shots.column('#0',width=300); self.shots.pack(fill='both',expand=True,pady=8); self.shots.bind('<<TreeviewSelect>>',self.show_shot)
        bar=ttk.Frame(left); bar.pack(fill='x'); ttk.Button(bar,text='生成本镜头',command=self.generate_shot).pack(side='left'); ttk.Button(bar,text='重新生成本镜头',command=self.regen_shot).pack(side='left',padx=8); ttk.Button(bar,text='生成最终成片',command=self.final_render).pack(side='right',padx=8)
        ttk.Button(bar,text='保存项目',command=self.save).pack(side='right')
        ttk.Label(right,text='③ 本地资产库',font=('Microsoft YaHei UI',14,'bold')).pack(anchor='w')
        self.assets=ttk.Treeview(right,columns=('kind','source','path'),show='tree headings',height=13)
        for c,t,w in [('kind','类型',80),('source','来源',90),('path','本地文件',300)]: self.assets.heading(c,text=t); self.assets.column(c,width=w)
        self.assets.column('#0',width=180); self.assets.pack(fill='both',expand=True,pady=8)
        ab=ttk.Frame(right); ab.pack(fill='x'); ttk.Button(ab,text='＋上传演员',command=lambda:self.upload('演员')).pack(side='left'); ttk.Button(ab,text='＋上传场景',command=lambda:self.upload('场景')).pack(side='left',padx=5); ttk.Button(ab,text='＋上传产品素材',command=lambda:self.upload('产品图')).pack(side='left'); ttk.Button(ab,text='刷新资产库',command=self.refresh_assets).pack(side='right')
        self.detail=tk.StringVar(value='等待创建项目'); ttk.Label(right,textvariable=self.detail,justify='left',wraplength=470).pack(fill='x',pady=10)
        self.cost=tk.StringVar(value='成本：尚未计算'); ttk.Label(right,textvariable=self.cost,font=('Microsoft YaHei UI',12,'bold')).pack(anchor='w')
        ttk.Label(self,text='本地存储：本机磁盘  |  资产库：永久复用  |  云端生成：仅在需要时调用',relief='sunken',anchor='w',padding=8).pack(fill='x',side='bottom')
    def refresh_gpu(self):
        g=detect_gpu(); self.gpu_text.set(('🟢 '+g.get('name','NVIDIA')+' · '+g.get('mode','CPU')) if g.get('available') else '⚪ 未检测到 NVIDIA GPU · CPU模式')
    def create(self):
        self.project=new_project(self.url.get(),self.level.get(),self.form.get()); self.refresh_shots(); c=estimate(len(self.project.shots)); self.cost.set(f"预计成本 ¥{c['总计']:.2f} / 预算 ¥{c['预算']:.2f}"); self.detail.set('项目已创建：商品解析 → 策略 → 分镜 → 单镜头生成 → 本地合成。');
        if c['超预算']: messagebox.showwarning('预算拦截','预计超过 ¥3，生产尚未开始。必须确认后才能继续。')
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
            out=self.store.render_placeholder_shot(self.project,s)
            self.refresh_shots()
            self.detail.set(f'镜头 {s.index} 已生成 v{s.version}。本地FFmpeg输出：{out}')
        except Exception as e:
            s.status='生成失败'
            self.store.save(self.project)
            messagebox.showerror('镜头生成失败',str(e))
    def regen_shot(self):
        s=self.selected()
        if not s:return messagebox.showinfo('提示','先选择要重新生成的镜头。')
        old=s.version; mark_regenerate(self.project,self.project.shots.index(s)); self.refresh_shots(); self.detail.set(f'镜头 {s.index}：v{old} → v{s.version}。其他镜头版本保持不变。')
    def upload(self,kind):
        p=filedialog.askopenfilename(title=f'选择{kind}文件')
        if p:self.lib.add_file(p,Path(p).stem,kind); self.refresh_assets()
    def refresh_assets(self):
        for x in self.assets.get_children(): self.assets.delete(x)
        for a in self.lib.all(): self.assets.insert('', 'end',text=a.name,values=(a.kind,a.source,a.path or ''))
    def final_render(self):
        if not self.project:return messagebox.showinfo('提示','先创建项目。')
        try:\n            out=self.store.build_final(self.project)\n            self.detail.set(f'最终成片已输出：{out}')
            messagebox.showinfo('完成',f'最终广告已生成\\n{out}')
        except Exception as e:
            messagebox.showerror('暂不能成片',str(e))
\n    def save(self):
        if self.project:self.store.save(self.project); self.detail.set(f'项目已保存到本机：{PROJECTS/self.project.id}.json')

if __name__=='__main__': App().mainloop()
