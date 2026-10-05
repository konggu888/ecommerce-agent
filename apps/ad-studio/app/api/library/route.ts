import {NextResponse} from "next/server";
import {DEFAULT_ACTORS} from "@/lib/actor-library";
import {DEFAULT_SCENES} from "@/lib/asset-library";
export async function GET(){return NextResponse.json({actors:DEFAULT_ACTORS,scenes:DEFAULT_SCENES,upload:{enabled:true,aiGenerationSlot:true}})}