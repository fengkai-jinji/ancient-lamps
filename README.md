# 🌟 流光映古灯

> 一盏古灯，穿越千年时光，照亮历史的长河

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/fengkai-jinji/ancient-lamps/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/fengkai-jinji/ancient-lamps?style=social)](https://github.com/fengkai-jinji/ancient-lamps/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/fengkai-jinji/ancient-lamps?style=social)](https://github.com/fengkai-jinji/ancient-lamps/network/members)

## 📖 项目简介

**流光映古灯** 是一个致力于探索和传承中华古代灯具文化的数字化项目。通过现代信息技术，我们将那些沉睡在历史长河中的灯具珍宝重新唤醒，让更多人能够感受古人的智慧与审美。

从战国时期的青铜灯，到汉代的陶灯，再到唐宋的瓷灯，每一盏灯都承载着不同时代的文化记忆。本项目通过图片展示、文化解读、交互体验等多种形式，为用户提供沉浸式的古代灯具文化之旅。

## ✨ 核心特性

- 🏺 **灯具鉴赏** - 收录各朝代精美灯具图片，支持高清放大查看细节
- 🗺️ **历史地图** - 展示古代灯具出土地点，探索文明分布
- 📚 **文化解读** - 深入解析灯具背后的历史故事与文化内涵
- 🤖 **智能交互** - AI 驱动的问答系统，随时解答关于古灯的疑问
- 🎨 **创意体验** - 虚拟灯具设计打印，将传统美学融入现代生活

## 🛠️ 技术栈

### 后端技术
- **Python** - 核心开发语言
- **Flask** - 轻量级 Web 框架
- **MySQL** - 数据存储
- **RESTful API** - 接口设计

### 前端技术
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **ECharts** - 数据可视化图表库
- **WebGL** - 3D 模型渲染

### 第三方服务
- **通义千问 API** - AI 智能问答支持
- **百度地图 API** - 地理信息展示

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- npm 或 yarn

### 后端部署

```bash
# 进入后端目录
cd 流光映古灯-璞玉组/backend

# 安装依赖
pip install -r requirements.txt

# 配置数据库连接（复制配置模板）
cp backend/utils/config.example.py backend/utils/config.py
# 数据库密码及服务密钥通过环境变量提供，见下文

# 初始化数据库
# 运行数据库脚本完成表结构创建

# 启动服务
python app.py
```

### 本地凭据配置

请先复制上面的配置模板，再在启动后端的同一个 PowerShell 窗口中设置环境变量：

```powershell
$env:DB_PASSWORD = '<填写本机数据库密码>'
$env:AMAP_API_KEY = '<填写新建的高德 Web 服务密钥>'
$env:DEEPSEEK_API_KEY = '<填写新建的 DeepSeek 密钥>'
python app.py
```

- 数据库可选变量：`DB_HOST`（默认 localhost）、`DB_PORT`（默认 3306）、`DB_USER`（默认 root）、`DB_NAME`（默认 card）。
- 缺少 `DB_PASSWORD` 时，示例配置会停止启动，避免意外使用硬编码密码。
- 缺少 `AMAP_API_KEY` 时跳过地址地理编码；缺少 `DEEPSEEK_API_KEY` 时聊天接口返回配置提示。
- `test_ai_api.py` 使用同一个 `DEEPSEEK_API_KEY`；数据库更新脚本使用相同的 `DB_*` 变量。
- 程序直接读取进程环境变量，不会自动加载 `.env`。如使用本地 `.env` 或实际 `config.py`，请保持其被 Git 忽略。
- 不要将真实密钥、密码、终端环境截图提交到仓库。历史中出现过的凭据应在对应平台撤销或更换。

### 前端地图配置

复制 `流光映古灯-璞玉组/puyu2.0/.env.example` 为同目录下的 `.env.local`，填写新申请的高德 JavaScript API Key 和安全码，再启动或重新构建前端。未配置时跳过地图加载。

`VITE_*` 变量会进入浏览器构建产物，并非服务端秘密存储。请在高德控制台配置对应域名的访问限制，前后端分别使用对应服务类型的凭据；不要沿用历史中的旧值。`.env.local` 已被忽略，请勿提交。

### 前端部署

```bash
# 进入前端目录
cd 流光映古灯-璞玉组/puyu2.0

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

## 📁 项目结构

```
流光映古灯-temp/
├── 流光映古灯-璞玉组/
│   ├── backend/                    # 后端服务
│   │   ├── backend/
│   │   │   ├── models/            # 数据模型
│   │   │   └── utils/             # 工具函数
│   │   ├── data/                  # 数据文件
│   │   ├── scripts/               # 初始化脚本
│   │   ├── static/                # 静态资源
│   │   ├── templates/             # HTML 模板
│   │   └── app.py                 # 应用入口
│   │
│   └── puyu2.0/                   # 前端应用
│       ├── src/
│       │   ├── assets/            # 静态资源
│       │   ├── components/        # Vue 组件
│       │   ├── router/            # 路由配置
│       │   └── views/             # 页面视图
│       ├── public/                # 公共资源
│       └── package.json           # 项目配置
│
├── README.md                      # 项目文档
└── .gitignore                     # Git 忽略配置
```

## 🎯 功能模块

| 模块 | 描述 |
|------|------|
| 首页展示 | 精美轮播与快速入口 |
| 灯具鉴赏 | 历代灯具分类展示 |
| 历史地图 | 出土地点可视化 |
| 文化解读 | 深度文化内容 |
| 智能问答 | AI 互动体验 |
| 创意工坊 | 虚拟设计打印 |

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是新功能、功能修复还是文档改进，都可以提交 Pull Request。

1. **Fork** 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📜 许可证

本项目基于 [MIT 许可证](https://opensource.org/licenses/MIT) 开源，您可以自由使用、修改和分发本项目的代码。

## 💬 联系我们

- **GitHub Issues** - 问题反馈与功能建议
- **项目维护者** - fengkai-jinji

---

## 🌌 结语

> *灯火摇曳，光影流转*
> 
> *千年之前的匠人，以智慧为芯，以艺术为油，点燃了这盏不灭的文化之灯*
> 
> *今日，我们接过这束文明的火种*
> *在数字的星河中，为它寻找新的容器*
> 
> *愿这盏古灯，能照亮更多人的心房*
> *愿古老的智慧，能在新的时代继续流淌*
> 
> *—— 流光映古灯，承古人之光，燃今人之情*

---

⭐ 如果这个项目对您有帮助，请为我们点亮一颗星！

*流光映古灯 · 传承千年的光与影*
