# 🎉 VoxCPM Docker 部署 - 从这里开始

## 🚀 三步启动

### 第 1 步：启动服务
```bash
./start.sh
```

### 第 2 步：等待启动
首次启动需要下载模型（约 3GB），请耐心等待 2-5 分钟。

### 第 3 步：访问服务
- **UI 界面**: http://localhost:7861
- **API 文档**: http://localhost:7861/apidocs

## 🎯 三种使用方式

### 1️⃣ Web UI（最简单）
打开浏览器 → http://localhost:7861 → 输入文本 → 点击合成

### 2️⃣ REST API（适合集成）
```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=你好，我是 VoxCPM" \
  --output output.wav
```

### 3️⃣ MCP（适合 AI Agent）
详见 [MCP_GUIDE.md](MCP_GUIDE.md)

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 快速上手指南 |
| [README_DOCKER.md](README_DOCKER.md) | 完整部署文档 |
| [MCP_GUIDE.md](MCP_GUIDE.md) | MCP 使用说明 |
| [CHECKLIST.md](CHECKLIST.md) | 部署检查清单 |

## 🧪 测试验证

```bash
# 运行自动化测试
./test_deployment.sh
```

## 🛠️ 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

## 🆘 遇到问题？

1. **端口被占用**: 修改 `.env` 中的 `PORT`
2. **GPU 内存不足**: 降低 `inference_timesteps` 到 5
3. **模型下载慢**: 首次启动需要时间，请耐心等待

详见 [README_DOCKER.md](README_DOCKER.md) 的故障排除章节。

## ✨ 特性亮点

- ✅ **自动 GPU 选择** - 自动选择显存占用最少的 GPU
- ✅ **三种访问模式** - UI、API、MCP 三合一
- ✅ **智能显存管理** - 空闲 60 秒自动释放显存
- ✅ **一键启动** - 零配置快速部署
- ✅ **完整文档** - 中文文档，详细说明

## 🎊 开始使用

```bash
./start.sh
```

然后访问 http://localhost:7861 开始体验！

---

**项目主页**: https://github.com/OpenBMB/VoxCPM
