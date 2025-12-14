# 🎨 艺启智AI (ArtSpark AI) - 乡村美育助教平台



> **“用 AI 点亮大山里的审美与创意，守护每一颗孤独的童心。”**

“艺启智AI”是一个专为乡村中小学设计的现代化美育教学平台。我们不只是提供工具，更是通过先进的 AI 技术（通义万相、Qwen-VL、FLUX 等），致力于解决乡村教育中**审美资源匮乏、专业师资不足、留守儿童心理关怀缺失**的三大难题。

我们核心提供四重价值保障：**审美培养、创意思维培养、知识普惠（打破信息差）、心理健康支持**。

------



## ✨ 核心功能 (Core Features)

我们将所有功能模块融入到了一个温暖的教育叙事中：

### 1. 审美培养与知识普惠 (Aesthetics & Knowledge)

> *“打破城乡信息差，让乡村孩子也能拥有全球顶级的艺术视野。”*

- **🏛️ 名画鉴赏室 (Art Gallery)**
  - **功能**：对接大都会艺术博物馆 (Met) API，将世界级博物馆搬进乡村教室。
  - **AI 赋能**：独创 **“分龄 AI 讲解”**。小艺助教能识别学生年龄（6岁或15岁），用童话隐喻或历史背景等不同方式深度解读名画，并打破语言障碍，让高雅艺术“听得懂、喜欢看”。
- **🤖 艺术小百科 (Art Q&A)**
  - **功能**：基于大语言模型 (LLM) 的 7x24 小时百科助教。
  - **价值**：解决乡村教师非专业出身、知识面受限的问题。无论是“梵高为什么割耳朵”还是“什么是波普艺术”，都能给出准确且有趣的回答。



### 2. 创意思维与技能实践 (Creativity & Practice)

> *“不仅给灵感，更给脚手架。拒绝 AI 代画，坚持 AI 助学。”*

- **🎨 创意绘练 (Creative Drawing Practice) [核心升级]**
  - **痛点解决**：解决学生“想画不敢画”、老师“不会评画”的难题。
  - **教学闭环**：
    1. **生成教材**：输入天马行空的创意，AI 生成**适合临摹的简笔线稿**（脚手架），而非完美成品图。
    2. **线下实践**：鼓励学生回归纸笔，锻炼手眼协调与线条控制力。
    3. **慧眼点评**：**Qwen-VL 视觉大模型** 化身老师，识别学生作业，从构图、线条等维度给予鼓励式点评和改进建议。
- **🖍️ AI 智能上色 (Smart Coloring)**
  - **功能**：学生上传线稿，AI 提供多种配色方案（水彩、厚涂等）。
  - **价值**：帮助学生直观理解色彩关系，培养色彩感知力。
- **🖼️ 风格工坊 (Creative & Portrait Workshop)**
  - **功能**：包含“创意工坊”与“人像工坊”。
  - **价值**：通过 AI 风格迁移技术，让学生直观感受“梵高风”、“国画风”、“赛博朋克”等不同艺术流派的视觉特征，激发创造力。



### 3. 心理健康支持 (Mental Health)

> *“每一幅画背后，都藏着孩子想说的话。”*

- **❤️ 心情画板 (Mood Painting) [公益特色]**
  - **功能**：融合心理学的艺术疗愈工具，关注留守儿童内心世界。
  - **机制**：内置 **“校验-赋能”** 心理学模型。当学生表达负面情绪（如“孤独”）时，AI 生成的画面会先“接纳”这种情绪（如雨夜），再巧妙植入“希望”元素（如一盏灯），实现无声的心理疏导。



### 4. 易用性与乡村适配 (Accessibility & Adaptation)

> *“设备不设限，交互零门槛。为乡村真实教学场景量身定制。”*

- **🎙️ 全局语音交互 (Voice Input)**
  - **场景洞察**：在触控大屏上使用软键盘打字极其繁琐，且低龄儿童拼音熟练度低，传统的文字输入方式严重拖慢课堂节奏。
  - **适配方案**：全站核心功能集成 **DashScope 语音识别 (ASR)**。
    - **动口不动手**：无论是在大屏前还是手机上，孩子只需按住说话：“我想画一只在大海里游泳的猫”，AI 即可精准识别。这不仅解决了打字难的问题，更让课堂互动如聊天般自然高效。
- **🌐 多语言国际化支持 (Internationalization)**
  - **功能**：基于 Vue I18n 的完整多语言支持系统，目前支持中文简体和英文。
  - **价值**：为海外华人学校、国际学校提供本土化体验，同时为未来拓展到"一带一路"沿线国家做好技术储备。
- **💬 用户反馈系统 (Feedback System)**
  - **功能**：集成钉钉机器人的实时反馈收集系统，用户可随时提交使用建议和问题反馈。
  - **价值**：建立产品与用户的直接沟通渠道，持续优化产品体验，确保真正解决乡村教育痛点。
- **📱 全场景响应式设计 (Responsive Design)**
  - **场景洞察**：乡村学校普遍已配备多媒体触控一体机，但仍存在少数情况，或多媒体设备故障情况；同时需兼顾课后手机使用场景。
  - **适配方案**：
    - **触屏优化**：针对教室电子白板/一体机的大屏环境优化了按钮尺寸与交互逻辑，老师和学生在**无键鼠**情况下也能流畅点击操作。
    - **移动端兜底**：完美适配手机端。既方便老师随时查看备课，也为没有电脑的学生家庭提供“手机拍照交作业”的保底通道。



