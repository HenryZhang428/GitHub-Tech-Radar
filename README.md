# GitHub Tech Radar 🚀

> 你的私人技术情报中心。发现、分析并追踪 GitHub 上的技术趋势与大佬动态。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![AI](https://img.shields.io/badge/AI-Ollama%20Local-purple.svg)

## 📖 项目介绍

这是一个全自动化的 GitHub 情报收集与分析系统。它不仅仅是简单的热榜搬运工，更是一个集成了 **本地 AI 模型** 的智能分析师。

**核心特性**:

*   **🔍 智能混合搜索 (Smart Hybrid Search)**:
    *   **跨语言理解**: 输入中文关键词（如"AI助手"），AI 自动转换为技术术语进行全球搜索。
    *   **精准产品定位**: 自动识别专有名词（如"Xiaozhi"），直达具体项目而非泛化结果。
*   **🌍 七国语言实时互译**: 内置多语言 UI (中/英/日/韩/西/法/德)，并支持 **AI 解读内容的实时翻译**。
*   **⚡️ Mac 状态栏情报站**: 驻留在菜单栏，随时一键查看全球热点。
*   **🌌 科幻风 Web Dashboard**:
    *   **多维度热榜**: 支持 **Daily / Weekly / Monthly** 自由切换，精准把握短期热点与长期趋势。
    *   **Guru Discovery**: 内置行业大神推荐库（AI, 前端, 后端等），像刷微博一样一键关注技术大牛。
    *   **VIP 动态追踪**: 实时监控关注对象的 Star/Create 动态，不错过任何一个潜力项目。
*   **🧠 本地 AI 深度解读**: 内置支持 **Ollama (Llama 3.2)**，完全本地运行，免费且隐私安全。
*   **📂 自动归档**: 每日情报自动保存为 Markdown 历史档案，构建你的技术知识库。

## 🚀 快速开始

### 1. 环境准备

确保你安装了 Python 3.10+ 和 [Ollama](https://ollama.com/)。

**拉取 AI 模型 (推荐 Llama 3.2)**:
```bash
ollama pull llama3.2:3b
```

### 2. 安装项目

```bash
git clone https://github.com/your-username/github-tech-radar.git
cd github-tech-radar

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动服务

本项目包含三个组件，建议按需运行：

**A. 交互式 Web 情报站 (推荐)**
提供完整的可视化界面，支持大神关注、智能搜索、热榜切换等交互功能。
```bash
python src/web_server.py
# 访问 http://localhost:5001
```

**B. 后台数据服务**
仅用于定时抓取数据和生成静态文件（如果不需要交互式 Web 功能）。
```bash
python src/service.py
```

**C. Mac 状态栏 App**
提供便捷的菜单栏访问入口。
```bash
python src/mac_app.py
```

## ⚙️ 配置指南

### 关注列表 (VIP Watchlist)
你可以在 Web 界面中直接管理关注对象，也可以手动编辑 `watchlist.json` 文件：
```json
[
  "torvalds",
  "antirez",
  "karpathy",
  "yyx990803"
]
```

### AI 模型配置
默认使用本地 `llama3.2:3b`。如需修改，请编辑 `src/llm.py`。

## 🏗️ 架构设计

*   **`src/web_server.py`**: 基于 Flask 的交互式 Web 服务端。
*   **`src/service.py`**: 后台守护进程，负责调度爬虫和 AI 分析任务。
*   **`src/mac_app.py`**: 基于 `rumps` 的 macOS 客户端。
*   **`src/cache_manager.py`**: 统一数据持久化层，管理 JSON 缓存。
*   **`src/user_tracker.py`**: 负责追踪用户动态的逻辑。
*   **`src/llm.py`**: AI 接口层，封装了 OpenAI 和 Ollama 的调用逻辑。
*   **`src/scraper.py`**: GitHub 数据采集与搜索模块。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License
