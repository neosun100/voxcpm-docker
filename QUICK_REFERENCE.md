# 🚀 VoxCPM 流式API - 快速参考卡

## ⚡ 一分钟快速测试

```bash
cd /home/neo/upload/VoxCPM
python3 quick_test_streaming.py
```

## 📊 关键数据

| 指标 | 普通API | 流式API | 提升 |
|------|---------|---------|------|
| 首字节 | 15-24秒 | **2-3秒** | **85-90%** ⬆️ |

## 🔌 API端点

```
POST http://localhost:7861/api/tts/stream
```

## 💻 使用示例

### Python
```python
import requests

response = requests.post(
    "http://localhost:7861/api/tts/stream",
    data={"text": "你好", "inference_timesteps": 5},
    stream=True
)

with open("out.wav", "wb") as f:
    for chunk in response.iter_content(8192):
        if chunk:
            f.write(chunk)
```

### curl
```bash
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=你好" \
  -F "inference_timesteps=5" \
  --output out.wav
```

## 📝 参数

| 参数 | 必填 | 默认值 |
|------|------|--------|
| text | ✅ | - |
| inference_timesteps | ❌ | 5 |
| cfg_value | ❌ | 2.0 |
| prompt_audio | ❌ | null |
| prompt_text | ❌ | null |

## 🧪 测试命令

```bash
# 快速测试 (30秒)
python3 quick_test_streaming.py

# 完整对比 (5分钟)
python3 test_streaming_api.py

# 基准测试 (10分钟)
python3 benchmark_streaming.py
```

## 📚 文档

- [API使用指南](STREAMING_API.md)
- [测试指南](TEST_STREAMING.md)
- [执行指南](RUN_TESTS_NOW.md)
- [实现总结](STREAMING_SUMMARY.md)

## 🔧 故障排查

```bash
# 检查服务
curl http://localhost:7861/health

# 启动服务
docker-compose up -d && sleep 30

# 查看日志
docker logs voxcpm
```

## ✅ 验证清单

- [ ] 首字节 < 3秒
- [ ] 音频可播放
- [ ] 文件大小正常
- [ ] 无错误信息

## 🎯 预期结果

```
⚡ 首字节: 2.45秒
⏱️  总时间: 15.67秒
🎵 音频块数: 8
💾 文件: 275KB
```

---

**开始测试:** `python3 quick_test_streaming.py` 🚀
