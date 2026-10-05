import http from "node:http";
import {LocalAssetLibrary} from "./store.mjs";
const lib=new LocalAssetLibrary();
const json=(res,status,data)=>{res.writeHead(status,{"content-type":"application/json; charset=utf-8","access-control-allow-origin":"*","access-control-allow-methods":"GET,POST,DELETE,OPTIONS","access-control-allow-headers":"content-type"});res.end(JSON.stringify(data))};
const server=http.createServer(async(req,res)=>{
 if(req.method==="OPTIONS"){res.writeHead(204,{"access-control-allow-origin":"*","access-control-allow-methods":"GET,POST,DELETE,OPTIONS","access-control-allow-headers":"content-type"});return res.end()}
 const u=new URL(req.url||"/","http://127.0.0.1");
 if(u.pathname==="/health")return json(res,200,{ok:true,storage:"本地文件资产库"});
 if(u.pathname==="/assets"&&req.method==="GET")return json(res,200,{assets:lib.list(u.searchParams.get("kind")||undefined)});
 if(u.pathname==="/assets/reusable"&&req.method==="GET")return json(res,200,{assets:lib.findReusable(u.searchParams.get("kind")||"actor",(u.searchParams.get("tags")||"").split(",").filter(Boolean))});
 if(u.pathname==="/assets"&&req.method==="POST"){let body="";for await(const c of req)body+=c;try{return json(res,201,lib.add(JSON.parse(body)))}catch(e){return json(res,400,{error:"保存本地资产失败"})}}
 if(u.pathname.startsWith("/assets/")&&req.method==="DELETE")return json(res,200,{ok:lib.remove(u.pathname.split("/").pop())});
 return json(res,404,{error:"未找到本地工作器接口"});
});
server.listen(Number(process.env.AD_STUDIO_PORT||3939),"127.0.0.1",()=>console.log("AD STUDIO 本地资产库：http://127.0.0.1:"+Number(process.env.AD_STUDIO_PORT||3939)));