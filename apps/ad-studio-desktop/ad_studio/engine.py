from .models import Project, Shot, uid
import re

FORMS=['真人口播','真人剧情','产品展示','真人+产品','生活场景','街头采访','情侣','夫妻','家庭','职场','开箱','测评','对比','教程','POV','UGC','直播间风格','电影感','短剧']

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

def estimate_cost(shots):
    cloud=max(1,min(3,(shots+1)//2)); return {'本地':0.0,'云端':round(cloud*0.72,2),'总计':round(cloud*0.72,2),'预算':3.0,'超预算':cloud*0.72>3}
