# 🚀 流式API测试指南

## 快速开始

### 1. 确保服务运行

```bash
# 检查服务状态
curl http://localhost:7861/health

# 如果未运行，启动服务
docker-compose up -d

# 查看日志
docker logs -f voxcpm
```

### 2. 运行快速测试（推荐）

```bash
cd /home/neo/upload/VoxCPM
python3 quick_test_streaming.py
```

**预期输出:**
```
🚀 快速测试流式API
==================================================
✅ 服务运行中

🟢 测试流式API...
⚡ 首字节: 2.34秒
  📦 块1: 8192字节
  📦 块2: 8192字节
  ...

✅ 完成
⚡ 首字节: 2.34秒
⏱️  总时间: 15.67秒
💾 保存: quick_test_stream.wav
```

### 3. 运行完整性能测试

```bash
python3 test_streaming_api.py
```

**测试内容:**
- ✅ 场景1: 默认语音（无参考音频）
  - 普通API测试
  - 流式API测试
  - 性能对比
  
- ✅ 场景2: 声音克隆（使用参考音频）
  - 普通API测试
  - 流式API测试
  - 性能对比

**预期结果:**

```
📊 性能对比
============================================================

⚡ 首字节响应时间:
  普通API:  15.23 秒
  流式API:  2.45 秒
  ⬆️  提升: 83.9% (12.78秒)

⏱️  总生成时间:
  普通API:  15.23 秒
  流式API:  15.67 秒

📦 文件大小:
  普通API:  275.4 KB
  流式API:  275.4 KB

🎵 流式输出:
  音频块数: 8
  首块时间: 2.45s
  末块时间: 15.67s
```

## 手动测试

### 使用 curl

```bash
# 测试流式API
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=你好，这是流式测试" \
  -F "inference_timesteps=5" \
  --output test_stream.wav

# 测试普通API（对比）
curl -X POST http://localhost:7861/api/tts \
  -F "text=你好，这是普通测试" \
  -F "inference_timesteps=5" \
  --output test_normal.wav
```

### 使用 Python

```python
import requests
import time

# 流式API
start = time.time()
response = requests.post(
    "http://localhost:7861/api/tts/stream",
    data={"text": "测试文本", "inference_timesteps": 5},
    stream=True
)

first_byte = None
with open("output.wav", "wb") as f:
    for chunk in response.iter_content(8192):
        if chunk:
            if first_byte is None:
                first_byte = time.time()
                print(f"首字节: {first_byte - start:.2f}秒")
            f.write(chunk)

print(f"总时间: {time.time() - start:.2f}秒")
```

## 预期性能指标

### 首次请求（冷启动）
- 模型加载: ~15秒
- 首字节: ~17秒
- 总时间: ~30秒

### 后续请求（模型已加载）
- **流式API首字节: 2-3秒** ⚡
- 普通API首字节: 15-24秒
- 总生成时间: 15-24秒（两者相同）

### 性能提升
- **首字节延迟降低: 85-90%** 🚀
- 用户感知延迟: 显著降低
- 可实现边生成边播放

## 测试场景

### 场景1: 短文本（推荐）
```bash
text="你好，这是测试。"
# 预期: 首字节 2-3秒，总时间 10-15秒
```

### 场景2: 中等文本
```bash
text="你好，这是VoxCPM流式语音合成测试。我们正在对比性能差异。"
# 预期: 首字节 2-3秒，总时间 15-20秒
```

### 场景3: 长文本
```bash
text="这是一段较长的测试文本。VoxCPM支持流式输出，可以边生成边返回音频。这大幅降低了首字节响应时间，提升了用户体验。"
# 预期: 首字节 2-3秒，总时间 20-30秒
```

### 场景4: 声音克隆
```bash
# 需要提供参考音频
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=克隆的声音测试" \
  -F "prompt_audio=@examples/example.wav" \
  -F "prompt_text=参考音频文本" \
  --output cloned.wav
```

## 故障排查

### 问题1: 连接被拒绝
```bash
# 检查服务是否运行
docker ps | grep voxcpm

# 启动服务
docker-compose up -d

# 等待服务就绪（约30秒）
sleep 30
curl http://localhost:7861/health
```

### 问题2: 首字节延迟很高
- **原因**: 首次请求需要加载模型
- **解决**: 等待模型加载完成后再测试
- **验证**: 查看日志 `docker logs voxcpm | grep "model loaded"`

### 问题3: 音频不完整
- **原因**: 网络中断或接收不完整
- **解决**: 确保接收所有chunks
- **验证**: 检查文件大小是否合理（通常 200-500KB）

### 问题4: 测试脚本报错
```bash
# 检查Python依赖
pip3 install requests soundfile

# 检查文件权限
chmod +x test_streaming_api.py quick_test_streaming.py
```

## 输出文件

测试完成后，输出文件保存在:

```
./test_outputs/
├── normal_no_prompt.wav      # 普通API（默认语音）
├── streaming_no_prompt.wav   # 流式API（默认语音）
├── normal_with_prompt.wav    # 普通API（声音克隆）
└── streaming_with_prompt.wav # 流式API（声音克隆）

./
├── quick_test_stream.wav     # 快速测试输出
```

## 下一步

1. ✅ 验证流式API工作正常
2. ✅ 对比性能差异
3. 🔄 集成到前端应用
4. 🔄 实现实时播放
5. 🔄 优化用户体验

## 相关文档

- [流式API使用指南](STREAMING_API.md)
- [API参数说明](PARAMETERS.md)
- [部署文档](README.md)
