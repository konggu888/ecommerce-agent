export type Platform="淘宝"|"京东"|"拼多多"|"1688"|"抖音"|"自动识别";
export type LocalTask="商品解析"|"策略分析"|"文案剧本"|"字幕"|"剪辑合成"|"视频编码";
export type CloudTask="人物生成"|"场景生成"|"关键视频镜头"|"高质量配音";
export type HardwareProfile={gpu:string;vramGb:number;localVideoProcessing:boolean;localSmallModel:boolean};
export type CostEstimate={local:number;cloud:number;total:number;budget:number;overBudget:boolean};
export const DEFAULT_HARDWARE:HardwareProfile={gpu:"RTX 4050 Laptop",vramGb:6,localVideoProcessing:true,localSmallModel:true};