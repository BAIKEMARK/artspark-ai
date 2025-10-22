import os
import time
import requests
import json
import boto3
import uuid
import base64
from io import BytesIO
from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv

# --- 1. 配置 ---
load_dotenv() # 加载 .env 文件

app = Flask(__name__)

app.config["SECRET_KEY"] = "a_very_secret_random_string_for_your_app"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:63342", "http://127.0.0.1:63342"],
)

MODEL_SCOPE_BASE_URL = "https://api-inference.modelscope.cn/"
FLUX_MODEL_ID = "black-forest-labs/FLUX.1-Krea-dev"
QWEN_LLM_ID = "Qwen/Qwen3-30B-A3B-Instruct-2507"
QWEN_VL_ID = "Qwen/Qwen3-VL-8B-Instruct"

# --- R2 S3 客户端配置 ---
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL_BASE = os.getenv("R2_PUBLIC_URL_BASE")

s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto' # Cloudflare R2 通常使用 'auto'
)

# --- 2. 核心：API 密钥管理 (不变) ---

@app.route("/api/set_key", methods=["POST"])
def set_key():
    data = request.json
    api_key = data.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    session["api_key"] = api_key
    return jsonify({"message": "API key set successfully"}), 200


@app.route("/api/check_key", methods=["GET"])
def check_key():
    if session.get("api_key"):
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"error": "Session invalid or API key not set"}), 401


# --- 路由：用于解决CORS的图片下载代理 ---
@app.route("/api/proxy-download")
def proxy_download():
    image_url = request.args.get("url")
    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        # 使用 requests 下载图片
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # 确保请求成功

        # 将响应内容作为字节流
        image_data = BytesIO(response.content)

        # 确定 mime-type (从响应头获取，如果失败则默认为 png)
        mime_type = response.headers.get('Content-Type', 'image/png')

        # 使用 send_file 将图片流式传输回前端
        return send_file(
            image_data,
            mimetype=mime_type,
            as_attachment=True, # 告诉浏览器这是一个附件
            download_name='art-ai-image.png' # 默认文件名 (前端会覆盖)
        )

    except requests.exceptions.RequestException as e:
        print(f"Proxy download error: {e}")
        return jsonify({"error": f"Failed to fetch image: {e}"}), 500


# --- 3. 内部辅助函数 ---


def get_api_key():
    api_key = session.get("api_key")
    if not api_key:
        raise Exception("API key not set. Please set key in the modal.")
    return api_key


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

# R2 上传辅助函数
def upload_to_r2(base64_string):
    """将 Base64 字符串解码并上传到 R2, 返回公网 URL"""
    try:
        # 1. 解码 Base64
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)

        # 提取 mime-type (例如: "image/png")
        mime_type = header.split(";")[0].split(":")[-1]

        # 提取文件扩展名 (例如: "png")
        extension = mime_type.split("/")[-1]

        # 2. 生成唯一文件名
        file_name = f"uploads/{uuid.uuid4()}.{extension}"

        # 3. 上传到 R2
        s3_client.upload_fileobj(
            BytesIO(data),       # 文件字节流
            R2_BUCKET_NAME,      # 存储桶
            file_name,           # 文件在存储桶中的路径
            ExtraArgs={
                'ContentType': mime_type,
                'ACL': 'public-read' # [可选] 如果您的R2桶是私有的，这很有用
            }
        )

        # 4. 返回公网 URL
        public_url = f"{R2_PUBLIC_URL_BASE}/{file_name}"
        return public_url

    except Exception as e:
        print(f"R2 Upload Error: {e}")
        raise Exception("Failed to upload image to R2 OSS.")

