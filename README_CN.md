# 🎙️ VoxCPM Docker 部署

[English](README_EN.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Hub](https://img.shields.io/docker/v/neosun/voxcpm-allinone?label=Docker%20Hub)](https://hub.docker.com/r/neosun/voxcpm-allinone)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/OpenBMB/VoxCPM?style=social)](https://github.com/OpenBMB/VoxCPM)

> **生产级 VoxCPM TTS 服务 Docker 部署方案，支持 GPU、REST API、Web UI 和 MCP 协议集成。**

## ✨ 功能特性

- 🚀 **一键部署** - 单个 Docker 镜像包含所有依赖
- 🎨 **Gradio Web UI** - 友好的语音合成和克隆界面
- 🔌 **REST API** - 完整的 API，支持 12 个 VoxCPM 参数
- 🤖 **MCP 协议** - 模型上下文协议集成，支持 AI 助手
- 🎯 **GPU 自动管理** - 自动加载/卸载模型，支持空闲超时
- 💾 **持久化存储** - 音频文件保存到主机目录
- 🔒 **HTTPS 支持** - Nginx 反向代理，支持 SSL/TLS
- 📊 **健康监控** - 内置健康检查和状态端点
- 🌐 **公网访问** - 域名：https://voxcpm-tts.aws.xin

## 🎯 快速开始

### 方式一：Docker Run（推荐）

```bash
# 拉取镜像
docker pull neosun/voxcpm-allinone:1.0.8

# 运行容器
docker run -d \
  --name voxcpm \
  --gpus all \
  -p 7861:7861 \
  -v /path/to/uploads:/app/uploads \
  -v /path/to/outputs:/app/outputs \
  --restart unless-stopped \
  neosun/voxcpm-allinone:1.0.8
```

### 方式二：Docker Compose

```yaml
version: '3.8'

services:
  voxcpm:
    image: neosun/voxcpm-allinone:1.0.8
    container_name: voxcpm-service
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - PORT=7861
      - GPU_IDLE_TIMEOUT=60
    ports:
      - "7861:7861"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7861/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
```

启动服务：
```bash
docker-compose up -d
```

## 🌐 访问地址

| 服务 | URL | 说明 |
|------|-----|------|
| Web UI | http://localhost:7861 | Gradio 界面 |
| API 文档 | http://localhost:7861/docs | Swagger UI |
| 健康检查 | http://localhost:7861/health | 服务状态 |
| GPU 状态 | http://localhost:7861/api/gpu/status | GPU 信息 |
| 公网地址 | https://voxcpm-tts.aws.xin | HTTPS 访问 |

## 📦 安装部署

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+（可选）
- NVIDIA GPU，支持 CUDA 12.1
- NVIDIA Docker Runtime

### 安装 NVIDIA Docker Runtime

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 验证 GPU 访问

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 7861 | 服务端口 |
| `GPU_IDLE_TIMEOUT` | 60 | GPU 自动卸载超时（秒） |
| `NVIDIA_VISIBLE_DEVICES` | all | GPU 设备选择 |
| `HF_REPO_ID` | openbmb/VoxCPM1.5 | 模型仓库 |

### 卷挂载

| 主机路径 | 容器路径 | 用途 |
|----------|----------|------|
| `./uploads` | `/app/uploads` | 参考音频文件 |
| `./outputs` | `/app/outputs` | 生成的音频文件 |

## 🎨 使用示例

### Web UI

1. 在浏览器中打开 http://localhost:7861
2. 切换到"语音合成"或"语音克隆"标签
3. 输入文本并调整参数
4. 点击"生成"创建音频

### REST API

#### 文本转语音

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=你好，我是 VoxCPM。" \
  -F "cfg_value=2.0" \
  -F "inference_timesteps=10" \
  -o output.wav
```

#### 语音克隆

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=这是克隆的声音。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考文本" \
  -F "cfg_value=2.0" \
  -o cloned.wav
```

#### GPU 状态

```bash
curl http://localhost:7861/api/gpu/status
```

#### GPU 卸载

```bash
curl -X POST http://localhost:7861/api/gpu/offload
```

### MCP 集成

详细集成说明请参考 [MCP_GUIDE.md](MCP_GUIDE.md)。

## 📊 API 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | string | 必填 | 输入文本 |
| `prompt_audio` | file | null | 克隆参考音频 |
| `prompt_text` | string | null | 参考文本 |
| `cfg_value` | float | 2.0 | 引导强度（1.0-5.0） |
| `inference_timesteps` | int | 10 | 推理步数（5-50） |
| `min_len` | int | 2 | 最小长度 |
| `max_len` | int | 4096 | 最大长度 |
| `normalize` | bool | false | 文本规范化 |
| `denoise` | bool | false | 音频降噪 |
| `retry_badcase` | bool | true | 重试机制 |
| `retry_badcase_max_times` | int | 3 | 最大重试次数 |
| `retry_badcase_ratio_threshold` | float | 6.0 | 重试阈值 |

详细参数说明请参考 [PARAMETERS.md](PARAMETERS.md)。

## 🏗️ 项目结构

```
VoxCPM/
├── Dockerfile.allinone      # All-in-one Docker 镜像
├── docker-compose.yml        # Docker Compose 配置
├── server.py                 # FastAPI + Gradio 服务器
├── gpu_manager.py            # GPU 显存管理
├── mcp_server.py             # MCP 协议服务器
├── .env.example              # 环境变量模板
├── docs/                     # 文档
├── examples/                 # 使用示例
└── src/                      # VoxCPM 源代码
```

## 🛠️ 技术栈

- **基础镜像**: nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
- **Python**: 3.10
- **PyTorch**: 2.5.1+cu121
- **VoxCPM**: 1.5
- **FastAPI**: 最新版
- **Gradio**: 最新版
- **Nginx**: 反向代理，支持 SSL/TLS

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 镜像大小 | 17.2GB |
| 容器启动 | ~15 秒 |
| 首次生成 | ~110 秒（含模型加载） |
| 后续生成 | ~24 秒 |
| GPU 显存 | 2.14GB（模型已加载） |
| 音频质量 | 44.1kHz, 16-bit PCM |

## 🔧 故障排查

### 容器无法启动

```bash
# 查看日志
docker logs voxcpm

# 验证 GPU 访问
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 模型加载失败

```bash
# 检查磁盘空间
df -h

# 手动下载模型
docker exec -it voxcpm python3 -c "from huggingface_hub import snapshot_download; snapshot_download('openbmb/VoxCPM1.5')"
```

### 端口已被占用

```bash
# 更改端口映射
docker run -d --name voxcpm --gpus all -p 8080:7861 neosun/voxcpm-allinone:1.0.8
```

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2025-12-12)
- ✅ 初始版本发布
- ✅ All-in-one Docker 镜像
- ✅ FastAPI REST API，支持 12 个参数
- ✅ Gradio Web UI
- ✅ MCP 协议集成
- ✅ GPU 自动管理
- ✅ HTTPS 支持（Nginx）
- ✅ 14/14 测试通过

## 📄 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [VoxCPM](https://github.com/OpenBMB/VoxCPM) - 原始 TTS 模型
- [OpenBMB](https://github.com/OpenBMB) - 模型开发
- [ModelBest](https://modelbest.cn/) - 项目赞助

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=OpenBMB/VoxCPM&type=Date)](https://star-history.com/#OpenBMB/VoxCPM)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**用 ❤️ 打造 by VoxCPM 社区**
