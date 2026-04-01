# U2-NewTorrents-RSS

中文 | [English](#english)

基于 `https://github.com/Haruite/u2_scripts` 修改，专为 Vertex 等集成管理工具设计的 U2 自动抓新脚本。

不同于原版脚本通过监控文件夹追加任务，该脚本通过**生成 RSS 订阅源**实现跨平台任务分发，集成工具管理更方便。

## 🌟 特点

- **RSS 驱动**
  - 不下载物理种子文件
  - 仅输出标准 RSS 2.0 协议内容
  - 由 Vertex 统一接管下载、删除逻辑

- **面向持续运行**
  - 适合 VPS、Docker 和多设备部署
  - 支持首次建立基线和状态持久化

- **内置服务**
  - 自带轻量级 HTTP 服务
  - Vertex、autobrr 等工具可直接订阅

- **智能筛选**
  - 继承原版主要逻辑
  - 支持按置顶、做种人数、发布时间、免费状态等条件进行筛选

## 🚀 部署指南（推荐）

### 1. 准备文件

在宿主机创建目录（如 `/opt/u2_rss`），并确保包含以下文件：

- `download_new_torrents.py`（核心逻辑代码）
- `requirements.txt`（依赖库声明）
- `Dockerfile`（容器构建文件）
- `docker-compose.yml`
- `.env.example`

### 2. 配置参数

复制并编辑配置：

```bash
cp .env.example .env
```

重点参数：

- `U2_COOKIE`
  - 填入你的 U2 cookie
- `U2_PASSKEY`
  - 可选；留空时脚本会尝试从详情页解析
- `INTERVAL`
  - 扫描间隔
- `RSS_HTTP_PORT`
  - RSS 服务端口，默认 `8788`
- `SKIP_EXISTING_ON_FIRST_RUN`
  - 默认 `true`
  - 首次运行只建立基线，不回填当前页面已有项目

### 3. 构建并运行

```bash
docker compose up -d --build
```

启动后访问：

- `http://你的IP:8788/rss.xml`

## 🔗 在 Vertex 中使用

- 在 Vertex 的 RSS 订阅页面点击添加
- 地址填写：`http://你的IP:8788/rss.xml`
- 勾选 **“推送种子文件”**
- 建议填写 cookie，保证后续拉种稳定

## ❗️注意事项

- 默认 `SKIP_EXISTING_ON_FIRST_RUN=true`
  - 第一次启动只建立基线
  - 所以初始阶段 RSS 可能为空
- 如果希望首次启动就把当前命中的项目写入 RSS，可改为：

```env
SKIP_EXISTING_ON_FIRST_RUN=false
```

- 如果 RSS 里暂时没有 item，Vertex 可能提示错误，一般可忽略
- 若无法访问，请检查 VPS / 防火墙是否已放行 `8788` 端口
- 其他集成管理工具未全部测试，通常只要拉种时带上 cookie 就能避免大部分问题

## 📝 免责声明

本脚本仅供技术交流与学习使用，请务必严格遵守 U2 站点的相关使用规定。作者不对因使用本脚本导致的任何账号违规、封禁等后果承担责任。

---

## English

Adapted from `https://github.com/Haruite/u2_scripts`, this is an RSS-based U2 new-torrent tracker designed for integration tools such as Vertex.

### Features

- Outputs standard RSS 2.0 content instead of using a watch-folder workflow
- Lets Vertex handle downstream download management
- Includes a lightweight built-in HTTP service
- Supports baseline initialization on first run

### Quick deployment

```bash
cp .env.example .env
# edit .env
docker compose up -d --build
```

Feed URL:

- `http://<your-ip>:8788/rss.xml`

### Disclaimer

This project is for technical exchange and learning only. Please strictly follow the rules of the U2 site. The author assumes no responsibility for account violations, bans, or other consequences caused by using this project.
