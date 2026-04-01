# U2-CatchMagic-RSS

基于 `u2_scripts/catch_magic.py` 修改，专为 Vertex、autobrr 等集成管理工具设计的 U2 自动追魔脚本。

不同于原版通过本地下载链路处理任务，这个版本统一改为**生成 RSS 订阅源**，由 Vertex 接管后续下载流程，跨平台部署和管理都更方便。

## 🌟 特点

- **RSS 驱动**
  - 不直接下载物理种子文件
  - 输出标准 RSS 2.0 内容
  - 由 Vertex 统一接管下载、删种、分类等动作

- **保留核心逻辑**
  - 延续原脚本的主要筛选思路
  - 支持按做种人数、发布时间、魔法类型等条件筛选

- **容器友好**
  - 仓库已提供 `Dockerfile`、`docker-compose.yml`
  - 新设备部署更直接

- **内置 HTTP 服务**
  - 启动后直接提供 `/rss.xml`
  - Vertex、autobrr 等工具可直接订阅

## 🚀 部署指南（推荐）

### 1. 准备文件

本目录已经包含部署所需文件：

- `catch_magic.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### 2. 配置参数

复制配置模板并编辑：

```bash
cp .env.example .env
```

重点参数：

- `U2_COOKIE`
  - 你的 U2 cookie
  - 支持填写 `nexusphp_u2=...` 或只填值
- `UID`
  - 你的 U2 UID
- `API_TOKEN`
  - 推荐填写，稳定性更好
- `RSS_HTTP_PORT`
  - RSS 服务端口，默认 `8787`
- `INTERVAL`
  - 扫描周期

### 3. 构建并运行

推荐使用 Docker Compose：

```bash
docker compose up -d --build
```

启动后访问：

- `http://你的IP:8787/`
- `http://你的IP:8787/rss.xml`

如果你修改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

## 🔗 在 Vertex 中使用

- 在 Vertex 的 RSS 订阅页面点击添加
- 地址填写：`http://你的IP:8787/rss.xml`
- 勾选 **“推送种子文件”**
- 建议填写 U2 cookie，避免拉取种子时出现权限问题

## ❗️注意事项

- Vertex 即使不使用“抓取免费”逻辑，也建议填写 cookie
- 如果当前没有命中项目，`rss.xml` 可能暂时没有 item，Vertex 可能提示异常，一般可忽略
- 若无法访问，请检查 VPS / 防火墙是否放行对应端口
- 如需代理，可在 `.env` 中配置 `HTTP_PROXY` / `HTTPS_PROXY`

## 📝 免责声明

本脚本仅供技术交流与学习使用，请务必遵守 U2 站点相关规则。因使用本脚本导致的账号风险、违规或封禁等后果，请自行承担。

---

## English Summary

An RSS-based U2 promotion / magic tracker adapted from `u2_scripts/catch_magic.py`.

- Generates RSS instead of directly handling torrent downloads
- Designed to work with Vertex / autobrr
- Keeps the core filtering logic while exposing `/rss.xml`
- Recommended deployment: `docker compose up -d --build`
