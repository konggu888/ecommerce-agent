export type ExtractedSource = 'PRODUCT_PAGE'|'SEARCH_PAGE'|'CONTENT_PAGE'|'MARKET_PAGE'|'UNKNOWN';
export interface UrlDataInput {
 url:string; source:ExtractedSource; title?:string; price?:number; currency?:string;
 rating?:number; reviewCount?:number; salesCount?:number; cpc?:number; cvr?:number;
 stockText?:string; seller?:string; category?:string; rawText?:string; fetchedAt:string;
 evidence:string[];
}
export interface UrlFetchPlan {
 url:string; allowed:boolean; reason:string; source:ExtractedSource;
 fields:string[]; requiresServerFetch:boolean; confidence:number;
}
const productSignals=['product','item','goods','sku','shop','detail'];
const marketSignals=['market','trend','category','search','ranking'];
export function classifyUrl(url:string):ExtractedSource {
 const u=url.toLowerCase();
 if(productSignals.some(x=>u.includes(x))) return 'PRODUCT_PAGE';
 if(marketSignals.some(x=>u.includes(x))) return 'MARKET_PAGE';
 return 'UNKNOWN';
}
export function createUrlFetchPlan(url:string):UrlFetchPlan {
 try { const u=new URL(url); const source=classifyUrl(url);
   return {url,allowed:['http:','https:'].includes(u.protocol),reason:'公开网页读取；平台登录、验证码、私有数据不自动绕过',source,
     fields:['title','price','currency','rating','reviewCount','salesCount','seller','category','stockText'],requiresServerFetch:true,confidence:source==='UNKNOWN'?.35:.65};
 } catch { return {url,allowed:false,reason:'URL 无效',source:'UNKNOWN',fields:[],requiresServerFetch:true,confidence:0}; }
}
