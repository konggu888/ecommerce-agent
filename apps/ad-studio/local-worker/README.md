# 本地4050工作器

运行位置：用户自己的 Windows 笔记本，不运行在 Vercel。

- RTX 4050 Laptop 6GB：本地AI小任务、素材预处理、视频后期。
- CPU：商品解析、任务编排、文件管理。
- FFmpeg：裁切、拼接、字幕、音频混合、最终编码。
- 云端：只处理本地无法高质量完成的关键视频、人物、场景生成。

预计云端总成本 > ¥3.00 时必须返回 requires_confirmation=true，不能自动换模型、降低质量、减少镜头。

Windows 建议安装 NVIDIA 驱动、FFmpeg、Node.js 20+；可选安装 Ollama 用于本地小模型。

运行：
node local-worker/check-hardware.mjs
node local-worker/check-tools.mjs
node local-worker/render-demo.mjs <输入视频> [输出视频]

实际生成器通过 adapter 接入，不绑定单一供应商。