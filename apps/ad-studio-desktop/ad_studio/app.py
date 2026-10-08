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
        audit=plan.get('variant_set_audit') or {}
        audit_note=f"创意实验设计：{audit.get('design_status','未审计')}｜机制差异度 {audit.get('mechanism_score','-')}｜设计分 {audit.get('test_design_score','-')}"
        ttk.Label(frm,text=data_note,wraplength=1120,foreground='#555').pack(anchor='w',pady=(4,4))
        ttk.Label(frm,text=audit_note,wraplength=1120,foreground='#555').pack(anchor='w',pady=(0,4))
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
        detail.insert('end','\n\n【实验设计审计】\n')
        for pair in (audit.get('pairs') or []):
            detail.insert('end',f"• 方案{pair.get('a')} ↔ 方案{pair.get('b')}：{pair.get('test_quality','未判断')}｜核心机制差异：{','.join(pair.get('mechanism_differences') or []) or '无'}\n")
        detail.insert('end','\n【下一轮创意测试建议】\n')
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