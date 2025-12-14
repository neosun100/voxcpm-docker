# 🎵 VoxCPM 流式API使用指南

## 概述

流式API允许音频边生成边返回，大幅降低首字节响应时间，提升用户体验。

## API端点

### 流式端点
```
POST /api/tts/stream
```

### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | ✅ | - | 要合成的文本 |
| prompt_audio | file | ❌ | null | 参考音频（声音克隆） |
| prompt_text | string | ❌ | null | 参考音频文本 |
| cfg_value | float | ❌ | 2.0 | 引导强度 (1.0-5.0) |
| inference_timesteps | int | ❌ | 5 | 推理步数 |
| min_len | int | ❌ | 2 | 最小长度 |
| max_len | int | ❌ | 4096 | 最大长度 |
| normalize | bool | ❌ | false | 文本规范化 |
| denoise | bool | ❌ | false | 音频降噪 |

**注意**: 流式API不支持 `retry_badcase` 参数

## 使用示例

### Python (requests)

```python
import requests

# 基础使用
response = requests.post(
    "http://localhost:7861/api/tts/stream",
    data={
        "text": "你好，这是流式语音合成。",
        "inference_timesteps": 5
    },
    stream=True  # 重要：启用流式接收
)

# 接收音频流
with open("output.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
            print(f"收到 {len(chunk)} 字节")
```

### 声音克隆

```python
# 使用参考音频
with open("reference.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:7861/api/tts/stream",
        data={
            "text": "这是克隆的声音。",
            "prompt_text": "参考音频的文本",
            "inference_timesteps": 5
        },
        files={"prompt_audio": audio_file},
        stream=True
    )
    
    with open("cloned.wav", "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)
```

### curl

```bash
# 基础使用
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=你好世界" \
  -F "inference_timesteps=5" \
  --output stream_output.wav

# 声音克隆
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=克隆的声音" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考文本" \
  --output cloned.wav
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:7861/api/tts/stream', {
    method: 'POST',
    body: new FormData({
        text: '你好，流式合成',
        inference_timesteps: 5
    })
});

const reader = response.body.getReader();
const chunks = [];

while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    chunks.push(value);
    console.log(`收到 ${value.length} 字节`);
}

// 合并音频块
const blob = new Blob(chunks, {type: 'audio/wav'});
```

## 性能对比

### 测试场景
- 文本: "你好，这是VoxCPM流式语音合成测试。"
- 推理步数: 5
- GPU: NVIDIA (CUDA 12.1)

### 结果对比

| 指标 | 普通API | 流式API | 提升 |
|------|---------|---------|------|
| 首字节响应 | ~15-24秒 | ~2-3秒 | **85-90%** ⬆️ |
| 总生成时间 | ~15-24秒 | ~15-24秒 | 相同 |
| 用户体验 | 等待完成 | 边生成边播放 | 显著提升 ✨ |

### 关键优势

1. **首字节延迟降低 85-90%**
   - 普通API: 等待完整生成 (15-24秒)
   - 流式API: 首块音频 2-3秒返回

2. **渐进式播放**
   - 可以边接收边播放
   - 用户无需等待完整生成

3. **更好的交互体验**
   - 实时反馈
   - 降低感知延迟

## 运行测试

### 完整性能测试

```bash
cd /home/neo/upload/VoxCPM
python3 test_streaming_api.py
```

测试内容:
- ✅ 默认语音合成（普通 vs 流式）
- ✅ 声音克隆（普通 vs 流式）
- ✅ 详细性能对比报告

### 快速测试

```bash
python3 quick_test_streaming.py
```

## 注意事项

1. **流式限制**
   - 不支持 `retry_badcase` 参数
   - 音频块按生成顺序返回

2. **客户端要求**
   - 必须支持流式接收 (stream=True)
   - 建议使用 chunk_size=8192

3. **网络考虑**
   - 流式传输对网络稳定性要求较高
   - 建议在稳定网络环境使用

4. **音频格式**
   - 返回格式: WAV (PCM_16)
   - 采样率: 44100 Hz
   - 每个块都是完整的WAV格式

## 故障排查

### 服务未响应
```bash
# 检查服务状态
curl http://localhost:7861/health

# 查看日志
docker logs voxcpm
```

### 首字节延迟仍然很高
- 检查GPU是否已加载模型
- 首次请求需要加载模型 (~15秒)
- 后续请求会快很多

### 音频不完整
- 确保接收所有chunks
- 检查网络连接稳定性
- 增大 chunk_size

## 更多信息

- API文档: http://localhost:7861/docs
- 健康检查: http://localhost:7861/health
- GPU状态: http://localhost:7861/api/gpu/status
