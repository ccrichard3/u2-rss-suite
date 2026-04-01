# U2-CatchMagic-RSS

中文 | [English](#english)

把 U2 魔法种子列表转换成 RSS，供 Vertex / autobrr 等工具订阅。

## 功能

- 扫描 U2 魔法页面
- 根据脚本规则筛选可用项目
- 输出标准 RSS：`/rss.xml`
- 不直接下载实体 `.torrent`

## 部署

```bash
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

如果修改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

默认访问地址：

- `http://<IP>:8787/`
- `http://<IP>:8787/rss.xml`

## Vertex 使用

- 在 Vertex 新建 RSS 订阅
- RSS 地址填写：`http://<IP>:8787/rss.xml`
- 勾选“推送种子文件”
- 由 Vertex 使用你的 U2 凭据发起下载

## 重要变量

- `U2_COOKIE`: U2 cookie，支持直接填 `nexusphp_u2=...` 或只填值
- `UID`: 你的 U2 UID
- `API_TOKEN`: 可选；不填时直接抓网页
- `INTERVAL`: 扫描周期，单位秒
- `MAX_SEEDER_NUM`: 最大做种人数限制
- `DOWNLOAD_OLD` / `DOWNLOAD_NEW`: 旧种 / 新种开关
- `RSS_HTTP_PORT`: RSS 服务端口

## 数据目录

- `./data/catch_magic.log`
- `./data/catch_magic.data.txt`
- `./data/rss.xml`

## 说明

- 这个项目更适合与 Vertex 配套使用
- 脚本负责筛选和输出 RSS，不直接接管下载器
- 如需代理，可在 `.env` 中配置 `HTTP_PROXY` / `HTTPS_PROXY`

---

## English

Convert U2 promotion / magic entries into an RSS feed for Vertex, autobrr, or similar tools.

## Features

- Scans the U2 promotion / magic page
- Filters entries based on the script rules
- Exposes a standard RSS feed at `/rss.xml`
- Does not directly download `.torrent` files

## Deployment

```bash
cp .env.example .env
# edit .env
docker compose up -d --build
```

If you change `RSS_HTTP_PORT`, `docker-compose.yml` will map the same port automatically.

Default URLs:

- `http://<IP>:8787/`
- `http://<IP>:8787/rss.xml`

## Using with Vertex

- Create a new RSS subscription in Vertex
- Set the feed URL to `http://<IP>:8787/rss.xml`
- Enable torrent pushing in Vertex
- Let Vertex use your U2 credentials to fetch downloads

## Important variables

- `U2_COOKIE`: U2 cookie; accepts either `nexusphp_u2=...` or the raw value
- `UID`: your U2 user ID
- `API_TOKEN`: optional; if empty, the script falls back to page scraping
- `INTERVAL`: scan interval in seconds
- `MAX_SEEDER_NUM`: maximum seeder threshold
- `DOWNLOAD_OLD` / `DOWNLOAD_NEW`: old / new promotion switches
- `RSS_HTTP_PORT`: HTTP port for the RSS service

## Data files

- `./data/catch_magic.log`
- `./data/catch_magic.data.txt`
- `./data/rss.xml`

## Notes

- This project works best when paired with Vertex
- The script focuses on filtering and RSS generation, not download-client control
- Proxy settings can be provided through `HTTP_PROXY` / `HTTPS_PROXY`
