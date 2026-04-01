# U2-NewTorrents-RSS

中文 | [English](#english)

把 `download_new_torrents.py` 改造成 RSS 输出服务，统一交给 Vertex 控制下载行为。

## 功能

- 扫描 U2 新种页面
- 按脚本规则筛选新种
- 输出标准 RSS：`/rss.xml`
- 由 Vertex 订阅后再推给 qBittorrent / 其他客户端

## 部署

```bash
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

如果修改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

默认访问地址：

- `http://<IP>:8788/`
- `http://<IP>:8788/rss.xml`

## Vertex 使用

- 在 Vertex 新增 RSS 订阅
- RSS 地址填写：`http://<IP>:8788/rss.xml`
- 勾选“推送种子文件”
- 由 Vertex 统一控制后续下载动作

## 重要说明

默认 `SKIP_EXISTING_ON_FIRST_RUN=true`：

- 第一次启动只建立基线
- 不会把当前页面已有种子立刻写入 RSS
- 因此 RSS 在初始阶段可能为空，直到后续出现新的命中项

如果希望首次运行就把当前命中的项目也写入 RSS：

```env
SKIP_EXISTING_ON_FIRST_RUN=false
```

## 重要变量

- `U2_COOKIE`: U2 cookie，支持直接填 `nexusphp_u2=...` 或只填值
- `U2_PASSKEY`: 可选；留空时脚本会尝试从详情页解析
- `INTERVAL`: 扫描间隔
- `DOWNLOAD_STICKY`: 是否抓取置顶种
- `DOWNLOAD_NO_SEEDER_STICKY`: 置顶种无做种者时是否抓取
- `DOWNLOAD_NO_FREE_STICKY`: 非免费置顶种是否抓取
- `DOWNLOAD_NO_FREE_NON_STICKY`: 非免费非置顶种是否抓取
- `SKIP_EXISTING_ON_FIRST_RUN`: 首次是否跳过当前页面已有项目
- `RSS_HTTP_PORT`: RSS 服务端口

## 数据目录

- `./data/service.log`
- `./data/state.json`
- `./data/rss.xml`

## 说明

- 当前版本已经统一成 RSS 输出逻辑，不再直接写 qB 监控目录
- 推荐把所有后续下载行为都交给 Vertex
- 如需代理，可在 `.env` 中配置 `HTTP_PROXY` / `HTTPS_PROXY`

---

## English

This project converts `download_new_torrents.py` into an RSS service so that Vertex can take over all download actions.

## Features

- Scans the U2 new torrents page
- Filters items according to the script rules
- Exposes a standard RSS feed at `/rss.xml`
- Lets Vertex subscribe and forward matched torrents to qBittorrent or other clients

## Deployment

```bash
cp .env.example .env
# edit .env
docker compose up -d --build
```

If you change `RSS_HTTP_PORT`, `docker-compose.yml` will map the same port automatically.

Default URLs:

- `http://<IP>:8788/`
- `http://<IP>:8788/rss.xml`

## Using with Vertex

- Add a new RSS subscription in Vertex
- Set the feed URL to `http://<IP>:8788/rss.xml`
- Enable torrent pushing in Vertex
- Let Vertex handle the downstream download workflow

## Important behavior

By default, `SKIP_EXISTING_ON_FIRST_RUN=true`:

- The first run only creates a baseline
- Existing items on the page are not immediately added into the RSS feed
- So the feed may stay empty at first until future matched torrents appear

If you want currently matched items to be included on the first run:

```env
SKIP_EXISTING_ON_FIRST_RUN=false
```

## Important variables

- `U2_COOKIE`: U2 cookie; accepts either `nexusphp_u2=...` or the raw value
- `U2_PASSKEY`: optional; if empty, the script will try to parse it from the detail page
- `INTERVAL`: scan interval
- `DOWNLOAD_STICKY`: whether to include sticky torrents
- `DOWNLOAD_NO_SEEDER_STICKY`: whether to include sticky torrents without seeders
- `DOWNLOAD_NO_FREE_STICKY`: whether to include non-free sticky torrents
- `DOWNLOAD_NO_FREE_NON_STICKY`: whether to include non-free non-sticky torrents
- `SKIP_EXISTING_ON_FIRST_RUN`: whether to skip already-listed items on first run
- `RSS_HTTP_PORT`: HTTP port for the RSS service

## Data files

- `./data/service.log`
- `./data/state.json`
- `./data/rss.xml`

## Notes

- This version uses a unified RSS-output workflow and no longer writes directly into a qB watch directory
- It is recommended to let Vertex handle all downstream download actions
- Proxy settings can be provided through `HTTP_PROXY` / `HTTPS_PROXY`
