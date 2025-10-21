import os
import time
import requests
import random
import json
from flask import Flask, request, jsonify, session
from flask_session import Session  # 用于安全存储 API Key
from flask_cors import CORS

# --- 1. 配置 ---
app = Flask(__name__)

# 密钥是 session 必需的，请替换为您自己的随机字符串
app.config["SECRET_KEY"] = "a_very_secret_random_string_for_your_app"
app.config["SESSION_TYPE"] = "filesystem"  # 使用文件系统存储 session
Session(app)

# [关键] 配置CORS，允许您的前端(例如 localhost:63342)访问
# supports_credentials=True 是让 session 生效所必需的
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:63342"],
)

MODEL_SCOPE_BASE_URL = "https://api-inference.modelscope.cn/"
FLUX_MODEL_ID = "black-forest-labs/FLUX.1-Krea-dev"
QWEN_MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"

# --- 2. 核心：API 密钥管理 ---


@app.route("/api/set_key", methods=["POST"])
def set_key():
    """
    接收前端发来的 API Key 并安全地存储在服务器 session 中
    """
    data = request.json
    api_key = data.get("api_key")
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    # 将 Key 存储在服务器端的 session 中，不会泄露到前端
    session["api_key"] = api_key
    return jsonify({"message": "API key set successfully"}), 200

@app.route('/api/check_key', methods=['GET'])
def check_key():
    """
    检查服务器 session 中是否已存在有效的 API Key。
    """
    if session.get('api_key'):
        return jsonify({"status": "ok"}), 200
    else:
        # 如果 session 中没有 key（例如：已过期、服务器重启），
        # 返回 401 Unauthorized
        return jsonify({"error": "Session invalid or API key not set"}), 401

# --- 3. 内部辅助函数 (Python 逻辑) ---


def get_api_key():
    """从 session 中安全获取 API Key"""
    api_key = session.get("api_key")
    if not api_key:
        raise Exception("API key not set. Please set key in the modal.")
    return api_key


def get_headers(token):
    """获取通用的请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def generate_english_prompt(token, chinese_prompt, context_description):
    """[后端实现] 调用 Qwen 将中文提示词转为英文"""
    system_prompt = """You are a professional AI painting prompt engineer. Your task is to translate the user's Chinese description into a concise, effective English prompt for an image generation model (like FLUX).
