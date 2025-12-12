# ✅ VoxCPM Docker 部署检查清单

## 📋 文件清单

### Docker 相关 ✅
- [x] `Dockerfile` - CUDA 12.1 基础镜像
- [x] `docker-compose.yml` - GPU 支持配置
- [x] `.dockerignore` - 构建优化
- [x] `.env.example` - 环境变量模板
- [x] `start.sh` - 一键启动脚本（可执行）

### 服务端 ✅
- [x] `server.py` - 统一服务器（UI + API）
- [x] `mcp_server.py` - MCP 服务器（可执行）
- [x] `gpu_manager.py` - GPU 资源管理器

### 文档 ✅
- [x] `QUICKSTART.md` - 快速启动指南
- [x] `README_DOCKER.md` - 完整部署文档
- [x] `MCP_GUIDE.md` - MCP 使用指南
- [x] `DOCKER_STRUCTURE.md` - 项目结构说明
- [x] `DEPLOYMENT_SUMMARY.md` - 部署总结
- [x] `CHECKLIST.md` - 本检查清单

### 测试与工具 ✅
- [x] `test_deployment.sh` - 部署测试脚本（可执行）
- [x] `test_mcp.py` - MCP 测试脚本（可执行）
- [x] `Makefile` - 快捷命令
- [x] `mcp_client.json` - MCP 客户端配置

### 目录结构 ✅
- [x] `outputs/` - 输出目录（已创建）
- [x] `models/` - 模型缓存目录（Docker 自动创建）

## 🎯 功能检查清单

### 1. Docker 化 ✅
- [x] 基于 nvidia/cuda 镜像
- [x] 安装所有依赖
- [x] GPU 支持配置
- [x] 端口映射到 0.0.0.0
- [x] 卷挂载配置
- [x] 重启策略

### 2. 自动 GPU 选择 ✅
- [x] 检查 nvidia-smi
- [x] 查询所有 GPU 显存使用
- [x] 选择显存占用最少的 GPU
- [x] 设置 NVIDIA_VISIBLE_DEVICES
- [x] 更新 .env 文件

### 3. UI 界面模式 ✅
- [x] 语音合成标签页
  - [x] 文本输入框
  - [x] 参数调节（所有 12 个参数）
    - [x] cfg_value (滑块 0.5-5.0)
    - [x] inference_timesteps (滑块 5-20)
    - [x] min_len (滑块 1-100)
    - [x] max_len (滑块 100-8192)
    - [x] normalize (复选框)
    - [x] denoise (复选框)
    - [x] retry_badcase (复选框)
    - [x] retry_badcase_max_times (滑块 1-10)
    - [x] retry_badcase_ratio_threshold (滑块 1.0-20.0)
  - [x] 高级设置折叠面板
  - [x] 合成按钮
  - [x] 音频输出
- [x] 声音克隆标签页
  - [x] 文本输入框
  - [x] 参考音频上传
  - [x] 参考文本输入
  - [x] 参数调节（所有 12 个参数）
    - [x] cfg_value
    - [x] inference_timesteps
    - [x] min_len
    - [x] max_len
    - [x] normalize
    - [x] denoise
    - [x] retry_badcase
    - [x] retry_badcase_max_times
    - [x] retry_badcase_ratio_threshold
  - [x] 高级设置折叠面板
  - [x] 克隆按钮
  - [x] 音频输出
- [x] GPU 状态标签页
  - [x] 状态显示
  - [x] 刷新按钮
  - [x] 卸载按钮

### 4. API 模式 ✅
- [x] 健康检查端点 (`GET /health`)
- [x] TTS 端点 (`POST /api/tts`)
  - [x] 文本参数
  - [x] 文件上传（参考音频）
  - [x] 所有可调参数（12 个）
    - [x] text (required)
    - [x] prompt_audio (optional)
    - [x] prompt_text (optional)
    - [x] cfg_value (default: 2.0)
    - [x] inference_timesteps (default: 10)
    - [x] min_len (default: 2)
    - [x] max_len (default: 4096)
    - [x] normalize (default: false)
    - [x] denoise (default: false)
    - [x] retry_badcase (default: true)
    - [x] retry_badcase_max_times (default: 3)
    - [x] retry_badcase_ratio_threshold (default: 6.0)
  - [x] 音频文件返回
