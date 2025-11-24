# 🎨 艺启智AI (ArtSpark AI) - 乡村美育助教平台



“艺启智AI”是一个基于 **Vue 3** 和 **Python Flask** 构建的现代化 AI 美育教学平台。

本项目专为中小学（特别是乡村地区）美术教师设计，旨在通过先进的 AI 技术（通义万相、Qwen、FLUX 等）解决美术教学资源匮乏的问题，并创新性地融合了**心理学**元素，关注留守儿童的心理健康。



## ✨ 核心功能 (Features)



平台围绕“学、想、练”的教学闭环设计，包含六大核心模块：

### 1. 学 (Learn) - 艺术知识库

- **🏛️ 名画鉴赏室 (Art Gallery)**
  - **功能**：对接大都会艺术博物馆 (Met) API，提供海量名画数据。
  - **AI赋能**：集成腾讯云翻译消除语言障碍；独创 **“AI讲解”** 功能，AI 助教（小艺）会根据学生年龄段（如6-8岁或13-15岁），用生动或深度的语言解读名画。
- **🤖 艺术小百科 (Art Q&A)**
  - **功能**：基于大语言模型 (LLM) 的智能问答助手。
  - **特性**：支持多轮对话，能根据设定的“教学情景”（学生年龄）自动调整回答的语气和复杂度，是孩子们的 7x24 小时艺术老师。



### 2. 想 (Ideate) - 创意启发

- **💡 创意灵感生成器 (Idea Generator)**
  - **功能**：教师输入主题（如“春天”），AI 自动生成 3 个包含名称、描述和关键元素的创意方案，并同步生成示例图供参考。
- **❤️ 心情画板 (Mood Painting) [特色]**
  - **功能**：融合心理学的艺术疗愈工具。
  - **机制**：采用“校验-赋能”心理学模型。学生选择心情（如“难过”）和主题，AI 不会生硬说教，而是生成一个接纳情绪并赋予正向力量的绘画创意（例如：“画一间空荡的房间[校验]，但地板缝隙中长出了一棵发光的树[赋能]”）。



### 3. 练 (Create) - 创作实践

- AI智能上色 (Smart Coloring)
  - **功能**：学生上传线稿，AI 根据提示词（如“水彩风”）一键上色，帮助学生理解色彩搭配。
- 创意工坊 (Creative Workshop)
  - **功能**：风格迁移教学工具。支持“文本指令”模式（如“把校园变成梵高风格”）和“图像风格”模式（上传参考图进行风格融合）。
- 人像工坊 (Portrait Workshop)
  - **功能**：将学生照片转化为多种艺术风格（如“3D童话”、“国风工笔”、“二次元”等），增加课堂趣味性。

------



## 🛠️ 技术栈 (Tech Stack)

本项目采用 **前后端分离** 架构。

### **前端 (Frontend)**

- **Framework**: [Vue 3](https://vuejs.org/) (Composition API, `<script setup>`)
- **State Management**: [Pinia](https://pinia.vuejs.org/) (管理 Auth 和 Settings 状态)
- **UI Library**: [Element Plus](https://element-plus.org/) (全套 UI 组件)
- **Styling**: SCSS + CSS Variables (支持深色/自定义主题配置)
- **Icons**: Phosphor Icons (`@phosphor-icons/web`)
- **Markdown**: `marked` (用于渲染 AI 的富文本回答)

### **后端 (Backend)**

- **Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
- **API Protocol**: RESTful API
- **AI Integration**:
  - **阿里云 DashScope SDK** (通义千问 Qwen-Plus, 通义万相 Wanx 系列)
  - **ModelScope** (通过 HTTP 请求调用 FLUX, Qwen-VL 等开源模型)
- **Cloud Services**:
  - **Tencent Cloud TMT**: 机器翻译服务
  - **Cloudflare R2 (AWS S3 Compatible)**: 对象存储，用于处理图片上传

------



## ⚙️ 核心逻辑架构



1. **分层适配系统 (Adaptive System)**:
   - 前端 `SettingsSidebar.vue` 允许教师设置“学生年龄”（6-8岁, 9-10岁...）。
   - 后端 `prompt.py` 中预置了多套 Prompt 模板（如 `ART_QA_USER`, `PSYCH_ART_PROMPT`），根据前端传来的年龄参数动态调整 AI 的人设和输出复杂度。
2. **双轨 AI 引擎 (Dual-Engine)**:
   - **ModelScope 模式**: 适合使用开源模型（如 FLUX.1-Krea）。
   - **Bailian (DashScope) 模式**: 适合追求更高稳定性和速度（使用 Wanx2.1, Qwen-Max）。
   - 系统会自动根据任务类型（文生图、图生图、对话）选择最优模型。

------



## 🚀 部署与运行 (Getting Started)

### 前置要求

- **Node.js** (v16+)
- **Python** (3.8+)
- **API Keys**:
  - ModelScope API Key
  - DashScope API Key (阿里云百炼)
  - *(可选)* Tencent Cloud SecretId/Key (用于翻译功能)
  - *(可选)* R2/S3 存储配置 (用于图片上传功能

### 1. 后端启动 (Backend)

进入 `backend` 目录并运行 Flask 服务：

```
cd backend

# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 配置环境变量 (建议创建 .env 文件，参考 app.py 中的配置)
# 确保配置了 FLUX, Qwen 等模型的 ID 和必要的 Key

# 3. 启动服务
python app.py
# 服务将运行在 http://localhost:7860
```

> **注意**：`app.py` 配置了 CORS 允许跨域请求，方便前后端独立开发调试。



### 2. 前端启动 (Frontend)

进入根目录（包含 `package.json` 的目录）：

```
# 1. 安装 Node 依赖
npm install

# 2. 启动开发服务器
npm run dev
# 前端页面通常运行在 http://localhost:5173
```



### 3. 正式使用

1. 打开前端页面，系统会检测登录状态。

2. 首次使用需在弹窗或设置中输入 **ModelScope API Key** 进行认证（Key 安全存储于本地 Session 中）。

3. 在右下角“设置”中，可以选择 AI 平台（ModelScope / DashScope）及目标学生年龄段。

   

## 📁 项目结构

```
ArtSpark-AI/
├── backend/
│   ├── api.py             # Flask API 路由定义
│   ├── app.py             # Flask 应用主入口
│   ├── prompt.py          # AI 提示词模板
│   ├── requirements.txt   # Python 依赖
│   ├── services.py        # 与 ModelScope API 交互的服务
│   └── utils.py           # 辅助工具函数
├── frontend/
│   ├── public/
│   │   └── img/           # 存放公共图片资源
│   ├── src/
│   │   ├── components/    # Vue.js 可复用组件
│   │   ├── composables/   # Vue.js 组合式函数
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── styles/        # 全局 CSS 样式
│   │   ├── views/         # 主要功能视图组件
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 前端入口文件
│   ├── index.html         # HTML 入口
│   ├── package.json       # Node.js 依赖
│   └── vite.config.js     # Vite 配置文件
├── .gitignore             # Git 忽略配置
├── .env.example       # 环境变量配置文件
├── Dockerfile             # Docker 配置文件
└── README.md              # 项目说明
```
