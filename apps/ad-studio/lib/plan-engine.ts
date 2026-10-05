import {DEFAULT_ACTORS,selectActors} from "./actor-library";
import {DEFAULT_SCENES} from "./asset-library";
import {estimateCost} from "./engine";
export function buildCreativePlan(level:number,form:string){
 const tags=form==="真人剧情"?["生活"]:form==="街头采访"?["街头","UGC"]:form==="职场"?["职场","专业"]:["口播"];
 const actors=selectActors(DEFAULT_ACTORS,undefined,tags);
 const scene=DEFAULT_SCENES.find(s=>s.tags.some(t=>tags.includes(t)))||DEFAULT_SCENES[0];
 const shots=level>=3?6:5;
 return {shots,actors,scene,cost:estimateCost(shots),localAssets:true};
}