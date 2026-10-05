import subprocess

def detect_gpu():
    try:
        p=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
        if p.returncode!=0 or not p.stdout.strip(): return {'available':False,'mode':'CPU'}
        name,mem,driver=[x.strip() for x in p.stdout.splitlines()[0].split(',')]
        return {'available':True,'name':name,'vram_mb':int(mem),'driver':driver,'mode':'4050/6GB保守模式' if int(mem)<=7168 else '高显存模式'}
    except Exception as e:
        return {'available':False,'mode':'CPU','error':str(e)}
