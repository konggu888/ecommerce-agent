from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from pathlib import Path
import json
import re

from .browser_skill import fetch_with_browser_skill


@dataclass
class ProductInfo:
    url: str
    platform: str
    name: str = "待解析商品"
    description: str = ""
    price: str = ""
    images: list[str] = None
    fetched: bool = False
    error: str = ""
    source: str = ""

    def __post_init__(self):
        if self.images is None:
            self.images = []

    def to_dict(self):
        return asdict(self)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta = {}
        self.images = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            value = attrs.get("content")
            if key and value:
                self.meta[key.lower()] = value.strip()
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def _platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "taobao.com" in host or "tmall.com" in host:
        return "淘宝"
    if "jd.com" in host:
        return "京东"
    if "pinduoduo.com" in host or "yangkeduo.com" in host:
        return "拼多多"
    if "1688.com" in host:
        return "1688"
    if "douyin.com" in host:
        return "抖音"
    return "自动识别"


def _clean(value: str, limit: int) -> str:
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def _from_html(info: ProductInfo, html: str) -> ProductInfo:
    parser = _MetaParser()
    parser.feed(html)
    title = parser.meta.get("og:title") or parser.meta.get("twitter:title") or parser.title.strip()
    desc = parser.meta.get("og:description") or parser.meta.get("description") or ""
    image = parser.meta.get("og:image")
    images = [image] if image else []
    images.extend(parser.images[:19])
    info.name = _clean(title, 200) or "待解析商品"
    info.description = _clean(desc, 1000)
    info.images = list(dict.fromkeys(images))
    info.price = parser.meta.get("product:price:amount") or parser.meta.get("price") or ""
    info.fetched = True
    info.source = "direct_http"
    return info


def parse_product_url(url: str, timeout: int = 8, browser_fallback: bool = True) -> ProductInfo:
    url = (url or "").strip()
    if not url:
        return ProductInfo(url="", platform="自动识别", error="商品链接为空")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ProductInfo(url=url, platform="自动识别", error="不是有效的 HTTP/HTTPS 商品链接")

    info = ProductInfo(url=url, platform=_platform(url))
    direct_error = ""
    try:
        req = Request(url, headers={"User-Agent": "AdStudio/1.0 product-parser"})
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
        return _from_html(info, raw.decode(charset, errors="replace"))
    except Exception as exc:
        direct_error = str(exc)

    if browser_fallback:
        try:
            browser_result = fetch_with_browser_skill(url, timeout=max(timeout, 15))
            if browser_result.get("ok"):
                info.name = _clean(browser_result.get("name", ""), 200) or info.name
                info.description = _clean(browser_result.get("description", ""), 1000)
                info.price = str(browser_result.get("price", "") or "")
                info.images = list(dict.fromkeys(browser_result.get("images", [])[:20]))
                info.fetched = bool(info.name != "待解析商品" or info.description or info.price or info.images)
                if info.fetched:
                    info.source = "browser_skill"
                    return info
            browser_error = browser_result.get("error", "浏览器采集未读取到商品资料")
        except Exception as exc:
            browser_error = str(exc)
        info.error = f"直接抓取失败：{direct_error}；浏览器Skill也未完成：{browser_error}"
        return info

    info.error = direct_error
    return info


def save_product(info: ProductInfo, root: Path, project_id: str) -> Path:
    target = root / "products" / f"{project_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(info.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target
