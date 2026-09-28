# Taobao read-only API verification

Verified against the current Alibaba Developer official documentation on 2026-09-28.

Base endpoint:
`https://eco.taobao.com/router/rest`

Officially documented read-oriented 万相台无界 methods currently selected for the adapter:

- `taobao.universalbp.new.campaign.findlist` — full campaign list
- `taobao.universalbp.new.campaign.findpage` — paginated campaign list
- `taobao.universalbp.new.campaign.get` — campaign detail
- `taobao.universalbp.new.report.query.realtime` — realtime report
- `taobao.universalbp.new.report.query.campaign.special` — campaign report (restricted permission)
- `taobao.universalbp.new.report.query.item.promotion` — item promotion report
- `taobao.universalbp.new.report.chargesum` — account spend summary
- `taobao.universalbp.new.crowd.findlist` — campaign/ad-group crowd bindings
- `taobao.universalbp.new.creative.getbindcreativelist` — bound creatives
- `taobao.universalbp.new.creative.report.material` — creative material report

The official docs show these APIs use TOP common parameters including `app_key`, `sign_method` (`hmac` or `md5`), `sign`, timestamp, `v=2.0`, and `session` when authorization is required.

Write methods are intentionally blocked by the first integration stage, including campaign budget update and campaign bid update.

Important: this file records verified method names only. We do not invent undocumented request fields. Each method's request schema must be implemented from its individual official documentation page before live calls are enabled.
