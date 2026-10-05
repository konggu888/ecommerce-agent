from pathlib import Path

def write_srt(text:str,output:Path,duration=3):
    output.parent.mkdir(parents=True,exist_ok=True)
    body=text.strip() or ' '
    output.write_text(f'1\n00:00:00,000 --> 00:00:{int(duration):02d},000\n{body}\n',encoding='utf-8')
    return output
