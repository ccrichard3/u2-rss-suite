# u2-rss-suite

中文 | [English](#english)

基于以下项目修改：

- `https://github.com/zS1m/U2-CatchMagic-RSS`
- `https://github.com/Haruite/u2_scripts`

专为 Vertex 等集成管理工具设计的 U2 自动追魔、抓新脚本。

不同于原版脚本通过监控文件夹追加任务，该仓库统一通过**生成 RSS 订阅源**实现跨平台任务分发，后续下载、删除、分类等逻辑统一交给 Vertex 管理。

## 📦 包含项目

### U2-CatchMagic-RSS

- 自动追踪 U2 魔法种子
- 输出 RSS 给 Vertex / autobrr 订阅
- 适合统一接入 Vertex 的追魔场景

目录：
- `u2-catchmagic-rss/`

### U2-NewTorrents-RSS

- 自动筛选 U2 新种
- 输出 RSS 给 Vertex 统一处理
- 不再直接写入 qB 监控目录

目录：
- `u2-newtorrents-rss/`

## 🌟 特点

- **RSS 驱动**
  - 不下载物理种子文件
  - 仅输出标准 RSS 2.0 协议内容
  - 由 Vertex 统一接管下载、删除逻辑

- **面向集成管理**
  - 适合 Vertex、autobrr 等工具直接订阅
  - 更适合 VPS、多设备和容器化部署

- **内置服务**
  - 自带轻量级 HTTP 服务
  - 启动后即可输出 `/rss.xml`

- **智能筛选**
  - 继承原版核心逻辑
  - 支持按体积、做种人数、发布时间、魔法关键词等条件进行筛选

## 🚀 快速开始

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
- 地址填写对应服务的 `/rss.xml`
- 勾选 **“推送种子文件”**
- 下载行为统一让 Vertex 处理

## ❗️注意事项

- `u2-newtorrents-rss` 默认首次运行只建立基线，因此 RSS 可能暂时为空
- 如果 RSS 暂时没有 item，Vertex 可能提示异常，一般可忽略
- Vertex 建议填写 U2 cookie，避免后续拉种时出现权限问题

## 📝 免责声明

本脚本仅供技术交流与学习使用，请务必严格遵守 U2 站点的相关使用规定。作者不对因使用本脚本导致的任何账号违规、封禁等后果承担责任。

---

## English

Adapted from:

- `https://github.com/zS1m/U2-CatchMagic-RSS`
- `https://github.com/Haruite/u2_scripts`

This repository provides U2 automation scripts for Vertex-style integrated management tools.

Instead of appending tasks through a watch-folder workflow, these scripts expose RSS feeds so that downstream download, deletion, and category management can be handled centrally by Vertex.

### Included projects

- `u2-catchmagic-rss`
  - Tracks U2 promotion / magic entries
  - Exposes them as RSS for Vertex / autobrr

- `u2-newtorrents-rss`
  - Tracks U2 new torrents
  - Exposes them as RSS for Vertex-managed download workflows

### Highlights

- RSS-driven workflow
- Built for integration tools such as Vertex
- Lightweight built-in HTTP RSS service
- Keeps the core filtering logic from the original scripts

### Disclaimer

This project is for technical exchange and learning only. Please strictly follow the rules of the U2 site. The author assumes no responsibility for account violations, bans, or other consequences caused by using this project.
