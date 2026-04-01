# U2-NewTorrents-RSS

基于 `u2_scripts/download_new_torrents.py` 修改，专为 Vertex 等集成管理工具设计的 U2 新种筛选脚本。

不同于原版通过本地监控目录或直接下发任务，这个版本统一改为**生成 RSS 订阅源**，后续下载链路全部交给 Vertex 处理，更适合 VPS 和多设备部署。

## 🌟 特点

- **RSS 驱动**
  - 不再直接写入 qB 监控目录
  - 输出标准 RSS 2.0 内容
  - 后续下载、删种、分类统一交给 Vertex

- **保留筛选逻辑**
  - 延续原脚本针对新种、置顶种、免费与非免费种的规则判断
  - 可按做种数、下载数、发布时间等条件自动筛选

- **适合持续运行**
  - 支持状态持久化
  - 支持首次建立基线
  - 适合长期在 Docker 中运行

- **内置 HTTP 服务**
  - 启动后直接提供 `/rss.xml`
  - Vertex 可直接订阅

## 🚀 部署指南（推荐）

### 1. 准备文件

本目录已经包含部署所需文件：

- `download_new_torrents.py`
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
- `U2_PASSKEY`
  - 可选；留空时脚本会尝试从详情页解析
- `INTERVAL`
  - 扫描间隔
- `SKIP_EXISTING_ON_FIRST_RUN`
  - 默认 `true`
  - 首次运行只建立基线，不回填当前页面已有项目
- `RSS_HTTP_PORT`
  - RSS 服务端口，默认 `8788`

### 3. 构建并运行

推荐使用 Docker Compose：

```bash
docker compose up -d --build
```

启动后访问：

- `http://你的IP:8788/`
- `http://你的IP:8788/rss.xml`

如果你修改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

## 🔗 在 Vertex 中使用

- 在 Vertex 的 RSS 订阅页面点击添加
- 地址填写：`http://你的IP:8788/rss.xml`
- 勾选 **“推送种子文件”**
- 建议填写 U2 cookie，保证后续拉种稳定

## ❗️注意事项

- 默认 `SKIP_EXISTING_ON_FIRST_RUN=true`
  - 第一次启动只建立基线
  - 所以初始阶段 RSS 可能为空
- 如果你希望首次启动就把当前命中的项目写入 RSS，可改为：

```env
SKIP_EXISTING_ON_FIRST_RUN=false
```

- 如果 RSS 里暂时没有 item，Vertex 可能提示订阅异常，通常可以忽略
- 若无法访问，请检查 VPS / 防火墙是否已放行端口
- 如需代理，可在 `.env` 中配置 `HTTP_PROXY` / `HTTPS_PROXY`

## 📝 免责声明

本脚本仅供技术交流与学习使用，请务必遵守 U2 站点相关规则。因使用本脚本导致的账号风险、违规或封禁等后果，请自行承担。

---

## English Summary

An RSS-based U2 new-torrent tracker adapted from `u2_scripts/download_new_torrents.py`.

- Outputs RSS instead of writing to a qB watch directory
- Designed for Vertex-managed download workflows
- Supports baseline initialization on first run
- Recommended deployment: `docker compose up -d --build`
