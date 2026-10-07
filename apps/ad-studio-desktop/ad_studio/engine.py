from .models import Project, Shot, uid
from .asset_generation import AssetGenerator
import re

FORMS=['真人口播','真人剧情','产品展示','真人+产品','生活场景','街头采访','情侣','夫妻','家庭','职场','开箱','测评','对比','教程','POV','UGC','直播间风格','电影感','短剧']

# Provider pricing is deliberately centralized so real provider/model prices can be
# plugged in later without changing the desktop workflow.
DEFAULT_RATES = {
    'cloud_video_per_shot': 0.72,
    'cloud_image_per_asset': 0.00,
    'cloud_voice_per_shot': 0.00,
    'cloud_other': 0.00,
    'local_processing': 0.00,
}

def detect_platform(url):
    u=(url or '').lower()
    for key,name in [('taobao','淘宝'),('tmall','淘宝'),('jd.com','京东'),('pinduoduo','拼多多'),('yangkeduo','拼多多'),('1688.com','1688'),('douyin','抖音')]:
        if key in u:return name
    return '自动识别'

def product_name(url):
    m=re.search(r'(?:item|goods|product)[=/]([A-Za-z0-9_-]{3,})',url or '')
    return '待解析商品' if not m else f'商品-{m.group(1)[:12]}'

def build_shots(level,form,actor_id=None,scene_id=None,product_ids=None):
    titles=['3秒钩子：直接抛出用户痛点','产品特写：展示核心卖点','真人使用：自然场景体验','卖点证明：细节/对比/结果','用户反应：强化可信度','结尾CTA：明确行动']
    n=6 if level>=3 else 5
    return [Shot(uid('shot'),i+1,titles[i],f'{form}画面：等待素材生成',f'围绕{form}完成第{i+1}镜头文案',actor_id,scene_id,product_ids or []) for i in range(n)]

def new_project(url,level,form):
    return Project(uid('project'),product_name(url),detect_platform(url),form,level,None,None,build_shots(level,form))

def mark_regenerate(project,index):
    s=project.shots[index]
    s.version+=1; s.status='需重生成'; s.video_path=None
    return s


def estimate_asset_generation(library, root, creative_shots):
    """预估缺失资产费用；同一组需求跨多个镜头只计一次。绝不触发实际生成。"""
    generator=AssetGenerator(root/'asset-generation.json',root)
    rows=[]; total=0.0; seen=set()
    for shot in creative_shots:
        req=shot.get('asset_resolution',{}) or {}
        for kind,key in (('演员','actor_tags'),('场景','scene_tags'),('商品素材','product_tags')):
            tags=tuple(sorted({str(x).strip() for x in (req.get(key,[]) or []) if str(x).strip()}))
            if not tags or not req.get('generation_if_missing',True):
                continue
            found=library.best_match(kind,list(tags))
            if found:
                continue
            identity=(kind,tags)
            if identity in seen:
                continue
            seen.add(identity)
            price=float(generator.price(kind))
            rows.append({'镜头':shot.get('index'),'类型':kind,'标签':list(tags),'状态':'需要自动生成','单价':price,'小计':round(price,2)})
            total += price
    return {
        '数量':len(rows),
        '总计':round(total,2),
        '明细':rows,
        '已配置':any(generator.configured(k) for k in ('演员','场景','商品素材'))
    }
def estimate_cost(shots, rates=None):
    """Return a preflight estimate with an auditable line-item breakdown.

    The default rate table is a placeholder provider price table, not a claim
    about any particular vendor. Passing rates lets the real provider adapter
    supply current prices later.
    """
    r=dict(DEFAULT_RATES)
    if rates:
        r.update(rates)
    count=max(1,int(shots))
    items=[
        {'项目':'云端视频生成','数量':count,'单价':round(float(r['cloud_video_per_shot']),4),
         '小计':round(count*float(r['cloud_video_per_shot']),2),'计费方式':'按计划镜头'},
        {'项目':'云端图片/资产生成','数量':0,'单价':round(float(r['cloud_image_per_asset']),4),
         '小计':0.0,'计费方式':'按新增资产'},
        {'项目':'云端配音','数量':0,'单价':round(float(r['cloud_voice_per_shot']),4),
         '小计':0.0,'计费方式':'按镜头'},
        {'项目':'其他云端任务','数量':0,'单价':round(float(r['cloud_other']),4),
         '小计':0.0,'计费方式':'按实际调用'},
        {'项目':'本地4050处理/FFmpeg','数量':1,'单价':round(float(r['local_processing']),4),
         '小计':round(float(r['local_processing']),2),'计费方式':'本地'},
    ]
    cloud=round(sum(x['小计'] for x in items if x['项目']!='本地4050处理/FFmpeg'),2)
    local=round(next(x['小计'] for x in items if x['项目']=='本地4050处理/FFmpeg'),2)
    total=round(local+cloud,2)
    return {
        '本地':local,'云端':cloud,'总计':total,'预算':3.0,'超预算':total>3,
        '明细':items,'计价说明':'云端价格来自当前配置；默认 ¥0.72/计划视频镜头仅为占位价，不代表固定供应商报价。'
    }