ONLY return the English prompt itself, without any conversational text, markdown, greetings, or explanations.
Context: {}""".format(context_description)

    user_prompt = f'Chinese Description: "{chinese_prompt}"'

    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
        headers=get_headers(token),
        json={
            "model": QWEN_MODEL_ID,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 200,
            "temperature": 0.5,
        },
    )
    response.raise_for_status()  # 自动处理 HTTP 错误
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content.replace('"', "").strip()


def submit_sync_generation(token, body):
    """
    [后端实现] 提交“同步”图像生成任务，用于单张图片
    """
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
    """
    [后端实现] 提交“异步”图像生成任务，返回 task_id
    """
    async_headers = {**get_headers(token), "X-ModelScope-Async-Mode": "true"}
    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/images/generations", headers=async_headers, json=body
    )
    response.raise_for_status()
    return response.json()["task_id"]


def poll_generation_result(token, task_id):
    """
    [后端实现] 轮询异步任务直到成功
    """
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
        time.sleep(3)  # [优化] 轮询间隔 3-5 秒


# --- 4. 面向前端的 API 路由 ---


@app.route("/api/generate-steps", methods=["POST"])
def handle_generate_steps():
    """
    [路由] 分步绘画
    """
    try:
        api_key = get_api_key()
        data = request.json
        theme = data.get("theme")
        difficulty = data.get("difficulty")

        step_configs = {
            "初级": [
                "第一步：画一个简单的轮廓",
                "第二步：添加五官",
                "第三步：画上身体",
                "第四步：涂上颜色",
            ],
            "中级": [
                "第一步：构思草图",
                "第二步：明确主体轮廓",
                "第三步：添加背景元素",
                "第四步：细化阴影",
                "第五步：上色和高光",
            ],
            "高级": [
                "第一步：基础构图",
                "第二步：主体轮廓",
                "第三步：添加主要细节",
                "第四步：深入刻画（例如：阴影）",
                "第五步：添加背景和环境",
                "第六步：最终上色和高光",
            ],
        }
        steps_cn = step_configs[difficulty]
        results = []
        constant_seed = random.randint(0, 2**31 - 1)
        previous_image_url = None

        for i, step_desc_full in enumerate(steps_cn):
            chinese_prompt = f"绘画教学步骤图，主题：{theme}，{step_desc_full}"
            english_prompt = generate_english_prompt(
                api_key, chinese_prompt, f"Step {i + 1}/{len(steps_cn)}"
            )

            body = {
                "model": FLUX_MODEL_ID,
                "prompt": english_prompt,
                "seed": constant_seed,
                "size": "1024x1024",
            }
            if previous_image_url:
                body["image_url"] = previous_image_url

            # [关键] 后端使用异步轮询，前端无需等待
            task_id = submit_async_generation_task(api_key, body)
            image_url = poll_generation_result(api_key, task_id)

            results.append(
                {
                    "step": i + 1,
                    "description": step_desc_full.split("：")[1] or step_desc_full,
                    "imageUrl": image_url,
                }
            )
            previous_image_url = image_url

        return jsonify(results)  # 直接返回最终的步骤数组

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-style", methods=["POST"])
def handle_generate_style():
    """
    [路由] 风格工坊
    """
    try:
        api_key = get_api_key()
        data = request.json
        content = data.get("content")
        style = data.get("style")

        style_prompts = {
            "梵高": f"梵高风格，充满活力的笔触，厚涂颜料，主题：{content}",
            "毕加索": f"毕加索立体主义风格，破碎的视角，几何形状，主题：{content}",
            "水墨画": f"中国传统水墨画风格，黑白，留白，意境，主题：{content}",
            "剪纸风格": f"中国剪纸风格，鲜艳的红色，镂空，对称，主题：{content}",
            "水彩画": f"水彩画风格，透明的颜色，湿画法，主题：{content}",
        }
        style_desc = {
            "梵高": "梵高：使用旋转、充满活力的笔触和厚重的颜料来表达情感。",
            "毕加索": "毕加索：通过将物体分解成几何形状来从多个角度展示它们。",
            "水墨画": "水墨画：利用墨色的浓淡变化和笔触的力度来传达意境。",
            "剪纸风格": "剪纸风格：中国传统的民间艺术，通常使用红色纸张和镂空图案。",
            "水彩画": "水彩画：一种使用透明颜料和水在纸上作画的技法。",
        }

        chinese_prompt = style_prompts.get(style, f"{style}风格，{content}")
        english_prompt = generate_english_prompt(
            api_key, chinese_prompt, f"A beautiful artwork in the style of {style}."
        )

        body = {"model": FLUX_MODEL_ID, "prompt": english_prompt, "size": "1024x1024"}

        # 单张图使用同步模式
        image_url = submit_sync_generation(api_key, body)

        return jsonify(
            {
                "imageUrl": image_url,
                "styleDescription": style_desc.get(style, "这是一种独特的艺术风格"),
            }
        )

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask-question", methods=["POST"])
def handle_ask_question():
    """
    [路由] 艺术问答
    """
    try:
        api_key = get_api_key()
        data = request.json
        question = data.get("question")

        user_prompt = f"你是一位友好的艺术老师。请用小学生能轻松理解的、简洁的语言（大约100-150字）回答以下问题：{question}。不要使用复杂的专业术语。"

        response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json={
                "model": QWEN_MODEL_ID,
                "messages": [{"role": "user", "content": user_prompt}],
                "max_tokens": 500,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        # 直接转发 Qwen 的完整响应
        return jsonify(response.json())

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-ideas", methods=["POST"])
def handle_generate_ideas():
    """
    [路由] 创意灵感
    """
    try:
        api_key = get_api_key()
        data = request.json
        theme = data.get("theme")

        # 1. 调用 Qwen 生成创意 JSON
        text_prompt = f"""为主题"{theme}"生成3个绘画创意灵感，适合小学生。请使用严格的JSON格式返回，包含一个 'ideas' 数组，每个对象有 'name' (创意名称), 'description' (一句话描述), 'elements' (3个关键词，用逗号分隔)。
                例如: {{"ideas": [{{"name": "...", "description": "...", "elements": "..."}}]}}"""

        text_response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json={
                "model": QWEN_MODEL_ID,
                "messages": [{"role": "user", "content": text_prompt}],
                "max_tokens": 500,
                "temperature": 0.8,
            },
        )
        text_response.raise_for_status()

        ideas_data = text_response.json()
        content = ideas_data["choices"][0]["message"]["content"]
        json_string = content.replace("```json\n", "").replace("```", "").strip()
        ideas = json.loads(json_string).get("ideas", [])

        # 2. 循环为每个创意生成图片
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
                    "size": "1024x1024",
                }

                idea["exampleImage"] = submit_sync_generation(api_key, img_body)
            except Exception as img_err:
                print(f"Failed to generate image for idea '{idea['name']}': {img_err}")
                idea["exampleImage"] = None  # 即使图片失败，也返回文本
            processed_ideas.append(idea)

        return jsonify(processed_ideas)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


# --- 5. 启动服务器 ---
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)