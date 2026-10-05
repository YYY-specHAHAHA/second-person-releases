# 第二人称公开发布仓库

此仓库仅用于 `second.translens.cn` 静态网站与已验收的正式签名 APK。应用源码、签名私钥、用户对话、API Key、测试者信息不进入此仓库。

公开页面由私有源码仓库中的 `release/scripts/build_public_site.py` 生成，并复制到 `site/`。GitHub Pages 使用本仓库的 `pages.yml` 部署。每个正式版本的 Release 附件须包含 `second-person-<版本>.apk`、`SHA256SUMS.txt`、公开版 `release-manifest.json` 和发布说明；Tag 为 `v<版本>`。在上传附件、验证可公开下载和完成发布门禁前，网站保持“正式版准备中”，且不存在 `latest.json`。

发布步骤与回滚措施见私有源码仓库 `release/release-runbook.md`。用户支持邮箱：dosomethinginteresting@outlook.com。
