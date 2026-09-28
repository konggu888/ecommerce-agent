export type JobStatus = 'QUEUED'|'RUNNING'|'COMPLETED'|'FAILED'|'CANCELLED';
export interface JobState { jobId:string; type:string; status:JobStatus; totalTasks:number; completedTasks:number; failedTasks:number; currentTask?:string; startedAt?:string; updatedAt:string; finishedAt?:string; error?:string; resultLocation?:string; }
export function createJob(jobId:string,type:string,totalTasks:number):JobState{return {jobId,type,status:'QUEUED',totalTasks,completedTasks:0,failedTasks:0,updatedAt:new Date().toISOString()};}
export function startJob(job:JobState,currentTask?:string):JobState{return {...job,status:'RUNNING',currentTask,startedAt:job.startedAt??new Date().toISOString(),updatedAt:new Date().toISOString()};}
export function updateJob(job:JobState,completedTasks:number,currentTask?:string,failedTasks=job.failedTasks):JobState{return {...job,status:'RUNNING',completedTasks,failedTasks,currentTask,updatedAt:new Date().toISOString()};}
export function completeJob(job:JobState,resultLocation?:string):JobState{return {...job,status:'COMPLETED',completedTasks:job.totalTasks,currentTask:undefined,finishedAt:new Date().toISOString(),updatedAt:new Date().toISOString(),resultLocation};}
export function failJob(job:JobState,error:string):JobState{return {...job,status:'FAILED',error,finishedAt:new Date().toISOString(),updatedAt:new Date().toISOString()};}
export function progress(job:JobState){return {percent:job.totalTasks?Math.round(job.completedTasks/job.totalTasks*100):0,remaining:Math.max(0,job.totalTasks-job.completedTasks),status:job.status};}
