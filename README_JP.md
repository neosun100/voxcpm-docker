# 🎙️ VoxCPM Docker デプロイ

[English](README_EN.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

[![Docker Hub](https://img.shields.io/docker/v/neosun/voxcpm-allinone?label=Docker%20Hub)](https://hub.docker.com/r/neosun/voxcpm-allinone)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/OpenBMB/VoxCPM?style=social)](https://github.com/OpenBMB/VoxCPM)

> **GPU、REST API、Web UI、MCPプロトコル統合をサポートする本番環境対応のVoxCPM TTSサービスDockerデプロイソリューション。**

## ✨ 機能

- 🚀 **ワンクリックデプロイ** - すべての依存関係を含む単一のDockerイメージ
- 🎨 **Gradio Web UI** - 音声合成とクローニングのための使いやすいインターフェース
- 🔌 **REST API** - 12のVoxCPMパラメータをサポートする完全なAPI
- 🤖 **MCPプロトコル** - AIアシスタント用のモデルコンテキストプロトコル統合
- 🎯 **GPU自動管理** - アイドルタイムアウトによるモデルの自動ロード/アンロード
- 💾 **永続ストレージ** - ホストディレクトリへのオーディオファイル保存
- 🔒 **HTTPS対応** - SSL/TLS対応のNginxリバースプロキシ
- 📊 **ヘルスモニタリング** - 組み込みのヘルスチェックとステータスエンドポイント
- 🌐 **パブリックアクセス** - ドメイン：https://voxcpm-tts.aws.xin

## 🎯 クイックスタート

### 方法1：Docker Run（推奨）

```bash
# イメージをプル
docker pull neosun/voxcpm-allinone:1.0.0

# コンテナを実行
docker run -d \
  --name voxcpm \
  --gpus all \
  -p 7861:7861 \
  -v /path/to/uploads:/app/uploads \
  -v /path/to/outputs:/app/outputs \
  --restart unless-stopped \
  neosun/voxcpm-allinone:1.0.0
```

### 方法2：Docker Compose

```yaml
version: '3.8'

services:
  voxcpm:
    image: neosun/voxcpm-allinone:1.0.0
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

サービスを起動：
```bash
docker-compose up -d
```

## 🌐 アクセスポイント

| サービス | URL | 説明 |
|---------|-----|------|
| Web UI | http://localhost:7861 | Gradioインターフェース |
| APIドキュメント | http://localhost:7861/docs | Swagger UI |
| ヘルスチェック | http://localhost:7861/health | サービスステータス |
| GPUステータス | http://localhost:7861/api/gpu/status | GPU情報 |
| パブリックURL | https://voxcpm-tts.aws.xin | HTTPSアクセス |

## 📦 インストール

### 前提条件

- Docker 20.10+
- Docker Compose 1.29+（オプション）
- CUDA 12.1対応のNVIDIA GPU
- NVIDIA Docker Runtime

## 🎨 使用例

### REST API

#### テキスト音声変換

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=こんにちは、VoxCPMです。" \
  -F "cfg_value=2.0" \
  -F "inference_timesteps=10" \
  -o output.wav
```

#### 音声クローニング

```bash
curl -X POST http://localhost:7861/api/tts \
  -F "text=これはクローンされた音声です。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参照テキスト" \
  -F "cfg_value=2.0" \
  -o cloned.wav
```

## 🛠️ 技術スタック

- **ベースイメージ**: nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
- **Python**: 3.10
- **PyTorch**: 2.5.1+cu121
- **VoxCPM**: 1.5
- **FastAPI**: 最新版
- **Gradio**: 最新版

## 📈 パフォーマンス

| 指標 | 値 |
|------|-----|
| イメージサイズ | 17.2GB |
| コンテナ起動 | ~15秒 |
| 初回生成 | ~110秒（モデルロード含む） |
| 以降の生成 | ~24秒 |
| GPUメモリ | 2.14GB（モデルロード後） |
| オーディオ品質 | 44.1kHz, 16-bit PCM |

## 📄 ライセンス

このプロジェクトはApache License 2.0の下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=OpenBMB/VoxCPM&type=Date)](https://star-history.com/#OpenBMB/VoxCPM)

## 📱 フォローする

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**VoxCPMコミュニティによって ❤️ で作成**
