export type BuyerPlatform='TAOBAO'|'PINDUODUO';
export interface BuyerVisibleProduct {
 platform:BuyerPlatform; query?:string; rank?:number; productId?:string; title?:string;
 price?:number; originalPrice?:number; rating?:number; reviewCount?:number;
 salesCount?:number; seller?:string; category?:string; tags?:string[];
 promotion?:string; shipping?:string; stockText?:string; sourceUrl:string;
 observedAt:string; visibilityMode:'BUYER_SESSION'; evidence:string[];
}
export interface BuyerSessionAdapter {
 platform:BuyerPlatform;
 search(page:any,query:string):Promise<BuyerVisibleProduct[]>;
 openProduct(page:any,url:string):Promise<BuyerVisibleProduct>;
}
function text(v:any){return typeof v==='string'?v.trim():undefined}
export function createBuyerSessionAdapter(platform:BuyerPlatform):BuyerSessionAdapter {
 return {
  platform,
  async search(page,query){
   await page.goto(platform==='TAOBAO'?'https://s.taobao.com/search?q='+encodeURIComponent(query):'https://mobile.yangkeduo.com/search_result.html?search_key='+encodeURIComponent(query));
   return extractVisibleProducts(page,query,platform);
  },
  async openProduct(page,url){
   await page.goto(url);
   const title=text(await page.title());
   return {platform,title,sourceUrl:url,observedAt:new Date().toISOString(),visibilityMode:'BUYER_SESSION',evidence:[url]};
  }
 };
}
export async function extractVisibleProducts(page:any,query:string,platform:BuyerPlatform):Promise<BuyerVisibleProduct[]> {
 const rows=await page.evaluate(()=>Array.from(document.querySelectorAll('a')).map((a:any)=>({title:(a.innerText||a.textContent||'').trim(),href:a.href})).filter((x:any)=>x.title&&x.href).slice(0,50));
 return rows.map((x:any,i:number)=>({platform,query,rank:i+1,title:x.title.slice(0,300),sourceUrl:x.href,observedAt:new Date().toISOString(),visibilityMode:'BUYER_SESSION',evidence:[x.href]}));
}
