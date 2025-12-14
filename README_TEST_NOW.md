# 🚀 立即测试流式API

## ⚠️ 重要提示

流式API代码已实现，但**需要重启Docker容器**才能生效！

## 📊 当前测试结果

### ✅ 普通API（已验证）

| 文本 | 首字节 | 总时间 | 文件大小 |
|------|--------|--------|----------|
| 短文本(14字) | 1.05s | 1.05s | 206.8KB |
| 中文本(51字) | 3.94s | 3.94s | 909.6KB |
| 长文本(126字) | 8.34s | 8.35s | 1557.3KB |

### ❌ 流式API（未生效）

- 返回: 404 Not Found
- 原因: Docker容器运行旧代码
- 解决: 重启容器

## 🔧 立即执行（3步）

### 步骤1: 重启服务

```bash
cd /home/neo/upload/VoxCPM
docker-compose restart
sleep 30
```

### 步骤2: 验证流式API

```bash
curl -X POST http://localhost:7861/api/tts/stream \
  -F "text=测试流式API" \
  --output test.wav

# 检查文件大小（应该 > 0）
ls -lh test.wav
```

### 步骤3: 运行完整测试

```bash
python3 api_validation_test.py
```

## 📈 预期结果

重启后应该看到：

```
🟢 测试流式API (/api/tts/stream)
  运行 1/5 [流式][short]: 首字节=0.3s, 总时间=1.0s, 大小=206.8KB
  运行 2/5 [流式][short]: 首字节=0.3s, 总时间=1.0s, 大小=193.0KB
  ...

📊 性能对比
  普通API:  1.05s
  流式API:  0.30s
  提升:     71.4% ⬆️
```

## 🎯 预期性能提升

| 文本 | 普通API | 流式API | 提升 |
|------|---------|---------|------|
| 短文本 | 1.05s | **~0.3s** | **~70%** |
| 中文本 | 3.94s | **~1.0s** | **~75%** |
| 长文本 | 8.34s | **~2.0s** | **~76%** |

## 📁 测试报告

测试完成后查看：

```bash
# 查看Markdown报告
cat api_validation_results/api_validation_*.md

# 查看JSON数据
cat api_validation_results/api_validation_*.json | jq .
```

## 🆘 故障排查

### 问题1: 容器重启失败

```bash
# 查看日志
docker logs voxcpm

# 完全重启
docker-compose down
docker-compose up -d
sleep 60
```

### 问题2: 流式API仍返回404

```bash
# 检查端点是否存在
grep "def tts_stream" server.py

# 检查容器中的代码
docker exec voxcpm grep "def tts_stream" /app/server.py
```

如果容器中没有，需要重新构建：

```bash
docker-compose down
docker-compose build
docker-compose up -d
sleep 60
```

### 问题3: 测试脚本报错

```bash
# 安装依赖
pip3 install requests

# 检查服务
curl http://localhost:7861/health
```

## 📚 相关文档

- [API测试结果](API_TEST_RESULTS.md)
- [最终测试总结](FINAL_TEST_SUMMARY.md)
- [流式API指南](STREAMING_API.md)
- [快速参考](QUICK_REFERENCE.md)

---

**立即执行:**
```bash
docker-compose restart && sleep 30 && python3 api_validation_test.py
```