def generate_english_prompt(token, chinese_prompt, context_description):
    """[后端实现] 调用 Qwen 将中文提示词转为英文"""
    full_user_prompt = f"""
<task>
You are an expert AI art prompt translator and enhancer. Your job is to translate a Chinese description into a vivid, concise, and high-quality English prompt suitable for the FLUX image model.

1.  Translate the core meaning of the Chinese description.
2.  Enrich the prompt with 2-3 professional "quality modifier" keywords (e.g., 'masterpiece', 'best quality', 'vibrant colors', 'dynamic lighting', 'cinematic', 'detailed').
3.  Keep the context in mind.

**Rules:**
-   **ONLY** output the final English prompt.
-   **DO NOT** include any conversational text, markdown, or explanations.
</task>

<context>
{context_description}
</context>

<chinese_description>
{chinese_prompt}
</chinese_description>
"""
    messages = [{"role": "user", "content": full_user_prompt}]

    # 还原为原始的 payload 结构
    payload = {
        "model": QWEN_LLM_ID,
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.5,
    }

    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
        headers=get_headers(token),
        json=payload
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content.replace('"', "").strip()


def get_style_prompt_from_image(token, base64_image_url):

    system_prompt = """
        You are an expert style analysis bot. Your sole purpose is to analyze an image and extract its visual style as a comma-separated list of keywords for an AI art model.
        
        **Rules:**
        -   Focus on: **visual style** (e.g., 'oil painting', 'watercolor', '3d render'), **texture**, **color palette**, **lighting**, and **mood**.
        -   Use ONLY English keywords and short phrases.
        -   Separate all terms with a comma.
        -   DO NOT use full sentences or conversational language.
        
        **Example Output:**
        'oil painting, impasto, thick brush strokes, swirling clouds, vibrant blues and yellows, dynamic, expressive'
        """

    payload = {
        "model": QWEN_VL_ID,
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"image": base64_image_url},
                        {"text": "Analyze the style of this image based on the rules."},
                    ],
                },
            ]
        },
        "parameters": {"max_tokens": 300, "temperature": 0.6},
    }
    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/services/aigc/multimodal-generation/generation",
        headers=get_headers(token),
        json=payload,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("output"):
        return data["output"]["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Qwen-VL API Error: {data.get('message', 'Unknown error')}")

def submit_sync_generation(token, body):
    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/images/generations",
        headers=get_headers(token),
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("images") and data["images"][0].get("url"):
        return data["images"][0]["url"]
    raise Exception(f"API Error (Sync): {data.get('message', 'Unknown error')}")


def submit_async_generation_task(token, body):
    async_headers = {**get_headers(token), "X-ModelScope-Async-Mode": "true"}
    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/images/generations", headers=async_headers, json=body
    )
    response.raise_for_status()
    return response.json()["task_id"]


def poll_generation_result(token, task_id):
    poll_headers = {**get_headers(token), "X-ModelScope-Task-Type": "image_generation"}
    while True:
        result = requests.get(
            f"{MODEL_SCOPE_BASE_URL}v1/tasks/{task_id}", headers=poll_headers
        )
        result.raise_for_status()
        data = result.json()
        if data["task_status"] == "SUCCEED":
            return data["output_images"][0]
        elif data["task_status"] == "FAILED":
            raise Exception(f"Task failed: {data.get('task_message', 'Unknown error')}")
        time.sleep(3)


# --- 4. 面向前端的 API 路由 (保留Img2Img修复) ---


