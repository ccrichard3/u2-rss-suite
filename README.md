# u2-rss-suite

中文 | [English](#english)

一个面向 U2 场景的 RSS 工具合集仓库，当前包含：

- `u2-catchmagic-rss/`
  - 扫描 U2 魔法种子页面
  - 生成 RSS，供 Vertex / autobrr 订阅
- `u2-newtorrents-rss/`
  - 扫描 U2 新种页面
  - 生成 RSS，统一交给 Vertex 控制后续下载

推荐链路：

`U2 页面 -> RSS 服务 -> Vertex -> qBittorrent / 其他下载器`

这样脚本只负责“发现”和“输出 RSS”，下载、分类、限速、客户端管理都放在 Vertex。

## 仓库结构

```text
u2-rss-suite/
├── u2-catchmagic-rss/
│   ├── catch_magic.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
└── u2-newtorrents-rss/
    ├── download_new_torrents.py
    ├── Dockerfile
    ├── docker-compose.yml
    └── .env.example
```

## 快速开始

克隆仓库：

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

## 已整理内容

- 已移除真实 cookie / passkey / 私密配置
- 统一改成环境变量配置
- 已容器化，便于新设备部署
- 每个子项目都带 `.env.example`、`docker-compose.yml`、`README.md`

## 适合的使用方式

- 想抓魔法种子：用 `u2-catchmagic-rss`
- 想抓符合规则的新种：用 `u2-newtorrents-rss`
- 想统一控制下载行为：让 Vertex 订阅 RSS，再由 Vertex 推送给下载器

## 注意事项

- `u2-newtorrents-rss` 默认首次运行只建立基线，RSS 可能暂时为空
- 两个服务都不会直接替你管理下载器配置，推荐和 Vertex 配合使用
- 发布到 GitHub 前请确认 `.env` 和 `data/` 没有被提交

---

## English

A collection of U2-oriented RSS tools, currently including:

- `u2-catchmagic-rss/`
  - Scans the U2 promotion / magic page
  - Exposes matched entries as RSS for Vertex / autobrr
- `u2-newtorrents-rss/`
  - Scans the U2 new torrents page
  - Exposes matched entries as RSS so Vertex can handle downloads

Recommended flow:

`U2 pages -> RSS service -> Vertex -> qBittorrent / other download clients`

This keeps the scripts focused on discovery and RSS generation, while download control stays in Vertex.

## Repository layout

```text
u2-rss-suite/
├── u2-catchmagic-rss/
│   ├── catch_magic.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
└── u2-newtorrents-rss/
    ├── download_new_torrents.py
    ├── Dockerfile
    ├── docker-compose.yml
    └── .env.example
```

## Quick start

Clone the repository:

```bash
git clone https://github.com/ccrichard3/u2-rss-suite.git
cd u2-rss-suite
```

Deploy `U2-CatchMagic-RSS`:

```bash
cd u2-catchmagic-rss
cp .env.example .env
# edit .env
docker compose up -d --build
```

Deploy `U2-NewTorrents-RSS`:

```bash
cd ../u2-newtorrents-rss
cp .env.example .env
# edit .env
docker compose up -d --build
```

## What has been cleaned up

- Real cookies / passkeys / private values were removed
- Configuration is now environment-variable based
- Both tools are containerized for easier deployment
- Each subproject includes `.env.example`, `docker-compose.yml`, and its own README

## Recommended usage

- Use `u2-catchmagic-rss` for promotion / magic tracking
- Use `u2-newtorrents-rss` for rule-based new torrent tracking
- Let Vertex subscribe to the RSS feeds and handle download actions centrally

## Notes

- `u2-newtorrents-rss` skips existing items on first run by default, so the RSS feed may be empty at first
- The scripts are designed to generate RSS, not to replace your download manager setup
- Make sure `.env` and `data/` are not committed before pushing changes