- [x] GPU 状态端点 (`GET /api/gpu/status`)
- [x] GPU 卸载端点 (`POST /api/gpu/offload`)
- [x] Swagger 文档 (`GET /apidocs`)
  - [x] 所有参数说明
  - [x] 参数类型和默认值
  - [x] 参数描述
- [x] CORS 支持
- [x] 错误处理

### 5. MCP 模式 ✅
- [x] MCP 服务器实现
- [x] 工具：text_to_speech
  - [x] 完整参数支持（12 个）
    - [x] text (required)
    - [x] output_path (optional)
    - [x] cfg_value (default: 2.0)
    - [x] inference_timesteps (default: 10)
    - [x] min_len (default: 2)
    - [x] max_len (default: 4096)
    - [x] normalize (default: False)
    - [x] denoise (default: False)
    - [x] retry_badcase (default: True)
    - [x] retry_badcase_max_times (default: 3)
    - [x] retry_badcase_ratio_threshold (default: 6.0)
  - [x] 类型注解
  - [x] 文档字符串
- [x] 工具：voice_cloning
  - [x] 参考音频支持
  - [x] 完整参数支持（12 个）
    - [x] text (required)
    - [x] reference_audio (required)
    - [x] reference_text (optional)
    - [x] output_path (optional)
    - [x] cfg_value (default: 2.0)
    - [x] inference_timesteps (default: 10)
    - [x] min_len (default: 2)
    - [x] max_len (default: 4096)
    - [x] normalize (default: False)
    - [x] denoise (default: False)
    - [x] retry_badcase (default: True)
    - [x] retry_badcase_max_times (default: 3)
    - [x] retry_badcase_ratio_threshold (default: 6.0)
  - [x] 类型注解
  - [x] 文档字符串
- [x] 工具：get_gpu_status
  - [x] 显存查询
  - [x] 模型状态
- [x] 工具：offload_model
  - [x] 强制卸载
- [x] MCP 客户端配置文件
- [x] MCP 使用文档（已更新所有参数）

### 6. GPU 管理 ✅
- [x] 延迟加载模型
- [x] 自动空闲卸载
  - [x] 可配置超时时间
  - [x] 后台监控线程
- [x] 线程安全（锁机制）
- [x] 强制卸载接口
- [x] 三种模式共享管理器

### 7. 文档完整性 ✅
- [x] 快速启动指南（30 秒上手）
- [x] 完整部署文档
  - [x] 三种访问模式说明
  - [x] API 使用示例
  - [x] 参数说明
  - [x] 故障排除
- [x] MCP 使用指南
  - [x] 所有工具说明
  - [x] 参数文档（已更新所有 12 个参数）
  - [x] 使用示例
  - [x] 配置说明
- [x] 项目结构说明
- [x] 部署总结
- [x] 参数完整对照表 ⭐ 新增
  - [x] 所有 12 个参数详解
  - [x] 参数范围和默认值
  - [x] 使用场景推荐
  - [x] API/MCP 调用示例

### 8. 参数完整性检查 ✅ 新增
- [x] VoxCPM.generate() 所有参数已识别
  - [x] text ✅
  - [x] prompt_wav_path ✅
  - [x] prompt_text ✅
  - [x] cfg_value ✅
  - [x] inference_timesteps ✅
  - [x] min_len ✅
  - [x] max_len ✅
  - [x] normalize ✅
  - [x] denoise ✅
  - [x] retry_badcase ✅
  - [x] retry_badcase_max_times ✅
  - [x] retry_badcase_ratio_threshold ✅
- [x] UI 界面支持所有参数
- [x] API 端点支持所有参数
- [x] MCP 工具支持所有参数
- [x] Swagger 文档包含所有参数
- [x] 参数说明文档完整

