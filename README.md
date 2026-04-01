# u2-rss-suite

面向 U2 使用场景的 RSS 工具合集，统一采用：

`U2 页面 -> RSS 输出 -> Vertex -> 下载器`

也就是说，这个仓库里的脚本都负责“发现目标”和“生成 RSS”，后续下载、删种、分类、限速等动作统一交给 Vertex 之类的集成管理工具处理。

## 当前包含

### 1. U2-CatchMagic-RSS

基于 `u2_scripts/catch_magic.py` 改造，用于追踪 U2 魔法种子并输出 RSS。

适合：
- 追魔法
- 按魔法规则筛选
- 让 Vertex 统一接管下载

目录：
- `u2-catchmagic-rss/`

### 2. U2-NewTorrents-RSS

基于 `u2_scripts/download_new_torrents.py` 改造，用于筛选 U2 新种并输出 RSS。

适合：
- 抓新种
- 按置顶 / 免费 / 做种情况自动筛选
- 不再直接写入 qB 监控目录

目录：
- `u2-newtorrents-rss/`

## 🌟 设计思路

- **RSS 驱动**：脚本不直接管理下载器，统一输出 RSS
- **便于集成**：适合配合 Vertex / autobrr / 其他 RSS 工具
- **Docker 优先**：默认按容器部署整理，新设备迁移更方便
- **保留核心逻辑**：尽量继承原脚本筛选思路，只把输出链路改成 RSS

## 🚀 快速部署

先拉取仓库：

```bash
git clone https://github.com/ccrichard3/u2-rss-suite.git
cd u2-rss-suite
```

部署 `U2-CatchMagic-RSS`：

```bash
cd u2-catchmagic-rss
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

部署 `U2-NewTorrents-RSS`：

```bash
cd ../u2-newtorrents-rss
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

## 🔗 与 Vertex 配合使用

- 在 Vertex 中添加 RSS 订阅
- 订阅地址填对应服务的 `/rss.xml`
- 勾选“推送种子文件”
- 下载行为统一让 Vertex 处理

## ❗️注意事项

- `u2-newtorrents-rss` 默认首次运行只建立基线，所以 RSS 可能暂时为空
- 某些情况下如果 RSS 暂时没有 item，Vertex 可能提示订阅异常，通常可忽略
- 建议在 Vertex 中填写 U2 cookie，避免拉取种子时出现权限问题
- 发布或分享前请确认 `.env`、`data/` 等私密内容没有提交

## 📝 免责声明

本仓库仅供技术交流与学习使用，请务必遵守相关站点规则。因使用脚本产生的账号风险、权限问题或其他后果，请自行承担。

---

## English Summary

This repository contains U2-oriented RSS tools adapted from `u2_scripts`.

- `u2-catchmagic-rss`: track U2 promotion / magic entries and expose them as RSS
- `u2-newtorrents-rss`: track U2 new torrents and expose them as RSS

Recommended flow:

`U2 pages -> RSS feeds -> Vertex -> download client`

These scripts are designed for integration tools such as Vertex. They focus on filtering and RSS generation, while downstream download actions are handled centrally by Vertex.
