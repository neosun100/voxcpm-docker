# 🎙️ VoxCPM Docker 部署

[English](README_EN.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Hub](https://img.shields.io/docker/v/neosun/voxcpm-allinone?label=Docker%20Hub)](https://hub.docker.com/r/neosun/voxcpm-allinone)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/OpenBMB/VoxCPM?style=social)](https://github.com/OpenBMB/VoxCPM)

> **生產級 VoxCPM TTS 服務 Docker 部署方案，支援 GPU、REST API、Web UI 和 MCP 協議整合。**

## 📸 介面預覽

![VoxCPM Web UI](docs/images/ui-screenshot.png)

## ✨ 功能特性

- 🚀 **一鍵部署** - 單一 Docker 映像包含所有依賴
- 🎨 **Gradio Web UI** - 友善的語音合成和克隆介面
- 🔌 **REST API** - 完整的 API，支援 12 個 VoxCPM 參數
- 🤖 **MCP 協議** - 模型上下文協議整合，支援 AI 助手
- 🎯 **GPU 自動管理** - 自動載入/卸載模型，支援閒置逾時
- 💾 **持久化儲存** - 音訊檔案儲存到主機目錄
- 🔒 **HTTPS 支援** - Nginx 反向代理，支援 SSL/TLS
- 📊 **健康監控** - 內建健康檢查和狀態端點
- 🌐 **公網存取** - 網域：https://voxcpm-tts.aws.xin

## 🎯 快速開始

### 方式一：Docker Run（推薦）

```bash
# 拉取映像
docker pull neosun/voxcpm-allinone:1.0.8

# 執行容器
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
```

啟動服務：
```bash
docker-compose up -d
```

## 🌐 存取位址

| 服務 | URL | 說明 |
|------|-----|------|
| Web UI | http://localhost:7861 | Gradio 介面 |
| API 文件 | http://localhost:7861/docs | Swagger UI |
| 健康檢查 | http://localhost:7861/health | 服務狀態 |
| GPU 狀態 | http://localhost:7861/api/gpu/status | GPU 資訊 |
| 公網位址 | https://voxcpm-tts.aws.xin | HTTPS 存取 |

## 📦 安裝部署

### 前置需求

- Docker 20.10+
- Docker Compose 1.29+（選用）
- NVIDIA GPU，支援 CUDA 12.1
- NVIDIA Docker Runtime

## 🎨 使用範例

### REST API

#### 文字轉語音

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=你好，我是 VoxCPM。" \
  -F "cfg_value=2.0" \
  -F "inference_timesteps=10" \
  -o output.wav
```

#### 語音克隆

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=這是克隆的聲音。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=參考文字" \
  -F "cfg_value=2.0" \
  -o cloned.wav
```

## 🛠️ 技術棧

- **基礎映像**: nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
- **Python**: 3.10
- **PyTorch**: 2.5.1+cu121
- **VoxCPM**: 1.5
- **FastAPI**: 最新版
- **Gradio**: 最新版

## 📈 效能指標

| 指標 | 數值 |
|------|------|
| 映像大小 | 17.2GB |
| 容器啟動 | ~15 秒 |
| 首次生成 | ~110 秒（含模型載入） |
| 後續生成 | ~24 秒 |
| GPU 顯存 | 2.14GB（模型已載入） |
| 音訊品質 | 44.1kHz, 16-bit PCM |

## 📄 授權

本專案採用 Apache License 2.0 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=OpenBMB/VoxCPM&type=Date)](https://star-history.com/#OpenBMB/VoxCPM)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**用 ❤️ 打造 by VoxCPM 社群**
