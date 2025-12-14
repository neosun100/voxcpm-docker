# VoxCPM API 使用指南

## 🎯 快速开始

### 基础语音合成
```bash
# 生成 WAV 并保存
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好世界", "voice": "alloy", "response_format": "wav"}' \
  -o output.wav

# 生成并直接播放（Linux）
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好世界", "voice": "alloy", "response_format": "wav"}' \
  | ffplay -autoexit -nodisp -
```

## 📡 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/speech` | POST | 语音合成（支持流式） |
| `/v1/voices/create` | POST | 上传音频创建自定义音色 |
| `/v1/voices/custom` | GET | 列出所有自定义音色 |
| `/v1/voices/{voice_id}` | GET | 获取音色详情 |
| `/v1/voices/{voice_id}` | DELETE | 删除自定义音色 |
| `/v1/models` | GET | 列出可用模型 |
| `/v1/voices` | GET | 列出预设音色 |

## 🎤 语音合成 API

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 否 | 模型：`tts-1`(快速), `tts-1-hd`(高质量), `gpt-4o-mini-tts` |
| `input` | string | 是 | 要合成的文本（最大4096字符） |
| `voice` | string | 否 | 预设音色或自定义 voice_id |
| `response_format` | string | 否 | 输出格式：`wav`, `mp3`, `pcm`, `opus`, `aac`, `flac` |
| `speed` | float | 否 | 语速：0.25-4.0，默认1.0 |

### 预设音色
`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ash`, `ballad`, `coral`, `sage`, `verse`

### 示例

```bash
# WAV 格式
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "wav"}' \
  -o speech.wav

# MP3 格式
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "mp3"}' \
  -o speech.mp3

# PCM 流式（最低延迟）
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "alloy", "response_format": "pcm"}' \
  -o speech.pcm

# PCM 转 WAV
ffmpeg -f s16le -ar 44100 -ac 1 -i speech.pcm speech.wav
```

## 🎨 自定义音色 API

### 1. 创建自定义音色

上传参考音频，获取 voice_id：

```bash
curl -X POST https://voxcpm-tts.aws.xin/v1/voices/create \
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
# 使用自定义 voice_id
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "20cfdc63ddf8", "response_format": "wav"}' \
  -o output.wav

# 直接播放
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "让子弹飞一会儿", "voice": "20cfdc63ddf8", "response_format": "wav"}' \
  | ffplay -autoexit -nodisp -
```

### 3. 列出自定义音色

```bash
curl -s https://voxcpm-tts.aws.xin/v1/voices/custom | jq .
```

**响应：**
```json
{
  "voices": [
    {
      "id": "20cfdc63ddf8",
      "name": "张麻子",
      "text": "翻译翻译，什么叫惊喜",
      "created_at": 1765726976
    }
  ]
}
```

### 4. 获取音色详情

```bash
curl -s https://voxcpm-tts.aws.xin/v1/voices/20cfdc63ddf8 | jq .
```

### 5. 删除自定义音色

```bash
curl -X DELETE https://voxcpm-tts.aws.xin/v1/voices/20cfdc63ddf8
```

## 🌊 流式播放

### Web 前端（PCM 流式）

访问测试页面：**https://mytts.aws.xin**

### 命令行流式播放

```bash
# WAV 流式播放
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好，这是流式语音测试", "voice": "alloy", "response_format": "wav"}' \
  | ffplay -autoexit -nodisp -

# 使用 aplay（Linux）
curl -s https://voxcpm-tts.aws.xin/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "你好", "voice": "alloy", "response_format": "wav"}' \
  | aplay
```

## 🐳 Docker 部署

```bash
# 拉取镜像
docker pull neosun/voxcpm-allinone:latest

# 运行
docker run -d \
  --name voxcpm \
  --gpus all \
  -p 7861:7861 \
  -v ./voices:/app/voices \
  -v ./outputs:/app/outputs \
  neosun/voxcpm-allinone:latest
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| PCM 首字节延迟 | ~0.001s |
| WAV 首字节延迟 | ~0.09s |
| 生成速度 | ~2-8s（取决于文本长度） |
| 音频质量 | 44.1kHz, 16-bit PCM |

## 🔗 相关链接

- 流式测试页面：https://mytts.aws.xin
- API 文档：https://voxcpm-tts.aws.xin/docs
- Docker Hub：https://hub.docker.com/r/neosun/voxcpm-allinone
- GitHub：https://github.com/neosun100/voxcpm-docker
