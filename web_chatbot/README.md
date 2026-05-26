# Web Chatbot

一个基于 FastAPI 和 DeepSeek API 的现代化 Web 聊天机器人。

## 功能特性

### 核心功能
- ✅ 流式响应（Streaming）
- ✅ 会话管理（Session ID）
- ✅ 多轮对话上下文保持
- ✅ 自动会话清理（1小时过期）

### 安全与稳定性
- ✅ 完善的错误处理（前后端）
- ✅ 超时检测（60秒请求超时，30秒流超时）
- ✅ 输入验证（空消息、长度限制 4000 字符）
- ✅ XSS 防护

### 用户体验
- ✅ 现代化 UI（渐变色、卡片式、动画效果）
- ✅ 自动滚动到底部
- ✅ Enter 键发送消息
- ✅ 清空对话按钮
- ✅ 错误提示（红色显示）

### 生产就绪
- ✅ 日志系统（控制台 + 文件）
- ✅ 性能监控（请求时间追踪）
- ✅ CORS 跨域支持
- ✅ 可配置 System Prompt

## 快速开始

### 1. 安装依赖

```bash
cd web_chatbot
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API Key

### 3. 启动服务器

```bash
uvicorn main:app --reload --port 9000
```

### 4. 访问应用

打开浏览器访问：`http://localhost:9000`

## 自定义配置

### 自定义 AI 角色

在 `.env` 文件中设置：

```
SYSTEM_PROMPT=你是一个专业的 Python 编程助手
```

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **前端**: 原生 HTML/CSS/JavaScript
- **AI**: DeepSeek API (OpenAI SDK)
- **日志**: Python logging

## 许可证

MIT License
