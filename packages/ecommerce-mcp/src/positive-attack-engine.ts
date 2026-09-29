import { GameState, Action } from './game-state';

export interface PositiveStrategyCandidate {
  strategyId: string;
  strategyName: string;
  mappedAction: Action;
  score: number;
  trigger: string;
  nextObservation: string;
  opponentBranches: string[];
}

const STRATEGIES: Array<[string,string,Action,string,string]> = [
 ['P01','核心关键词重构','CHANGE_KEYWORD','搜索意图错配或点击效率偏低','曝光、CTR、CVR变化'],
 ['P02','长尾关键词切入','CHANGE_KEYWORD','核心词拥挤且存在明确长尾需求','长尾流量与转化'],
 ['P03','主图价值重构','CREATIVE_REFRESH','曝光正常但点击偏低','CTR与转化'],
 ['P04','详情页重构','DETAIL_PAGE_REFRESH','点击正常但转化偏低','CVR、退款与咨询'],
 ['P05','视频商品表达','CONTENT_VIDEO','静态素材难表达商品价值','完播、点击、转化'],
 ['P06','真实UGC沉淀','UGC_CONTENT','缺少真实使用证据','自然触达与转化'],
 ['P07','真实评价质量提升','REVIEW_QUALITY','评价信息密度不足','评价质量与转化'],
 ['P08','品牌合作','BRAND_COLLAB','目标人群高度互补','新增触达与转化'],
 ['P09','品牌授权商品','BRAND_AUTHORIZED_PRODUCT','用户重视品牌与正品保障','信任与客单'],
 ['P10','官方认证/检测','CERTIFICATION','质量疑虑影响购买','转化与售后'],
 ['P11','专业背书','EXPERT_ENDORSEMENT','购买需要专业解释','咨询与转化'],
 ['P12','场景化定位','SCENARIO_POSITIONING','人群定义过宽','场景流量质量'],
 ['P13','人群细分','AUDIENCE_SEGMENTATION','不同人群转化差异明显','各人群单位经济'],
 ['P14','套餐组合','BUNDLE_VALUE','单品高度可比','客单、毛利与转化'],
 ['P15','SKU梯度','SKU_LADDER','预算跨度大或价格带断层','SKU迁移与利润'],
 ['P16','新品迭代','PRODUCT_ITERATION','旧SKU增长边际下降','新品冷启动与复购'],
 ['P17','差异化规格','PRODUCT_DIFFERENTIATION','商品高度同质化','转化与价格敏感度'],
 ['P18','包装升级','PACKAGING_UPGRADE','包装与品牌表达不一致','复购与品牌搜索'],
 ['P19','履约速度优势','FULFILLMENT_SPEED','到货时间敏感','交付时间与转化'],
 ['P20','售后承诺','SERVICE_PROMISE','购买风险阻碍转化','转化与售后成本'],
 ['P21','客服专业化','CUSTOMER_SERVICE','咨询到成交流失高','咨询转化'],
 ['P22','内容矩阵','CONTENT_MATRIX','单一内容渠道增长有限','自然触达与转化'],
 ['P23','直播演示','LIVE_DEMO','商品需要现场演示','观看到成交'],
 ['P24','达人/创作者合作','CREATOR_COLLAB','目标人群集中于兴趣圈层','增量触达与转化'],
 ['P25','搜索内容占位','SEARCH_CONTENT','高意图问题缺少品牌内容','自然搜索进入'],
 ['P26','品牌词建设','BRAND_SEARCH','商品被记住但品牌弱','品牌搜索与复购'],
 ['P27','复购机制','REPEAT_PURCHASE','一次性成交占比高','复购率与LTV'],
 ['P28','会员体系','MEMBERSHIP','老客稳定但关系弱','留存与复购'],
 ['P29','老客新品测试','CUSTOMER_NEW_PRODUCT_TEST','新品冷启动困难','反馈与复购'],
 ['P30','跨品类协同','CROSS_CATEGORY','存在相邻需求','跨品类购买'],
 ['P31','渠道扩张','CHANNEL_EXPANSION','单平台依赖过高','新增渠道单位经济'],
 ['P32','区域突破','REGIONAL_EXPANSION','区域需求与竞争强度不同','区域单位经济'],
 ['P33','季节窗口','SEASONAL_WINDOW','需求具有周期性','窗口期增量'],
 ['P34','事件营销','EVENT_CONTENT','行业事件聚集目标人群','事件流量转化'],
 ['P35','供应链差异化','SUPPLY_CHAIN','成本或交付是核心变量','毛利与履约稳定性'],
 ['P36','独家合作','EXCLUSIVE_SUPPLY','商品容易同质化','供给差异化'],
 ['P37','成本结构优化','COST_STRUCTURE','增长但利润不增长','边际利润'],
 ['P38','价格架构','PRICE_ARCHITECTURE','单一价格覆盖不了需求','转化与客单结构'],
 ['P39','社会证明矩阵','SOCIAL_PROOF','消费者需要更多购买证据','转化与退款'],
 ['P40','组合式增长攻势','COMPOUND_GROWTH','单一优化边际递减','各变量增量贡献']
];

const mapScore=(s:GameState,id:string):number=>{
 const roi=s.roi??0, ctr=s.ctr??0, cvr=s.cvr??0;
 let score=.42;
 if(['P01','P02','P25'].includes(id)&&ctr<.03)score+=.22;
 if(['P04','P07','P10','P11','P20','P21','P39'].includes(id)&&cvr<.03)score+=.20;
 if(['P14','P15','P38'].includes(id)&&s.price>0)score+=.08;
 if(['P16','P17','P29'].includes(id)&&cvr>.02)score+=.08;
 if(['P19','P35','P36'].includes(id)&&s.competitors.some(c=>(c.price??s.price)<s.price*.95))score+=.05;
 if(['P27','P28','P30'].includes(id)&&roi>1.5)score+=.08;
 return Math.min(.9,score);
};

export function rankPositiveStrategies(state:GameState, limit=8):PositiveStrategyCandidate[]{
 return STRATEGIES.map(([id,name,action,trigger,obs])=>({
   strategyId:id,strategyName:name,mappedAction:action as Action,score:mapScore(state,id),
   trigger,nextObservation:obs,
   opponentBranches:['竞品正常跟随','无明显响应','平台/需求自然变化','未知原因']
 })).sort((a,b)=>b.score-a.score).slice(0,Math.max(1,limit));
}

export function getPositiveStrategy(id:string){return STRATEGIES.find(x=>x[0]===id)??null;}
