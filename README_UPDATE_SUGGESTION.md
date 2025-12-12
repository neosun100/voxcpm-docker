# README.md 更新建议

建议在原 README.md 中添加以下 Docker 部署章节：

## 🐳 Docker 部署（推荐）

### 快速启动

```bash
# 一键启动（自动选择最空闲的 GPU）
./start.sh

# 访问服务
# UI:  http://localhost:7861
# API: http://localhost:7861/apidocs
```

### 三种访问模式

VoxCPM Docker 版本支持三种访问方式：

1. **Web UI** - 适合人工交互和测试
2. **REST API** - 适合应用集成
3. **MCP 协议** - 适合 AI Agent 和自动化工作流

详见 [Docker 部署指南](README_DOCKER.md)

### 特性

- ✅ 自动选择显存占用最少的 GPU
- ✅ 智能 GPU 内存管理（空闲自动释放）
- ✅ 三合一服务（UI + API + MCP）
- ✅ 零配置一键启动
- ✅ 完整中文文档

### 文档

- [快速启动](START_HERE.md) - 30 秒上手
- [完整指南](README_DOCKER.md) - 详细部署文档
- [MCP 使用](MCP_GUIDE.md) - MCP 协议说明
- [项目结构](DOCKER_STRUCTURE.md) - 架构说明

---

## 或者在 README.md 开头添加醒目提示：

在原 README.md 的 "Quick Start" 章节之前添加：

```markdown
> 🐳 **推荐使用 Docker 部署**：支持 UI + API + MCP 三种访问模式，自动 GPU 管理，一键启动。
> 详见 [START_HERE.md](START_HERE.md) 或 [Docker 部署指南](README_DOCKER.md)
```
