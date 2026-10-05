from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from pathlib import Path
import json
import re


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


def parse_product_url(url: str, timeout: int = 8) -> ProductInfo:
    url = (url or "").strip()
    if not url:
        return ProductInfo(url="", platform="自动识别", error="商品链接为空")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ProductInfo(url=url, platform="自动识别", error="不是有效的 HTTP/HTTPS 商品链接")

    info = ProductInfo(url=url, platform=_platform(url))
    try:
        req = Request(url, headers={"User-Agent": "AdStudio/1.0 product-parser"})
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
        html = raw.decode(charset, errors="replace")
        parser = _MetaParser()
        parser.feed(html)

        title = parser.meta.get("og:title") or parser.meta.get("twitter:title") or parser.title.strip()
        desc = parser.meta.get("og:description") or parser.meta.get("description") or ""
        image = parser.meta.get("og:image")
        images = [image] if image else []
        images.extend(parser.images[:19])

        info.name = re.sub(r"\\s+", " ", title).strip()[:200] or "待解析商品"
        info.description = re.sub(r"\\s+", " ", desc).strip()[:1000]
        info.images = list(dict.fromkeys(images))
        price = parser.meta.get("product:price:amount") or parser.meta.get("price")
        info.price = price or ""
        info.fetched = True
        return info
    except Exception as exc:
        info.error = str(exc)
        return info


def save_product(info: ProductInfo, root: Path, project_id: str) -> Path:
    target = root / "products" / f"{project_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(info.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target
