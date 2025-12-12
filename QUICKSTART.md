# VoxCPM 快速启动指南

## 🚀 30 秒启动

```bash
# 1. 一键启动
./start.sh

# 2. 访问服务
# UI:  http://localhost:7861
# API: http://localhost:7861/apidocs
```

## 📋 三种使用方式

### 方式 1️⃣: Web UI（最简单）

1. 打开浏览器访问 http://localhost:7861
2. 在 "Voice Synthesis" 标签页输入文本
3. 点击 "Synthesize" 生成语音
4. 在 "Voice Cloning" 标签页上传参考音频克隆声音

### 方式 2️⃣: REST API（适合集成）

```bash
# 文本转语音
curl -X POST http://localhost:7861/api/tts \
  -F "text=你好，我是 VoxCPM" \
  -F "cfg_value=2.0" \
  --output output.wav

# 声音克隆
curl -X POST http://localhost:7861/api/tts \
  -F "text=克隆的声音" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考文本" \
  --output cloned.wav
```

### 方式 3️⃣: MCP（适合 AI Agent）

```python
# 配置 MCP 客户端后
result = await mcp_client.call_tool(
    "text_to_speech",
    {"text": "Hello from MCP"}
)
```

详见 [MCP_GUIDE.md](MCP_GUIDE.md)

## ⚙️ 常用参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| cfg_value | 2.0 | 引导强度，越高越贴近提示 |
| inference_timesteps | 10 | 推理步数，越高质量越好 |

## 🛠️ 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 或使用 Makefile
make start   # 启动
make stop    # 停止
make logs    # 查看日志
make test    # 运行测试
```

## 🔧 故障排除

### 端口被占用
修改 `.env` 中的 `PORT=7862`

### GPU 内存不足
降低 `inference_timesteps` 到 5

### 模型下载慢
首次启动需要下载约 3GB 模型，请耐心等待

## 📚 更多文档

- [完整部署文档](README_DOCKER.md)
- [MCP 使用指南](MCP_GUIDE.md)
- [项目主页](README.md)

## 🆘 获取帮助

遇到问题？
1. 查看日志: `docker-compose logs -f`
2. 运行测试: `./test_deployment.sh`
3. 提交 Issue: https://github.com/OpenBMB/VoxCPM/issues
