# VoxCPM Docker 部署指南

## 🚀 快速开始

### 一键启动

```bash
./start.sh
```

脚本会自动：
1. ✅ 检测 NVIDIA GPU 环境
2. ✅ 选择显存占用最少的 GPU
3. ✅ 检查端口可用性
4. ✅ 启动 Docker 容器

### 访问服务

启动后可通过以下方式访问：

- **UI 界面**: http://0.0.0.0:7861
- **API 文档**: http://0.0.0.0:7861/apidocs
- **MCP 服务**: 使用 `mcp_client.json` 配置

## 📦 三种访问模式

### 1. UI 界面模式

访问 http://0.0.0.0:7861 使用 Web 界面：

**功能：**
- 🎤 **语音合成**：输入文本生成语音
- 🎭 **声音克隆**：上传参考音频克隆声音
- ⚙️ **参数调节**：调整 CFG、推理步数等
- 🖥️ **GPU 监控**：实时查看 GPU 状态

### 2. API 模式

#### 健康检查
```bash
curl http://localhost:7861/health
```

#### 文本转语音
```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=Hello, this is VoxCPM" \
  -F "cfg_value=2.0" \
  -F "inference_timesteps=10" \
  --output output.wav
```

#### 声音克隆
```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=Cloned voice speaking" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=Reference transcript" \
  --output cloned.wav
```

#### GPU 状态
```bash
curl http://localhost:7861/api/gpu/status
```

#### 卸载模型
```bash
curl -X POST http://localhost:7861/api/gpu/offload
```

### 3. MCP 模式

详见 [MCP_GUIDE.md](MCP_GUIDE.md)

**配置 MCP 客户端：**
```json
{
  "mcpServers": {
    "voxcpm": {
      "command": "python3",
      "args": ["/home/neo/upload/VoxCPM/mcp_server.py"],
      "env": {
        "GPU_IDLE_TIMEOUT": "600"
      }
    }
  }
}
```

**使用示例：**
```python
# 文本转语音
result = await mcp_client.call_tool(
    "text_to_speech",
    {"text": "Hello from MCP"}
)

# 声音克隆
result = await mcp_client.call_tool(
    "voice_cloning",
    {
        "text": "Cloned voice",
        "reference_audio": "/path/to/ref.wav"
    }
)
```

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
PORT=7861                    # 服务端口
GPU_IDLE_TIMEOUT=60         # GPU 空闲超时（秒）
NVIDIA_VISIBLE_DEVICES=0    # GPU ID
HF_REPO_ID=openbmb/VoxCPM1.5  # 模型 ID
```

### 参数说明

| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| cfg_value | 0.5-5.0 | 2.0 | 引导强度，越高越贴近提示 |
| inference_timesteps | 5-20 | 10 | 推理步数，越高质量越好但越慢 |
| normalize | bool | false | 文本规范化 |
| denoise | bool | false | 音频降噪 |

## 🛠️ 管理命令

### 查看日志
```bash
docker-compose logs -f
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 重新构建
```bash
docker-compose up -d --build
```

### 进入容器
```bash
docker exec -it voxcpm-service bash
```

## 📊 GPU 管理

### 自动管理

服务内置 GPU 管理器，会自动：
- ✅ 空闲 60 秒后自动卸载模型
- ✅ 需要时自动加载模型
- ✅ 释放 GPU 显存

### 手动管理

**通过 API：**
```bash
# 查看状态
curl http://localhost:7861/api/gpu/status

# 强制卸载
curl -X POST http://localhost:7861/api/gpu/offload
```

**通过 UI：**
- 访问 "GPU Status" 标签页
- 点击 "Offload Model" 按钮

**通过 MCP：**
```python
await mcp_client.call_tool("offload_model", {})
```

## 🔧 故障排除

### 端口被占用

修改 `.env` 中的 `PORT` 值：
```bash
PORT=7862
```

### GPU 内存不足

1. 降低 `inference_timesteps`
2. 手动卸载模型
3. 增加 `GPU_IDLE_TIMEOUT` 使模型更快卸载

### 模型下载慢

首次启动需要下载模型（约 3GB），可以：
1. 使用国内镜像源
2. 预先下载模型到 `./models` 目录

### 容器无法启动

检查 nvidia-docker：
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## 📈 性能优化

### 推荐配置

| 场景 | cfg_value | inference_timesteps | 说明 |
|------|-----------|---------------------|------|
| 快速预览 | 1.5 | 5 | 最快，质量较低 |
| 平衡模式 | 2.0 | 10 | 推荐，速度与质量平衡 |
| 高质量 | 2.5 | 15 | 最佳质量，较慢 |

### RTF (Real-Time Factor)

- RTX 4090: ~0.15
- RTX 3090: ~0.25
- RTX 3080: ~0.30

## 🔒 安全建议

1. **生产环境**：修改端口绑定从 `0.0.0.0` 到 `127.0.0.1`
2. **API 认证**：添加 API Key 验证
3. **文件上传**：限制上传文件大小和类型
4. **速率限制**：添加请求频率限制

## 📝 更新日志

### v1.0.0 (2025-12-12)
- ✅ 初始 Docker 化版本
- ✅ 支持 UI + API + MCP 三种模式
- ✅ 自动 GPU 管理
- ✅ 多语言支持

## 🆘 获取帮助

- GitHub Issues: https://github.com/OpenBMB/VoxCPM/issues
- 技术文档: [README.md](README.md)
- MCP 指南: [MCP_GUIDE.md](MCP_GUIDE.md)
