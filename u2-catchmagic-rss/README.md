# U2-CatchMagic-RSS

把 U2 魔法种子转成 RSS，给 Vertex / autobrr 等工具订阅。

## 功能
- 扫描 U2 魔法页
- 按规则筛选
- 输出标准 RSS (`/rss.xml`)
- 不直接下载实体 `.torrent`

## 部署
```bash
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

如果改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

访问：
- `http://<IP>:8787/`
- `http://<IP>:8787/rss.xml`

## Vertex 使用
- 新增 RSS 订阅
- 地址填：`http://<IP>:8787/rss.xml`
- 勾选 `推送种子文件`
- 填写 U2 cookie

## 重要变量
- `U2_COOKIE`: U2 cookie，支持直接填 `nexusphp_u2=...` 或只填值
- `UID`: 你的 U2 UID
- `API_TOKEN`: 可选，不填则直接抓网页
- `MAX_SEEDER_NUM`: 最大做种人数
- `DOWNLOAD_OLD` / `DOWNLOAD_NEW`: 旧种/新种开关
- `RSS_HTTP_PORT`: RSS 端口

## 数据目录
- `./data/catch_magic.log`
- `./data/catch_magic.data.txt`
- `./data/rss.xml`
