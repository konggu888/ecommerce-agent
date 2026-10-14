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

def _split_caption_text(text: str, max_chars: int) -> list[str]:
    """Split text at nearby punctuation where possible, with a hard character limit."""
    remaining = re.sub(r"\s+", " ", str(text).strip())
    max_chars = max(1, int(max_chars))
    chunks = []
    punctuation = "，。！？；：,.!?;:"
    while len(remaining) > max_chars:
        window = remaining[:max_chars]
        boundary = max((window.rfind(mark) for mark in punctuation), default=-1)
        cut = boundary + 1 if boundary >= max(4, max_chars // 2) else max_chars
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks or [" "]


def plan_subtitle_timing(text: str, duration=3, max_chars=18, min_segment_seconds=0.65):
    """Build timed captions for the real clip duration and report density compromises."""
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        duration = 3.0
    if not duration > 0:
        duration = 3.0
    duration = min(duration, 24 * 60 * 60)
    body = re.sub(r"\s+", " ", str(text).strip()) or " "
    max_chars = max(1, int(max_chars))
    try:
        min_segment_seconds = max(0.1, float(min_segment_seconds))
    except (TypeError, ValueError):
        min_segment_seconds = 0.65
    chunks = _split_caption_text(body, max_chars)
    max_cues = max(1, int(duration / min_segment_seconds))
    warnings = []
    effective_max_chars = max_chars
    if len(chunks) > max_cues:
        effective_max_chars = max(max_chars, (len(body) + max_cues - 1) // max_cues)
        chunks = _split_caption_text(body, effective_max_chars)
        warnings.append("镜头时长不足以容纳常规长度字幕，已减少切换次数；单条字幕可能偏密。")
    chars_per_second = len(body.replace(" ", "")) / duration
    if chars_per_second > 8:
        warnings.append(f"字幕信息密度偏高（约 {chars_per_second:.1f} 字/秒），建议缩短文案或延长镜头。")
    segment_duration = duration / len(chunks)
    rows = []
    for index, chunk in enumerate(chunks):
        start = index * segment_duration
        end = duration if index == len(chunks) - 1 else (index + 1) * segment_duration
        rows.append({"start": start, "end": end, "text": chunk})
    return {"segments": rows, "duration": duration, "char_count": len(body.replace(" ", "")),
            "chars_per_second": chars_per_second, "segment_count": len(rows),
            "effective_max_chars": effective_max_chars, "warnings": warnings}


def analyze_subtitle_density(text: str, duration=3, max_chars=18):
    """Return a UI-safe density summary without changing the subtitle text."""
    plan = plan_subtitle_timing(text, duration=duration, max_chars=max_chars)
    return {key: plan[key] for key in (
        "duration", "char_count", "chars_per_second", "segment_count",
        "effective_max_chars", "warnings"
    )}


def write_srt(text: str, output: Path, duration=3, max_chars=18):
    """A108: Write adaptive subtitles spanning the actual clip duration, not a fixed 3 seconds."""
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = plan_subtitle_timing(text, duration=duration, max_chars=max_chars)
    lines = []
    for i, row in enumerate(plan["segments"], 1):
        lines += [str(i), f"{_ts(row['start'])} --> {_ts(row['end'])}", row["text"], ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    return output

def write_srt_segments(segments, output: Path, max_chars=18):
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = segment_subtitles(segments, max_chars=max_chars)
    lines = []
    for i, row in enumerate(rows, 1):
        lines += [str(i), f"{_ts(row['start'])} --> {_ts(row['end'])}", row["text"], ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


_SRT_TIMESTAMP = re.compile(r"^(\\d{2,}:\\d{2}:\\d{2}[,.]\\d{1,3})\\s*-->\\s*(\\d{2,}:\\d{2}:\\d{2}[,.]\\d{1,3})(?:\\s+.*)?$")


def _parse_srt_timestamp(value: str) -> float:
    match = re.fullmatch(r"(\\d{2,}):(\\d{2}):(\\d{2})[,.](\\d{1,3})", value.strip())
    if not match:
        raise ValueError("SRT 时间戳格式无效")
    hours, minutes, seconds, fraction = match.groups()
    if int(minutes) >= 60 or int(seconds) >= 60:
        raise ValueError("SRT 时间戳中的分钟或秒超出范围")
    millis = int(fraction.ljust(3, "0")[:3])
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + millis / 1000.0


def parse_srt_cues(source: Path | str, duration: float | None = None,
                   end_tolerance: float = 0.15) -> dict:
    """Read real cue windows from SRT and validate them against one clip timeline."""
    path = Path(source)
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError("SRT 文件不存在或为空")
    raw = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\\n\\s*\\n", raw.replace("\\r\\n", "\\n").replace("\\r", "\\n").strip())
    cues = []
    previous_start = -1.0
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        time_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if time_index is None or time_index + 1 >= len(lines):
            raise ValueError("SRT cue 缺少时间窗或字幕文本")
        match = _SRT_TIMESTAMP.fullmatch(lines[time_index])
        if not match:
            raise ValueError("SRT cue 时间窗格式无效")
        start, end = _parse_srt_timestamp(match.group(1)), _parse_srt_timestamp(match.group(2))
        text = "\\n".join(lines[time_index + 1:]).strip()
        if not text or end <= start:
            raise ValueError("SRT cue 文本为空或结束时间不晚于开始时间")
        if start + 1e-6 < previous_start:
            raise ValueError("SRT cue 时间顺序不一致")
        previous_start = start
        cues.append({"start": start, "end": end, "duration": end - start, "text": text})
    if not cues:
        raise ValueError("SRT 没有有效字幕 cue")
    if duration is not None:
        clip_duration = float(duration)
        if not clip_duration > 0:
            raise ValueError("镜头时长无效，无法校验 SRT 时间轴")
        if any(cue["start"] < -1e-6 or cue["end"] > clip_duration + end_tolerance for cue in cues):
            raise ValueError("SRT cue 超出镜头时间轴")
        if abs(cues[-1]["end"] - clip_duration) > end_tolerance:
            raise ValueError("SRT 结束时间与当前镜头时长不匹配")
    return {"cues": cues, "cue_count": len(cues), "timeline_end": cues[-1]["end"], "duration": duration}