### 8. 测试脚本 ✅
- [x] 部署测试脚本
  - [x] 健康检查测试
  - [x] GPU 状态测试
  - [x] Swagger 文档测试
  - [x] UI 界面测试
  - [x] TTS API 测试
- [x] MCP 测试脚本
  - [x] 配置验证
  - [x] 工具列表

## 🧪 测试验证清单

### 本地测试 ⏳
- [ ] Docker 镜像构建成功
  ```bash
  docker-compose build
  ```
- [ ] 容器启动成功
  ```bash
  ./start.sh
  ```
- [ ] 自动选择最空闲 GPU
  ```bash
  # 检查日志中的 GPU 选择信息
  docker-compose logs | grep "Selected GPU"
  ```
- [ ] UI 界面可访问
  ```bash
  curl -I http://0.0.0.0:7861
  ```
- [ ] API 接口可访问
  ```bash
  curl http://0.0.0.0:7861/health
  ```
- [ ] Swagger 文档可访问
  ```bash
  curl -I http://0.0.0.0:7861/apidocs
  ```
- [ ] MCP 服务器可连接
  ```bash
  ./test_mcp.py
  ```
- [ ] 运行完整测试
  ```bash
  ./test_deployment.sh
  ```

### 功能测试 ⏳
- [ ] UI 文本合成功能
- [ ] UI 声音克隆功能
- [ ] UI GPU 状态显示
- [ ] UI GPU 卸载功能
- [ ] API 文本转语音
- [ ] API 声音克隆
- [ ] API GPU 状态查询
- [ ] API GPU 卸载
- [ ] MCP text_to_speech 工具
- [ ] MCP voice_cloning 工具
- [ ] MCP get_gpu_status 工具
- [ ] MCP offload_model 工具

### GPU 管理测试 ⏳
- [ ] 模型自动加载
- [ ] 模型自动卸载（等待 60 秒）
- [ ] 手动卸载功能
- [ ] 显存释放验证
  ```bash
  # 使用前
  nvidia-smi
  # 使用后等待 60 秒
  nvidia-smi
  ```

## 📊 性能验证 ⏳
- [ ] RTF 测试（应 < 0.3）
- [ ] 显存占用测试（应 < 6GB）
- [ ] 并发请求测试
- [ ] 长时间运行稳定性

## 🔒 安全检查 ⏳
- [ ] 端口绑定正确（0.0.0.0）
- [ ] 文件权限正确
- [ ] 环境变量不包含敏感信息
- [ ] 容器以非 root 用户运行（可选）

## 📝 文档检查 ✅
- [x] 所有文档文件存在
- [x] 文档内容完整
- [x] 示例代码正确
- [x] 链接有效
- [x] 格式规范

## 🎯 下一步操作

### 立即执行
```bash
# 1. 启动服务
./start.sh

# 2. 运行测试
./test_deployment.sh

# 3. 访问服务
# UI:  http://localhost:7861
# API: http://localhost:7861/apidocs
```

### 可选优化
- [ ] 添加 API 认证
- [ ] 添加速率限制
- [ ] 配置 HTTPS
- [ ] 添加监控告警
- [ ] 配置日志轮转
- [ ] 添加健康检查探针

## ✨ 完成标准

当以下所有项都完成时，部署即为成功：

1. ✅ 所有文件已创建
2. ⏳ Docker 镜像构建成功
3. ⏳ 容器启动成功
4. ⏳ 三种访问模式都可用
5. ⏳ GPU 自动管理正常工作
6. ⏳ 测试脚本全部通过

## 🆘 遇到问题？

1. 查看日志
   ```bash
   docker-compose logs -f
   ```

2. 检查 GPU
   ```bash
   nvidia-smi
   docker exec voxcpm-service nvidia-smi
   ```

3. 运行测试
   ```bash
   ./test_deployment.sh
   ```

4. 查看文档
   - [QUICKSTART.md](QUICKSTART.md)
   - [README_DOCKER.md](README_DOCKER.md)
   - [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

---

**准备好了吗？开始测试！**

```bash
./start.sh
```
