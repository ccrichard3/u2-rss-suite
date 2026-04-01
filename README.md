# u2-rss-suite

把两套 U2 RSS 脚本整理成可直接发 GitHub、可在新设备快速部署的方案。

## 包含项目
- `u2-catchmagic-rss/`
  - 抓 U2 魔法种子
  - 输出 RSS 给 Vertex / autobrr
- `u2-newtorrents-rss/`
  - 抓 U2 新种
  - 输出 RSS 给 Vertex 统一接管后续下载

## 推荐链路

`U2 页面 -> RSS 服务 -> Vertex -> qBittorrent / 其他下载器`

这样脚本只负责“发现 + 输出 RSS”，后续下载、分类、限速、客户端控制统一放在 Vertex。

## 新设备部署

### 方式一：作为一个仓库整体上传
```bash
git clone <your-repo>
cd u2-rss-suite
```

然后分别部署：

```bash
cd u2-catchmagic-rss
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

```bash
cd ../u2-newtorrents-rss
cp .env.example .env
# 编辑 .env
docker compose up -d --build
```

### 方式二：拆成两个独立仓库
- 一个仓库放 `u2-catchmagic-rss`
- 一个仓库放 `u2-newtorrents-rss`

如果你后面想单独维护版本，这种方式更清晰。

## 已整理内容
- 去掉真实密钥 / cookie / passkey
- 改成环境变量配置
- Docker 化
- 带 `.env.example`
- 带 `docker-compose.yml`
- 带单独 README

## 本地已做检查
- Python 语法编译通过
- 清理 `__pycache__` 后可直接作为 GitHub 目录使用