# 路由一：AI智能上色
@app.route("/api/colorize-lineart", methods=["POST"])
def handle_colorize_lineart():
    try:
        api_key = get_api_key()
        data = request.json
        base64_image = data.get("base64_image")
        prompt = data.get("prompt")

        if not base64_image:
            return jsonify({"error": "线稿图片是必需的"}), 400

        public_url = upload_to_r2(base64_image)

        # [优化] 强化中文提示词，加入质量词
        full_prompt = f"为这张线稿上色。风格：{prompt}。要求：杰作, 最高质量, 色彩鲜艳, 细节丰富, 专业上色, 干净的阴影。"
        english_prompt = generate_english_prompt(
            api_key, full_prompt, "Coloring a lineart image."
        )

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, grayscale, monochrome, sketch, unfinished, lineart",
            "image_url": public_url,
            "size": "1024x1024",
        }

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify({"imageUrl": image_url})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# 路由二：创意风格工坊
@app.route("/api/generate-style", methods=["POST"])
def handle_generate_style():
    try:
        api_key = get_api_key()
        data = request.json
        style = data.get("style")
        content = data.get("content", "")
        base64_image = data.get("base64_image")

        style_prompts = {
            "梵高": "梵高风格, 杰作, 厚涂颜料, 充满活力的旋转笔触, 鲜艳的色彩",
            "毕加索": "毕加索立体主义风格, 杰作, 破碎的视角, 几何形状, 抽象",
            "水墨画": "中国传统水墨画, 意境深远, 留白, 笔触有力, 墨色浓淡",
            "剪纸风格": "中国剪纸艺术, 杰作, 鲜艳的红色, 镂空, 对称美学",
            "水彩画": "水彩画风格, 色彩透明, 渲染, 湿画法, 明亮"
        }
        style_desc = {
            "梵高": "梵高：使用旋转、充满活力的笔触和厚重的颜料来表达情感。",
            "毕加索": "毕加索：通过将物体分解成几何形状来从多个角度展示它们。",
            "水墨画": "水墨画：利用墨色的浓淡变化和笔触的力度来传达意境。",
            "剪纸风格": "剪纸风格：中国传统的民间艺术，通常使用红色纸张和镂空图案。",
            "水彩画": "水彩画：一种使用透明颜料和水在纸上作画的技法。",
        }

        style_prompt_text = style_prompts.get(style, f"{style}风格")

        quality_boost = "杰作, 最高质量, 8k, 细节丰富"
        if content:
             full_chinese_prompt = f"{style_prompt_text}, {quality_boost}。主题：{content}"
        else:
             full_chinese_prompt = f"{style_prompt_text}, {quality_boost}"


        english_prompt = generate_english_prompt(
            api_key, full_chinese_prompt, f"A beautiful artwork in the style of {style}."
        )

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, bad anatomy",
            "size": "1024x1024"
        }

        if base64_image:
            public_url = upload_to_r2(base64_image)
            body["image_url"] = public_url

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify(
            {
                "imageUrl": image_url,
                "styleDescription": style_desc.get(style, "这是一种独特的艺术风格"),
            }
        )

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# 路由三：AI自画像
@app.route("/api/self-portrait", methods=["POST"])
def handle_self_portrait():
    try:
        api_key = get_api_key()
        data = request.json
        base64_image = data.get("base64_image")
        style_prompt = data.get("style_prompt")

        if not base64_image:
            return jsonify({"error": "照片是必需的"}), 400
        if not style_prompt:
            return jsonify({"error": "风格是必需的"}), 400

        public_url = upload_to_r2(base64_image)

        full_prompt = f"一张{style_prompt}风格的肖像画。杰作, 最高质量, 细节丰富。关键：必须保持输入照片中人物的面部特征和相似性。"
        english_prompt = generate_english_prompt(api_key, full_prompt, "A stylized portrait, maintaining likeness to the original photo.")

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            # [优化] 更严格的负向提示词
            "negative_prompt": "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, multiple heads, bad anatomy, extra limbs, mutation, gender swap",
            "image_url": public_url,
            "size": "1024x1024",
            "strength": 0.45
        }

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify({"imageUrl": image_url})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# 路由四：艺术融合
@app.route("/api/art-fusion", methods=["POST"])
def handle_art_fusion():
    try:
        api_key = get_api_key()
        data = request.json
        content_image_b64 = data.get("content_image")
        style_image_b64 = data.get("style_image")

        if not content_image_b64 or not style_image_b64:
            return jsonify({"error": "内容图片和风格图片都是必需的"}), 400

        content_url = upload_to_r2(content_image_b64)
        style_description = get_style_prompt_from_image(api_key, style_image_b64)

        # 明确指示AI“融合”风格和内容
        full_prompt = f"A masterpiece painting. Apply the following style: [{style_description}]. The composition and subject MUST be based on the input image."

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": full_prompt,
            "negative_prompt": "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, bad anatomy", # (已优化)
            "image_url": content_url,
            "size": "1024x1024",
            "strength": 0.6 # [新增] 艺术融合需要更高的 'strength' 来吸收风格
        }

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify({"imageUrl": image_url})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# 路由五：艺术问答
@app.route("/api/ask-question", methods=["POST"])
def handle_ask_question():
    try:
        api_key = get_api_key()
        data = request.json
        question = data.get("question")

        user_prompt = f"""
            <role>
            你是一位非常出色、友好的乡村艺术老师，你的名字叫“小艺”。
            </role>
            
            <audience>
            你的听众是小学生（6-10岁）。
            </audience>
            
            <task>
            用**非常简单、有趣、鼓励性**的语言回答下面的问题。
            </task>
            
            <rules>
            1.  **称呼：** 一定要以“嗨，小朋友！”或“你好呀！”开头。
            2.  **简洁：** 答案保持在100-150字左右。
            3.  **易懂：** 绝对不要使用任何复杂的专业术语。
            4.  **风格：** 像讲故事一样，多用比喻。
            </rules>
            
            <question>
            {question}
            </question>
            """
        payload = {
            "model": QWEN_LLM_ID,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 500,
            "temperature": 0.7,
        }

        response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()

        return jsonify(response.json())

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# 路由六：创意灵感
@app.route("/api/generate-ideas", methods=["POST"])
def handle_generate_ideas():
    try:
        api_key = get_api_key()
        data = request.json
        theme = data.get("theme")

        text_prompt = f"""
            <role>
            你是一个充满想象力的儿童艺术创意总监。
            </role>
            
            <audience>
            目标是给小学生（6-10岁）提供绘画灵感。
            </audience>
            
            <task>
            为主题 “{theme}” 生成 3 个独特且有趣的绘画创意。
            </task>
            
            <format_instructions>
            你必须严格按照下面的JSON格式返回，不要有任何JSON之外的文字、注释或markdown。
            <json_schema>
            {{
                "ideas": [
                    {{
                        "name": "创意名称 (例如：彩虹雨下的毛毛虫)",
                        "description": "一句话的有趣描述 (例如：一只毛毛虫撑着一片叶子在彩虹色的雨滴下散步)",
                        "elements": "3个关键词 (例如：彩虹, 毛毛虫, 叶子)"
                    }},
                    {{
                        "name": "...",
                        "description": "...",
                        "elements": "..."
                    }},
                    {{
                        "name": "...",
                        "description": "...",
                        "elements": "..."
                    }}
                ]
            }}
            </json_schema>
            </format_instructions>
            """

        payload = {
            "model": QWEN_LLM_ID,
            "messages": [{"role": "user", "content": text_prompt}],
            "max_tokens": 800,
            "temperature": 0.8,
        }

        text_response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json=payload
        )
        text_response.raise_for_status()

        ideas_data = text_response.json()
        content = ideas_data["choices"][0]["message"]["content"]
        json_string = content[content.find('{') : content.rfind('}')+1]

        ideas = json.loads(json_string).get("ideas", [])

        # 循环为每个创意生成图片
        processed_ideas = []
        for idea in ideas:
            try:
                img_prompt_cn = f"绘画创意示例：{idea['name']}，{idea['description']}，包含元素：{idea['elements']}"
                img_prompt_en = generate_english_prompt(
                    api_key,
                    img_prompt_cn,
                    "A simple, colorful illustration for a child.",
                )
                img_body = {
                    "model": FLUX_MODEL_ID,
                    "prompt": img_prompt_en,
                    "negative_prompt": "text, watermark, signature, blurry, low quality, ugly, deformed",
                    "size": "1024x1024",
                }
                idea["exampleImage"] = submit_sync_generation(api_key, img_body)
            except Exception as img_err:
                print(f"Failed to generate image for idea '{idea['name']}': {img_err}")
                idea["exampleImage"] = None
            processed_ideas.append(idea)

        return jsonify(processed_ideas)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# --- 4.5. 静态文件服务 (为 Docker 部署新增) ---
# 确保API路由优先

@app.route('/')
def serve_index():
    #
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    #
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    #
    return send_from_directory('.', 'script.js')

@app.route('/img/<path:filename>')
def serve_image(filename):
    #
    return send_from_directory('img', filename)


# --- 5. 启动服务器 ---
if __name__ == '__main__':
    # [修改] 监听 0.0.0.0 以便 Docker 容器可以从外部访问，并关闭 debug 模式
    app.run(debug=False, host='0.0.0.0', port=7860)