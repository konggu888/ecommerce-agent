"use client";
import {useMemo,useState} from "react";

const levels=["纯种草","轻广告","标准广告","强转化","极强转化"];
const forms=["真人口播","真人剧情","产品展示","真人+产品","生活场景","街头采访","情侣","夫妻","家庭","职场","开箱","测评","对比","教程","POV","UGC","直播间风格","电影感","短剧"];
const actors=[
 {name:"林川",gender:"男",age:"28岁",style:"自然、可信、生活化",source:"系统"},
 {name:"周野",gender:"男",age:"32岁",style:"成熟、专业、强转化",source:"系统"},
 {name:"苏宁",gender:"女",age:"26岁",style:"亲和、轻松、种草感",source:"系统"},
 {name:"顾瑶",gender:"女",age:"31岁",style:"高级、理性、专业",source:"系统"},
 {name:"阿杰",gender:"男",age:"24岁",style:"年轻、UGC、街头感",source:"AI生成"},
 {name:"小雨",gender:"女",age:"23岁",style:"活泼、真实、短视频感",source:"用户上传"}
];
function detect(url:string){const u=url.toLowerCase(); if(u.includes("taobao")||u.includes("tmall"))return"淘宝"; if(u.includes("jd.com"))return"京东"; if(u.includes("pinduoduo")||u.includes("yangkeduo"))return"拼多多"; if(u.includes("1688"))return"1688"; if(u.includes("douyin"))return"抖音"; return"自动识别";}
function estimate(shots:number){return +(Math.min(3,Math.ceil(shots/2))*0.72).toFixed(2)}

export default function Page(){
 const [url,setUrl]=useState(""); const [level,setLevel]=useState(2); const [form,setForm]=useState("自动选择"); const [actor,setActor]=useState(0); const [analyzed,setAnalyzed]=useState(false); const [generating,setGenerating]=useState(false); const [libraryOpen,setLibraryOpen]=useState(false); const [librarySource,setLibrarySource]=useState("全部");
 const platform=useMemo(()=>detect(url),[url]); const shots=level>=3?6:5; const cost=estimate(shots); const over=cost>3;
 function generate(){if(over){setLibraryOpen(true);return} setGenerating(true);setTimeout(()=>setGenerating(false),1200)}
 return <main>
  <header><div><span className="eyebrow">AD STUDIO / 本地算力优先</span><h1>AI 商品广告工厂</h1><p>一条商品链接，自动完成策略、演员、分镜、生成与剪辑。</p></div><div className="gpu">🟢 RTX 4050 Laptop · 本地算力已启用</div></header>
  <section className="grid">
   <div className="card hero"><h2>01 · 商品入口</h2><label>粘贴淘宝 / 京东 / 拼多多 / 1688 / 抖音商品链接</label><div className="row"><input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://..." /><button onClick={()=>setAnalyzed(true)} disabled={!url}>自动识别商品</button></div>{analyzed&&<div className="product"><b>示例商品：无线降噪耳机</b><span>平台：{platform}</span><span>类型：3C / 音频</span><span>卖点：降噪 · 长续航 · 低延迟</span><span>目标人群：18–35岁通勤 / 学生 / 游戏用户</span></div>}</div>
   <div className="card"><h2>02 · 广告力度</h2><div className="levels">{levels.map((x,i)=><button key={x} className={i===level?"selected":""} onClick={()=>setLevel(i)}><b>{i+1}</b>{x}</button>)}</div><p className="muted">系统会根据商品、受众与平台自动调整钩子、节奏和CTA。</p></div>
   <div className="card"><h2>03 · 形式与演员</h2><div className="formgrid"><button className={form==="自动选择"?"selected":""} onClick={()=>setForm("自动选择")}>✨ 自动选择</button>{forms.map(x=><button key={x} className={form===x?"selected":""} onClick={()=>setForm(x)}>{x}</button>)}</div><div className="librarybar"><span>演员库：可长期复用，生成一次后保存，下次直接调用</span><button onClick={()=>setLibraryOpen(true)}>管理演员库</button></div><div className="actors">{actors.map((a,i)=><button key={a.name} className={actor===i?"actor selected":"actor"} onClick={()=>setActor(i)}><div className="avatar">{a.gender}</div><div><b>{a.name}</b><small>{a.age} · {a.style}</small><em>{a.source}</em></div></button>)}</div></div>
   <div className="card"><h2>04 · AI策略与分镜</h2><div className="strategy"><div className="recommended"><b>推荐策略</b><strong>{level>=3?"痛点 → 证明 → 对比 → 转化":"真实体验 → 产品卖点 → 轻CTA"}</strong><span>自动选择：{form==="自动选择"?"真人+产品":form} · {actors[actor].name}</span></div>{Array.from({length:shots},(_,i)=><div className="shot" key={i}><span>镜头 {i+1}</span><div><b>{["3秒钩子：直接抛出用户痛点","产品特写：展示核心功能","真人使用：自然场景体验","卖点证明：前后对比/细节","用户反应：强化可信度","结尾CTA：明确行动"][i]}</b><small>素材：优先调用本地资产库 · 关键新镜头才调用云端AI · 后期本地4050</small></div></div>)}</div></div>
   <div className="card cost"><h2>05 · 成本控制</h2><div className="costline"><span>本地计算</span><b>¥0.00</b></div><div className="costline"><span>关键AI镜头（估算）</span><b>¥{cost.toFixed(2)}</b></div><div className="costline total"><span>预计总成本</span><b>¥{cost.toFixed(2)}</b></div><div className={over?"warning":"safe"}>{over?"⚠️ 已超过 ¥3.00：不会自动降画质/换模型，必须由你确认。":"✓ 在 ¥3.00 预算内：优先把预算用于关键视频镜头。"}</div><button className="generate" onClick={generate}>{generating?"正在生成…":"生成广告"}</button></div>
  </section>
  {libraryOpen&&<div className="modalBackdrop" onClick={()=>setLibraryOpen(false)}><div className="modal" onClick={e=>e.stopPropagation()}><div className="modalHead"><div><h2>演员与素材资产库</h2><p>一次生成，长期保存；后续广告优先复用，不重复消耗生成Token。</p></div><button onClick={()=>setLibraryOpen(false)}>关闭</button></div><div className="libraryActions"><button onClick={()=>setLibrarySource("全部")} className={librarySource==="全部"?"selected":""}>全部</button><button onClick={()=>setLibrarySource("系统")} className={librarySource==="系统"?"selected":""}>系统</button><button onClick={()=>setLibrarySource("用户上传")} className={librarySource==="用户上传"?"selected":""}>用户上传</button><button onClick={()=>setLibrarySource("AI生成")} className={librarySource==="AI生成"?"selected":""}>AI生成</button><button>＋上传演员</button><button>✨ AI生成演员</button></div><div className="libraryGrid">{actors.filter(a=>librarySource==="全部"||a.source===librarySource).map(a=><div className="libraryActor" key={a.name}><div className="avatar big">{a.gender}</div><div><b>{a.name}</b><span>{a.age} · {a.style}</span><small>来源：{a.source} · 可长期复用</small></div></div>)}</div><div className="libraryNote">资产库设计为独立持久化层：演员、场景、产品素材都可以保存 metadata、预览图和原始资产地址。以后换电脑或部署版本，也不需要重新生成演员。</div></div></div>}
  <footer>本版本采用“本地资产复用优先”原则：演员/场景生成一次后进入长期资产库；只有缺少的关键素材才调用云端生成。</footer>
 </main>
}