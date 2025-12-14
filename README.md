# 🎙️ VoxCPM Docker - 高质量中文语音合成

[English](README_EN.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Hub](https://img.shields.io/docker/v/neosun/voxcpm-allinone?label=Docker%20Hub)](https://hub.docker.com/r/neosun/voxcpm-allinone)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/voxcpm-docker?style=social)](https://github.com/neosun100/voxcpm-docker)

> **生产级 VoxCPM TTS 服务，支持 GPU 加速、OpenAI 兼容 API、自定义音色、流式输出**

## ✨ 核心特性

- 🚀 **OpenAI 兼容 API** - 直接替换 OpenAI TTS，无需改代码
- 🎨 **自定义音色** - 上传音频创建专属音色，支持声音克隆
- ⚡ **流式输出** - PCM 流式播放，首字节延迟 < 0.1s
- 🎯 **高质量合成** - 44.1kHz 16-bit，支持中英文
- 🐳 **一键部署** - Docker 镜像包含所有依赖
- 🔌 **多格式支持** - WAV, MP3, PCM, OPUS, AAC, FLAC

## 🎯 30 秒快速体验

```bash
# 直接播放语音（无需安装）
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好，欢迎使用语音合成", "voice": "alloy", "response_format": "wav"}' \
  | ffplay -autoexit -nodisp -

# 保存为文件
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好世界", "voice": "alloy", "response_format": "wav"}' \
  -o hello.wav
```

## 🐳 Docker 部署

### 方式一：Docker Run

```bash
docker pull neosun/voxcpm-allinone:latest

docker run -d \
  --name voxcpm \
  --gpus all \
  -p 7861:7861 \
  -v ./voices:/app/voices \
  -v ./outputs:/app/outputs \
  --restart unless-stopped \
  neosun/voxcpm-allinone:latest
```

### 方式二：Docker Compose

```yaml
version: '3.8'
services:
  voxcpm:
    image: neosun/voxcpm-allinone:latest
    container_name: voxcpm
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "7861:7861"
    volumes:
      - ./voices:/app/voices
      - ./outputs:/app/outputs
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## 📡 API 使用

### 语音合成

```bash
# WAV 格式
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "wav"}' \
  -o speech.wav

# MP3 格式
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "mp3"}' \
  -o speech.mp3

# PCM 流式（最低延迟）
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "pcm"}' \
  | ffplay -f s16le -ar 44100 -ac 1 -autoexit -nodisp -
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 否 | `tts-1`(快速), `tts-1-hd`(高质量), `gpt-4o-mini-tts` |
| `input` | string | 是 | 要合成的文本（最大4096字符） |
| `voice` | string | 否 | 预设音色或自定义 voice_id |
| `response_format` | string | 否 | `wav`, `mp3`, `pcm`, `opus`, `aac`, `flac` |
| `speed` | float | 否 | 语速 0.25-4.0，默认 1.0 |

### 预设音色

`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ash`, `ballad`, `coral`, `sage`, `verse`

## 🎨 自定义音色

### 1. 上传音频创建音色

```bash
curl -X POST http://localhost:7861/v1/voices/create \
  -F "audio=@your_voice.wav" \
  -F "name=我的音色" \
  -F "text=音频对应的文本内容"
```

**响应：**
```json
{
  "success": true,
  "voice_id": "20cfdc63ddf8",
  "name": "我的音色",
  "message": "音色创建成功，使用 voice='20cfdc63ddf8' 调用 /v1/audio/speech"
}
```

### 2. 使用自定义音色

```bash
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "20cfdc63ddf8", "response_format": "wav"}' \
  -o output.wav
```

### 3. 管理音色

```bash
# 列出所有自定义音色
curl -s http://localhost:7861/v1/voices/custom | jq .

# 获取音色详情
curl -s http://localhost:7861/v1/voices/20cfdc63ddf8 | jq .

# 删除音色
curl -X DELETE http://localhost:7861/v1/voices/20cfdc63ddf8
```

## 🌊 流式播放

### 命令行

```bash
# WAV 流式播放
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好世界", "voice": "alloy", "response_format": "wav"}' \
  | ffplay -autoexit -nodisp -

# 使用 aplay（Linux）
curl -s http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好", "voice": "alloy", "response_format": "wav"}' \
  | aplay
```

### Web 前端

使用 Web Audio API 实现 PCM 流式播放，边生成边播放，无需等待完整音频。

## 📊 API 端点一览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/speech` | POST | 语音合成（支持流式） |
| `/v1/voices/create` | POST | 上传音频创建自定义音色 |
| `/v1/voices/custom` | GET | 列出所有自定义音色 |
| `/v1/voices/{voice_id}` | GET | 获取音色详情 |
| `/v1/voices/{voice_id}` | DELETE | 删除自定义音色 |
| `/v1/models` | GET | 列出可用模型 |
| `/v1/voices` | GET | 列出预设音色 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger API 文档 |

## ⚡ 性能指标

| 指标 | 数值 |
|------|------|
| PCM 首字节延迟 | ~0.001s |
| WAV 首字节延迟 | ~0.09s |
| 生成速度 | 2-8s（取决于文本长度） |
| 音频质量 | 44.1kHz, 16-bit PCM |
| GPU 显存占用 | ~2.1GB |

## 🔗 在线服务

| 服务 | 地址 |
|------|------|
| API 服务 | https://voxcpm-tts.aws.xin |
| API 文档 | https://voxcpm-tts.aws.xin/docs |

## 📝 版本历史

### v1.4.0 (2025-12-14) - 自定义音色
- ✅ **自定义音色 API** - 上传音频创建专属音色
- ✅ 音色管理（创建/列表/详情/删除）
- ✅ 支持 voice_id 调用自定义音色
- ✅ 完整 API 文档

### v1.3.1 (2025-12-14) - 音频质量优化
- ⚡ 消除开头杂音（DC offset 去除 + 淡入效果）
- ⚡ 优化流式播放（500ms 缓冲 + 时间同步）
- ⚡ 防止音频重叠播放

### v1.3.0 (2025-12-14) - 流式播放
- 🌊 PCM 真流式输出（首字节 0.001s）
- 🌊 Web Audio API 前端播放
- 🌊 字节对齐修复

### v1.2.0 (2025-12-14) - 性能优化
- ⚡ 64% 延迟降低（0.25s → 0.09s）
- ⚡ 43% 总时间优化
- ⚡ WAV 头修复

### v1.1.0 (2025-12-13) - OpenAI 兼容
- ✅ OpenAI 兼容 `/v1/audio/speech` 端点
- ✅ 11 个预设音色
- ✅ 6 种音频格式
- ✅ 流式音频生成

### v1.0.0 (2025-12-12) - 初始版本
- ✅ All-in-one Docker 镜像
- ✅ FastAPI REST API
- ✅ Gradio Web UI
- ✅ GPU 自动管理

## 🛠️ 系统要求

- Docker 20.10+
- NVIDIA GPU（CUDA 12.1+）
- NVIDIA Docker Runtime
- 4GB+ GPU 显存

## 📄 许可证

Apache License 2.0

## 🙏 致谢

- [VoxCPM](https://github.com/OpenBMB/VoxCPM) - 原始 TTS 模型
- [OpenBMB](https://github.com/OpenBMB) - 模型开发

---

**Made with ❤️ by the VoxCPM Community**
