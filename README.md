# 🎨 艺启智AI - 乡村美术助教

“艺启智AI”是一个AI驱动的Web应用，旨在为中小学教师提供零门槛、专业化的美术教学支持。

本项目通过集成先进的AI模型（如ModelScope的FLUX和Qwen系列），提供一系列易于使用的美术创作和辅助工具，帮助教师激发学生的创造力，并为他们提供丰富的艺术灵感和知识。

## ✨ 主要功能

该平台围绕六大核心功能构建：

1.  **AI智能上色 (AI Smart Coloring)**

      * 用户上传一张线稿或简笔画，并提供简单的上色风格描述（例如：“水彩画, 明亮的颜色”）。
      * AI将自动为线稿生成专业、色彩丰富的彩色图片。

2.  **创意风格工坊 (Creative Style Workshop)**

      * 用户可以选择一种预设的艺术风格（如梵高、毕加索、水墨画等），并选择性地上传草图或输入内容描述。
      * AI将根据所选风格和输入内容，创作一幅全新的艺术作品。

3.  **AI自画像 (AI Self-Portrait)**

      * 用户上传一张自己的照片，并输入想要的风格（例如：“迪士尼卡通, 像素风”）。
      * AI会将其照片转换成对应风格的肖像画。

4.  **艺术融合 (Art Fusion)**

      * 用户上传一张“内容图片”（如宠物照片）和一张“风格图片”（如星空图）。
      * AI将提取风格图的视觉特征，并将其“刷”到内容图上，生成融合后的艺术品。

5.  **艺术知识问答 (Art Knowledge Q\&A)**

      * 一个面向学生的艺术百科全书。用户可以输入任何艺术相关的问题（例如：“什么是水墨画？”）。
      * AI（Qwen LLM）将以简洁易懂的语言提供答案。

6.  **创意灵感生成 (Creative Idea Generator)**

      * 当教师需要绘画主题时，可输入一个关键词（如：“春天”）。
      * AI将生成3个包含创意名称、描述和关键元素的绘画灵感，并为每个灵感生成一张示例图片。

## 🛠️ 技术栈

本项目采用前后端分离架构。

### **前端 (Client)**

  * **HTML5**
  * **CSS3:** 使用原生CSS，包含变量、Flexbox、Grid布局和动画。
  * **Vanilla JavaScript (ES6+):** 使用 `async/await` 和 `fetch` API 与后端通信，无任何外部框架依赖。

### **后端 (Server)**

  * **Python 3**
  * **Flask:** 作为Web框架，提供RESTful API接口。
  * **Flask-Session:** 用于在服务器端安全地管理用户的API Key。
  * **Flask-CORS:** 处理跨域请求。
  * **Requests:** 用于与外部ModelScope API通信。

### **外部AI服务**

  * **ModelScope (魔搭):** 作为所有AI功能的核心后端。
      * **LLM (文本生成):** `Qwen/Qwen3-30B-A3B-Instruct-2507` (用于艺术问答、创意生成、提示词翻译)。
      * **VL (多模态):** `Qwen/Qwen3-VL-8B-Instruct` (用于艺术融合中的风格识别)。
      * **Image Gen (图像生成):** `black-forest-labs/FLUX.1-Krea-dev` (用于所有图像生成任务)。

## ⚙️ 架构概览

1.  **认证:** 用户在前端输入他们的ModelScope API Key。
2.  **会话存储:** API Key通过 `/api/set_key` 接口发送到Flask后端，并安全地存储在服务器的\*\*会话 (Session)\*\*中。前端仅在 `localStorage` 中保留一个“已设置”的标记。
3.  **前端请求:** 当用户使用任一功能时（例如“AI上色”），前端将图像（转为Base64）和提示词发送到Flask后端的相应路由（例如 `/api/colorize-lineart`）。
4.  **后端处理:**
      * Flask服务器从**会话**中检索API Key。
      * 对于需要中文转英文的任务（如上色、自画像），后端会先调用Qwen LLM将中文提示词转为优化的英文提示词。
      * 后端使用该Key和处理后的提示词，向ModelScope API（例如FLUX模型）发起异步生成请求。
      * 服务器轮询ModelScope任务状态，直到获取到最终的图像URL。
5.  **结果显示:** Flask将包含结果（例如 `imageUrl`）的JSON响应返回给前端，前端将其显示给用户。

## 🚀 部署与运行

### **先决条件**

  * Python 3.7+
  * 一个有效的 **ModelScope API Key** (可从 [modelscope.cn](https://www.modelscope.cn/my/myaccesstoken) 获取)

### **1. 后端设置 (Flask Server)**

1.  克隆（或下载）项目文件到本地。

2.  打开一个终端，进入项目根目录。

3.  安装Python依赖项：

    ```bash
    pip install -r requirements.txt
    ```

4.  启动Flask服务器：

    ```bash
    python app.py
    ```

5.  服务器现在运行在 `http://localhost:7680`。

### **2. 前端运行 (Client)**

1.  **直接打开:** 在现代浏览器中直接打开 `index.html` 文件。
2.  **推荐方式 (使用本地服务器):**
      * 由于浏览器安全策略，建议从一个本地服务器访问 `index.html`。
      * 后端 `app.py` 中的CORS配置已预先允许了来自 `http://localhost:63342` 和 `http://127.0.0.1:63342` 的请求，这些是IDE（如PyCharm或WebStorm）中常见的本地服务器端口。
      * 您也可以使用VSCode的 "Live Server" 插件，或在项目目录中运行：
        ```bash
        python -m http.server 63342 
        ```
        (然后访问 `http://localhost:63342`)

### **3. 开始使用**

1.  在浏览器中打开前端页面。
2.  系统会首先弹出一个模态框，要求输入您的ModelScope API Key。
3.  输入API Key后，点击“进入美术馆”，即可开始使用所有功能。