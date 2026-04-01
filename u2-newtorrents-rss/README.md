# U2-NewTorrents-RSS

把 `download_new_torrents.py` 改造成 RSS 输出服务，统一交给 Vertex 控制下载。

## 功能
- 扫描 U2 新种页
- 按脚本规则筛选新种
- 输出标准 RSS (`/rss.xml`)
- Vertex 订阅后再推给 qB / 其他客户端

## 部署
```bash
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

如果改了 `RSS_HTTP_PORT`，`docker-compose.yml` 会自动按同端口映射。

访问：
- `http://<IP>:8788/`
- `http://<IP>:8788/rss.xml`

## Vertex 使用
- 新增 RSS 订阅
- 地址填：`http://<IP>:8788/rss.xml`
- 勾选 `推送种子文件`
- 填写 U2 cookie

## 重要说明
默认 `SKIP_EXISTING_ON_FIRST_RUN=true`：
- 第一次启动只建立基线
- **不会把当前页面已有旧种立刻写入 RSS**
- 所以后续 RSS 可能暂时为空，直到有新种命中规则

如果你想首次启动就把当前命中的项目也塞进 RSS：
```env
SKIP_EXISTING_ON_FIRST_RUN=false
```

## 重要变量
- `U2_COOKIE`: U2 cookie，支持直接填 `nexusphp_u2=...` 或只填值
- `U2_PASSKEY`: 可选；留空时脚本会尝试从详情页解析
- `INTERVAL`: 扫描间隔
- `DOWNLOAD_STICKY` 等变量控制筛选行为
- `RSS_HTTP_PORT`: RSS 端口

## 数据目录
- `./data/service.log`
- `./data/state.json`
- `./data/rss.xml`
