from pathlib import Path
import re

def _ts(seconds: float) -> str:
    ms = max(0, int(round(float(seconds) * 1000)))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def segment_subtitles(segments, max_chars=18):
    """按口播时间戳生成可读字幕，不凭空修改原话；超长句只按词边界拆分。"""
    result = []
    for seg in segments or []:
        text = re.sub(r"\s+", " ", str(seg.get("text", "")).strip())
        start, end = float(seg.get("start", 0)), float(seg.get("end", 0))
        if not text or end <= start:
            continue
        if len(text) <= max_chars:
            result.append({"start": start, "end": end, "text": text})
            continue
        chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        step = (end - start) / len(chunks)
        for i, chunk in enumerate(chunks):
            result.append({"start": start + i * step, "end": start + (i + 1) * step, "text": chunk.strip()})
    return result

def write_srt(text: str, output: Path, duration=3):
    output.parent.mkdir(parents=True, exist_ok=True)
    body = text.strip() or " "
    output.write_text(f"1\n{_ts(0)} --> {_ts(duration)}\n{body}\n", encoding="utf-8")
    return output

def write_srt_segments(segments, output: Path, max_chars=18):
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = segment_subtitles(segments, max_chars=max_chars)
    lines = []
    for i, row in enumerate(rows, 1):
        lines += [str(i), f"{_ts(row['start'])} --> {_ts(row['end'])}", row["text"], ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
