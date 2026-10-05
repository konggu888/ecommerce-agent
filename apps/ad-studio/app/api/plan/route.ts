import {NextResponse} from "next/server";
import {detectPlatform,estimateCost,localPlan} from "@/lib/engine";
import {DEFAULT_HARDWARE} from "@/lib/types";
export async function POST(req:Request){const body=await req.json().catch(()=>({}));const url=String(body.url||"");const level=Number(body.level??2);const shots=level>=3?6:5;const cost=estimateCost(shots);return NextResponse.json({platform:detectPlatform(url),product:{name:"无线降噪耳机",category:"3C / 音频",sellingPoints:["主动降噪","长续航","低延迟"],audience:"18–35岁通勤、学生、游戏用户"},shots,cost,hardware:DEFAULT_HARDWARE,plan:localPlan(DEFAULT_HARDWARE)});}