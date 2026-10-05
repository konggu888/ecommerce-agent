from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

@dataclass
class GenerationRequest:
    prompt:str
    output:Path
    duration:float=3
    reference_assets:list[str]=None

class ImageGenerator(Protocol):
    def generate(self,request:GenerationRequest)->Path: ...
class VideoGenerator(Protocol):
    def generate(self,request:GenerationRequest)->Path: ...
class VoiceGenerator(Protocol):
    def generate(self,text:str,output:Path)->Path: ...
class SmallLLM(Protocol):
    def complete(self,prompt:str)->str: ...

class UnconfiguredProvider:
    def generate(self,*args,**kwargs):
        raise RuntimeError('尚未配置云端生成器。请在设置中接入图像/视频/配音供应商。')
    def complete(self,*args,**kwargs):
        raise RuntimeError('尚未配置本地或云端小模型。')