## 🛠️ 技术栈 (Tech Stack)

本项目采用 **前后端分离** 架构。

### **前端 (Frontend)**

- **Framework**: [Vue 3](https://vuejs.org/) (Composition API, `<script setup>`)
- **State Management**: [Pinia](https://pinia.vuejs.org/) (管理 Auth 和 Settings 状态)
- **UI Library**: [Element Plus](https://element-plus.org/) (全套 UI 组件)
- **Styling**: SCSS + CSS Variables (支持深色/自定义主题配置)
- **Icons**: Phosphor Icons (`@phosphor-icons/web`)
- **Markdown**: `marked` (用于渲染 AI 的富文本回答)
- **Internationalization**: [Vue I18n](https://vue-i18n.intlify.dev/) (多语言国际化支持)
- **HTTP Client**: [Axios](https://axios-http.com/) (API 请求处理)

### **后端 (Backend)**

- **Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
- **API Protocol**: RESTful API
- **AI Integration**:
  - **阿里云 DashScope SDK** (通义千问 Qwen-Plus, 通义万相 Wanx 系列)
  - **ModelScope** (通过 HTTP 请求调用 FLUX, Qwen-VL 等开源模型)
  - **OpenAI Compatible API**: 兼容 OpenAI 格式的 API 调用
- **Cloud Services**:
  - **Tencent Cloud TMT**: 机器翻译服务
  - **Cloudflare R2 (AWS S3 Compatible)**: 对象存储，用于处理图片上传
  - **Audio (ASR)**: Paraformer-Realtime (语音识别)
- **Additional Libraries**:
  - **Pillow**: 图像处理
  - **PyDub**: 音频处理
  - **Gunicorn**: WSGI HTTP 服务器 (生产环境部署)

------

## ⚙️ 核心逻辑架构

1. **分层适配系统 (Adaptive System)**:
   - 前端设置“学生年龄”后，后端 `prompt.py` 会动态调整 AI 的策略：
   - **对低龄 (6-8岁)**：生成几何简笔画，讲解用词童趣，点评关注“胆量与兴趣”。
   - **对高龄 (13-15岁)**：生成素描线稿，讲解深入历史，点评关注“透视与结构”。
2. **教学闭环设计 (Pedagogical Loop)**:
   - **Input (AI)**: 提供“线稿脚手架”，降低门槛。
   - **Action (Student)**: 强制“线下动手”，保留纸笔训练。
   - **Feedback (AI)**: 利用多模态大模型 (VL) 实现即时反馈。
3. **双轨 AI 引擎**:
   - **ModelScope**: 灵活调用开源模型 (FLUX, Qwen-VL)。
   - **DashScope (阿里云百炼)**: 提供高性能服务 (Wanx2.1, Qwen-Plus)。

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

### 3. Docker 部署 (Production)

项目提供了完整的 Docker 部署方案，适合生产环境：

```bash
# 1. 构建 Docker 镜像
docker build -t artspark-ai .

# 2. 运行容器
docker run -d \
  --name artspark-ai \
  -p 7860:7860 \
  -e MODELSCOPE_API_KEY=your_modelscope_key \
  -e DASHSCOPE_API_KEY=your_dashscope_key \
  artspark-ai

# 3. 访问应用
# 应用将在 http://localhost:7860 运行
```

> **Docker 特性**：
> - 多阶段构建，优化镜像大小
> - 自动集成前端构建和后端服务
> - 内置 Gunicorn WSGI 服务器，适合生产环境
> - 支持音频处理 (ffmpeg) 和图像处理 (Pillow)



### 4. 正式使用

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
│   │   │   ├── ApiKeyModal.vue      # API Key 配置弹窗
│   │   │   ├── FeedbackForm.vue     # 用户反馈表单
│   │   │   ├── LanguageSwitcher.vue # 语言切换器
│   │   │   ├── VoiceInputButton.vue # 语音输入按钮
│   │   │   └── ...        # 其他UI组件
│   │   ├── composables/   # Vue.js 组合式函数
│   │   ├── i18n/          # 国际化配置
│   │   │   ├── locales/   # 语言包
│   │   │   │   ├── zh-CN.json # 中文语言包
│   │   │   │   └── en-US.json # 英文语言包
│   │   │   └── index.js   # i18n 配置入口
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── styles/        # 全局 CSS 样式
│   │   ├── views/         # 主要功能视图组件
│   │   │   ├── ArtGalleryView.vue   # 名画鉴赏
│   │   │   ├── IdeaGeneratorView.vue # 创意绘练
│   │   │   ├── MoodPaintingView.vue  # 心情画板
│   │   │   ├── LineColoringView.vue  # AI智能上色
│   │   │   ├── StyleWorkshopView.vue # 风格工坊
│   │   │   └── ArtQAView.vue        # 艺术小百科
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

------

## 📞 联系我们 (Contact)

如果您在使用过程中遇到问题，或有任何建议和反馈，欢迎通过以下方式联系我们：

- **应用内反馈**：点击右下角反馈按钮，直接提交问题和建议
- **GitHub Issues**：在项目仓库提交 Issue
- **邮箱联系**：[请在此处添加联系邮箱]

我们致力于为乡村教育提供更好的 AI 美育解决方案，您的每一个反馈都是我们前进的动力！

---

*"让每一个乡村孩子都能享受到优质的美育资源，用 AI 点亮他们的创意之光。"* ✨