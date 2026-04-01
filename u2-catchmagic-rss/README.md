# U2-CatchMagic-RSS

中文 | [English](#english)

基于以下项目修改：

- `https://github.com/zS1m/U2-CatchMagic-RSS`
- `https://github.com/Haruite/u2_scripts`

专为 Vertex 等集成管理工具设计的 U2 自动追魔脚本。

不同于原版脚本通过监控文件夹追加任务，该脚本通过**生成 RSS 订阅源**实现跨平台任务分发，集成工具管理更方便。

## 🌟 特点

- **RSS 驱动**
  - 不下载物理种子文件
  - 仅输出标准 RSS 2.0 协议内容
  - 由 Vertex 统一接管下载、删除逻辑

- **面向集成管理**
  - 适合 Vertex、autobrr 等工具直接订阅
  - 更适合 VPS、Docker 和多设备部署

- **内置服务**
  - 自带轻量级 HTTP 服务
  - 启动后直接输出 `/rss.xml`

- **智能筛选**
  - 继承原版主要逻辑
  - 支持按体积、做种人数、发布时间、魔法关键词等条件进行筛选

## 🚀 部署指南（推荐）

### 1. 准备文件

在宿主机创建目录（如 `/opt/u2_rss`），并确保包含以下文件：

- `catch_magic.py`（核心逻辑代码）
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
- `API_TOKEN` 和 `UID`
  - 推荐填写，可获得更稳定的数据
- `RSS_HTTP_PORT`
  - RSS 服务端口，默认 `8787`
- `INTERVAL`
  - 扫描周期

### 3. 构建并运行

```bash
docker compose up -d --build
```

启动后访问：

- `http://你的IP:8787/rss.xml`

## 🔗 在 Vertex 中使用

- 在 Vertex 的 RSS 订阅页面点击添加
- 地址填写：`http://你的IP:8787/rss.xml`
- 勾选 **“推送种子文件”**
- 网络异常时，先检查 VPS 防火墙是否已放行 `8787` 端口

## ❗️注意事项

- Vertex 勾选“推送种子文件”
- Vertex 无论是否勾选“抓取免费”，都建议填写 cookie
- 如果当前 `rss.xml` 没有 item，Vertex 可能提示错误，一般可忽略
- 其他集成管理工具未全部测试，通常只要拉种时带上 cookie 就能避免大部分问题

## 📝 免责声明

本脚本仅供技术交流与学习使用，请务必严格遵守 U2 站点的相关使用规定。作者不对因使用本脚本导致的任何账号违规、封禁等后果承担责任。

---

## English

Adapted from:

- `https://github.com/zS1m/U2-CatchMagic-RSS`
- `https://github.com/Haruite/u2_scripts`

This is an RSS-based U2 promotion / magic tracker designed for integration tools such as Vertex.

### Features

- Outputs standard RSS 2.0 content instead of downloading physical torrent files
- Lets Vertex handle downstream download and deletion logic
- Includes a lightweight built-in HTTP service
- Keeps the core filtering ideas from the original script

### Quick deployment

```bash
cp .env.example .env
# edit .env
docker compose up -d --build
```

Feed URL:

- `http://<your-ip>:8787/rss.xml`

### Disclaimer

This project is for technical exchange and learning only. Please strictly follow the rules of the U2 site. The author assumes no responsibility for account violations, bans, or other consequences caused by using this project.
