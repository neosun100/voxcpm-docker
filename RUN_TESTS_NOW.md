# 🚀 立即运行测试 - 执行指南

## ⚡ 快速开始（3步）

### 步骤 1: 检查服务状态

```bash
curl http://localhost:7861/health
```

**如果返回错误，启动服务:**
```bash
cd /home/neo/upload/VoxCPM
docker-compose up -d
sleep 30  # 等待服务启动
```

### 步骤 2: 快速测试（30秒）

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

### 步骤 3: 完整对比测试（5分钟）

```bash
python3 test_streaming_api.py
```

**预期输出:**
```
🎙️ VoxCPM 流式API性能测试
============================================================
✅ 服务运行正常

🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷
测试场景 1: 使用默认语音（无参考音频）
🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷🔷

============================================================
🔵 测试普通API（非流式）
============================================================
📝 输入文本: 你好，这是VoxCPM流式语音合成测试...
⏱️  开始请求...
⚡ 首字节响应时间: 15.23 秒
✅ 完成！
📊 总耗时: 15.23 秒
📦 文件大小: 275.4 KB
💾 保存到: ./test_outputs/normal_no_prompt.wav

============================================================
🟢 测试流式API
============================================================
📝 输入文本: 你好，这是VoxCPM流式语音合成测试...
⏱️  开始请求...
⚡ 首字节响应时间: 2.45 秒
  📦 收到第 1 块: 8192 字节 (累计 2.45s)
  📦 收到第 2 块: 8192 字节 (累计 4.12s)
  📦 收到第 3 块: 8192 字节 (累计 6.78s)
  ...
✅ 完成！
📊 总耗时: 15.67 秒
📦 文件大小: 275.4 KB
🎵 收到 8 个音频块
💾 保存到: ./test_outputs/streaming_no_prompt.wav

============================================================
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

[继续测试场景 2: 声音克隆...]

============================================================
✅ 测试完成！
📁 输出文件保存在: /home/neo/upload/VoxCPM/test_outputs
============================================================
```

## 📊 关键指标验证

### ✅ 成功标准

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| 流式API首字节 | 2-3秒 | 查看测试输出 |
| 普通API首字节 | 15-24秒 | 查看测试输出 |
| 性能提升 | 85-90% | 查看对比报告 |
| 音频质量 | 相同 | 文件大小一致 |
| 音频块数 | 5-10块 | 查看流式输出 |

### 🎯 验证清单

运行测试后，检查以下内容：

- [ ] 流式API首字节时间 < 3秒
- [ ] 普通API首字节时间 > 15秒
- [ ] 性能提升 > 80%
- [ ] 两种API文件大小相同
- [ ] 音频可以正常播放
- [ ] 没有错误信息

## 🔧 故障排查

### 问题 1: 服务未运行

**症状:**
```
❌ 无法连接到服务: Connection refused
```

**解决:**
```bash
cd /home/neo/upload/VoxCPM
docker-compose up -d
sleep 30
curl http://localhost:7861/health
```

### 问题 2: 首次请求很慢

**症状:**
```
⚡ 首字节: 17.34秒  # 比预期慢
```

**原因:** 首次请求需要加载模型

**解决:** 再运行一次测试，第二次会快很多

### 问题 3: Python依赖缺失

**症状:**
```
ModuleNotFoundError: No module named 'requests'
```

**解决:**
```bash
pip3 install requests soundfile numpy
```

### 问题 4: 权限错误

**症状:**
```
Permission denied: test_streaming_api.py
```

**解决:**
```bash
chmod +x *.py
```

## 📁 输出文件位置

测试完成后，检查以下文件：

```
/home/neo/upload/VoxCPM/
├── quick_test_stream.wav          # 快速测试输出
└── test_outputs/                  # 完整测试输出
    ├── normal_no_prompt.wav       # 普通API（默认语音）
    ├── streaming_no_prompt.wav    # 流式API（默认语音）
    ├── normal_with_prompt.wav     # 普通API（声音克隆）
    └── streaming_with_prompt.wav  # 流式API（声音克隆）
```

## 🎵 播放测试音频

### Linux
```bash
# 使用 aplay
aplay quick_test_stream.wav

# 使用 ffplay
ffplay quick_test_stream.wav
```

### macOS
```bash
afplay quick_test_stream.wav
```

### Windows
```bash
start quick_test_stream.wav
```

## 📈 可选：基准测试（10分钟）

如果想要更详细的统计数据：

```bash
python3 benchmark_streaming.py
```

这会运行每个场景3次，生成统计报告：
- 平均值
- 最小值
- 最大值
- JSON报告文件

## 🎉 测试成功后

### 验证结果

1. **查看性能提升**
   - 流式API首字节应该在 2-3秒
   - 比普通API快 85-90%

2. **播放音频文件**
   - 确认音频质量正常
   - 两种API输出应该一致

3. **查看输出文件**
   ```bash
   ls -lh test_outputs/
   ```

### 下一步

- ✅ 流式API已验证工作
- 🔄 可以集成到应用中
- 🔄 可以更新README
- 🔄 可以部署到生产环境

## 📞 需要帮助？

### 查看日志
```bash
# 服务日志
docker logs voxcpm

# 最近100行
docker logs --tail 100 voxcpm

# 实时日志
docker logs -f voxcpm
```

### 检查GPU状态
```bash
curl http://localhost:7861/api/gpu/status
```

### 重启服务
```bash
docker-compose restart
sleep 30
```

## 📝 报告结果

测试完成后，请报告：

1. **性能数据**
   - 流式API首字节时间: ___ 秒
   - 普通API首字节时间: ___ 秒
   - 性能提升百分比: ___ %

2. **测试状态**
   - [ ] 快速测试通过
   - [ ] 完整测试通过
   - [ ] 音频质量正常
   - [ ] 无错误信息

3. **问题反馈**
   - 遇到的问题: ___
   - 错误信息: ___
   - 解决方案: ___

---

**准备好了吗？开始测试！** 🚀

```bash
cd /home/neo/upload/VoxCPM
python3 quick_test_streaming.py
```
