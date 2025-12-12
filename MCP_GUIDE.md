# VoxCPM MCP Server Guide

## 概述

VoxCPM MCP Server 提供了程序化访问 VoxCPM TTS 功能的接口，基于 Model Context Protocol (MCP) 标准。

## 可用工具

### 1. text_to_speech

将文本转换为语音。

**参数：**
- `text` (string, required): 要合成的文本
- `output_path` (string, optional): 输出文件路径，不提供则自动生成
- `cfg_value` (float, optional): 引导强度 (0.5-5.0, 默认: 2.0)
- `inference_timesteps` (int, optional): 推理步数 (5-20, 默认: 10)
- `min_len` (int, optional): 最小 token 长度 (默认: 2)
- `max_len` (int, optional): 最大 token 长度 (默认: 4096)
- `normalize` (bool, optional): 启用文本规范化
- `denoise` (bool, optional): 启用音频降噪
- `retry_badcase` (bool, optional): 启用坏情况重试 (默认: True)
- `retry_badcase_max_times` (int, optional): 最大重试次数 (默认: 3)
- `retry_badcase_ratio_threshold` (float, optional): 音频文本比率阈值 (默认: 6.0)

**返回：**
```json
{
  "status": "success",
  "output_path": "/path/to/output.wav",
  "sample_rate": 44100
}
```

**使用示例：**
```python
# 基础使用
result = await mcp_client.call_tool(
    "text_to_speech",
    {
        "text": "Hello, this is VoxCPM speaking.",
        "cfg_value": 2.0,
        "inference_timesteps": 10
    }
)

# 高级使用（所有参数）
result = await mcp_client.call_tool(
    "text_to_speech",
    {
        "text": "Advanced text-to-speech synthesis.",
        "output_path": "/path/to/output.wav",
        "cfg_value": 2.5,
        "inference_timesteps": 15,
        "min_len": 2,
        "max_len": 4096,
        "normalize": True,
        "denoise": False,
        "retry_badcase": True,
        "retry_badcase_max_times": 5,
        "retry_badcase_ratio_threshold": 6.0
    }
)
```

### 2. voice_cloning

使用参考音频克隆声音并合成新文本。

**参数：**
- `text` (string, required): 要合成的文本
- `reference_audio` (string, required): 参考音频文件路径
- `reference_text` (string, optional): 参考音频的文本转录
- `output_path` (string, optional): 输出文件路径
- `cfg_value` (float, optional): 引导强度 (默认: 2.0)
- `inference_timesteps` (int, optional): 推理步数 (默认: 10)
- `min_len` (int, optional): 最小 token 长度 (默认: 2)
- `max_len` (int, optional): 最大 token 长度 (默认: 4096)
- `normalize` (bool, optional): 启用文本规范化
- `denoise` (bool, optional): 启用参考音频降噪
- `retry_badcase` (bool, optional): 启用坏情况重试 (默认: True)
- `retry_badcase_max_times` (int, optional): 最大重试次数 (默认: 3)
- `retry_badcase_ratio_threshold` (float, optional): 音频文本比率阈值 (默认: 6.0)

**返回：**
```json
{
  "status": "success",
  "output_path": "/path/to/cloned.wav",
  "sample_rate": 44100
}
```

**使用示例：**
```python
# 基础使用
result = await mcp_client.call_tool(
    "voice_cloning",
    {
        "text": "This is cloned voice speaking.",
        "reference_audio": "/path/to/reference.wav",
        "reference_text": "Original transcript"
    }
)

# 高级使用（所有参数）
result = await mcp_client.call_tool(
    "voice_cloning",
    {
        "text": "Advanced voice cloning with all parameters.",
        "reference_audio": "/path/to/reference.wav",
        "reference_text": "Reference transcript",
        "output_path": "/path/to/cloned.wav",
        "cfg_value": 2.5,
        "inference_timesteps": 15,
        "min_len": 2,
        "max_len": 4096,
        "normalize": True,
        "denoise": True,
        "retry_badcase": True,
        "retry_badcase_max_times": 5,
        "retry_badcase_ratio_threshold": 6.0
    }
)
```

### 3. get_gpu_status

获取当前 GPU 状态和内存使用情况。

**参数：** 无

**返回：**
```json
{
  "status": "success",
  "model_loaded": true,
  "memory_allocated_gb": 3.45,
  "memory_reserved_gb": 4.00,
  "device_name": "NVIDIA GeForce RTX 4090"
}
```

**使用示例：**
```python
status = await mcp_client.call_tool("get_gpu_status", {})
```

### 4. offload_model

强制从 GPU 卸载模型以释放显存。

**参数：** 无

**返回：**
```json
{
  "status": "success",
  "message": "Model offloaded from GPU"
}
```

**使用示例：**
```python
result = await mcp_client.call_tool("offload_model", {})
```

## 配置

### MCP 客户端配置

将以下配置添加到你的 MCP 客户端配置文件（如 `~/.config/mcp/config.json`）：

```json
{
  "mcpServers": {
    "voxcpm": {
      "command": "python3",
      "args": ["/home/neo/upload/VoxCPM/mcp_server.py"],
      "env": {
        "GPU_IDLE_TIMEOUT": "600",
        "HF_REPO_ID": "openbmb/VoxCPM1.5",
        "CUDA_VISIBLE_DEVICES": "0"
      }
    }
  }
}
```

### 环境变量

- `GPU_IDLE_TIMEOUT`: GPU 空闲超时时间（秒），默认 600
- `HF_REPO_ID`: Hugging Face 模型 ID，默认 `openbmb/VoxCPM1.5`
- `CUDA_VISIBLE_DEVICES`: 使用的 GPU ID

## MCP vs API 对比

| 特性 | MCP | REST API |
|------|-----|----------|
| 访问方式 | 程序化调用 | HTTP 请求 |
| 适用场景 | AI Agent、自动化脚本 | Web 应用、移动应用 |
| 连接方式 | 进程间通信 | 网络请求 |
| 性能 | 更快（本地） | 较慢（网络开销） |
| 文档 | 工具函数注解 | Swagger UI |

## 使用建议

1. **长时间运行任务**：MCP 服务器会自动管理 GPU 内存，空闲时自动卸载模型
2. **批量处理**：连续调用工具时，模型会保持加载状态，提高效率
3. **错误处理**：所有工具都会返回 `status` 字段，检查是否为 `"success"`
4. **GPU 管理**：定期调用 `get_gpu_status` 监控显存使用，必要时调用 `offload_model`

## 故障排除

### 模型加载失败

检查环境变量 `HF_REPO_ID` 是否正确，确保有网络连接下载模型。

### GPU 内存不足

调用 `offload_model` 释放显存，或降低 `inference_timesteps` 参数。

### 工具调用超时

增加 MCP 客户端的超时设置，首次调用需要下载模型可能较慢。
