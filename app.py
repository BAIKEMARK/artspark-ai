import os
import time
import requests
import random
import json
from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS

# --- 1. 配置 (不变) ---
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
QWEN_LLM_ID = "Qwen/Qwen3-30B-A3B-Instruct-2507"  # (您选择的模型)
QWEN_VL_ID = "Qwen/Qwen3-VL-8B-Instruct"  # (您选择的模型)

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


# --- 3. 内部辅助函数 (修复LLM调用) ---


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


def generate_english_prompt(token, chinese_prompt, context_description):
    """[后端实现] 调用 Qwen 将中文提示词转为英文"""
    full_user_prompt = f"""
    You are a professional AI painting prompt engineer. Your task is to translate the user's Chinese description into a concise, effective English prompt for an image generation model (like FLUX).
    ONLY return the English prompt itself, without any conversational text, markdown, greetings, or explanations.
    Context: {context_description}

    Chinese Description: "{chinese_prompt}"
"""
    messages = [{"role": "user", "content": full_user_prompt}]

    # 还原为原始的 payload 结构
    payload = {
        "model": QWEN_LLM_ID,
        "messages": messages,  #  使用 'messages' 作为顶层键
        "max_tokens": 200,
        "temperature": 0.5,
    }

    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
        headers=get_headers(token),
        json=payload,  #
    )
    response.raise_for_status()
    data = response.json()
    #  还原为原始的响应解析
    content = data["choices"][0]["message"]["content"]
    return content.replace('"', "").strip()


def get_style_prompt_from_image(token, base64_image_url):
    payload = {
        "model": QWEN_VL_ID,
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个艺术评论家。请只使用英文单词和短语，详细描述这张图片的视觉风格、纹理、色彩搭配和情感。不要说任何句子，只返回关键词，例如：'swirling clouds, vibrant blues and yellows, stars, texture...'",
                },
                {
                    "role": "user",
                    "content": [
                        {"image": base64_image_url},
                        {"text": "描述这张图片的风格。"},
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

        full_prompt = f"为这张线稿上色，{prompt}, high quality, professional coloring, clean colors"
        english_prompt = generate_english_prompt(
            api_key, full_prompt, "Coloring a lineart image."
        )

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, deformed, lineart",
            "image": base64_image,  # [保留修复] "image" 键
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
        content = data.get("content")
        base64_image = data.get("base64_image")

        style_prompts = {
            "梵高": "梵高风格，充满活力的笔触，厚涂颜料",
            "毕加索": "毕加索立体主义风格，破碎的视角，几何形状",
            "水墨画": "中国传统水墨画风格，黑白，留白，意境",
            "剪纸风格": "中国剪纸风格，鲜艳的红色，镂空，对称",
            "水彩画": "水彩画风格，透明的颜色，湿画法",
        }
        style_desc = {
            "梵高": "梵高：使用旋转、充满活力的笔触和厚重的颜料来表达情感。",
            "毕加索": "毕加索：通过将物体分解成几何形状来从多个角度展示它们。",
            "水墨画": "水墨画：利用墨色的浓淡变化和笔触的力度来传达意境。",
            "剪纸风格": "剪纸风格：中国传统的民间艺术，通常使用红色纸张和镂空图案。",
            "水彩画": "水彩画：一种使用透明颜料和水在纸上作画的技法。",
        }

        style_prompt_text = style_prompts.get(style, f"{style}风格")
        full_chinese_prompt = (
            f"{style_prompt_text}，主题：{content}" if content else style_prompt_text
        )

        english_prompt = generate_english_prompt(
            api_key,
            full_chinese_prompt,
            f"A beautiful artwork in the style of {style}.",
        )

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality",
            "size": "1024x1024",
        }

        if base64_image:
            body["image"] = base64_image

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

        full_prompt = (
            f"一张{style_prompt}风格的肖像画, high quality, professional portrait"
        )
        english_prompt = generate_english_prompt(
            api_key, full_prompt, "A stylized portrait."
        )

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, deformed, multiple heads, bad anatomy",
            "image": base64_image,
            "size": "1024x1024",

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
        content_image = data.get("content_image")
        style_image = data.get("style_image")

        if not content_image or not style_image:
            return jsonify({"error": "内容图片和风格图片都是必需的"}), 400

        style_description = get_style_prompt_from_image(api_key, style_image)
        full_prompt = f"A painting in the style of: {style_description}"

        body = {
            "model": FLUX_MODEL_ID,
            "prompt": full_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, deformed",
            "image": content_image,
            "size": "1024x1024",
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

        user_prompt = f"你是一位友好的艺术老师。请用小学生能轻松理解的、简洁的语言（大约100-150字）回答以下问题：{question}。不要使用复杂的专业术语。"

        # 还原为原始的 payload 结构
        payload = {
            "model": QWEN_LLM_ID,
            "messages": [{"role": "user", "content": user_prompt}],  #
            "max_tokens": 500,
            "temperature": 0.7,
        }

        response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json=payload,  #
        )
        response.raise_for_status()

        #  还原为原始的响应
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

        text_prompt = f"""为主题"{theme}"生成3个绘画创意灵感，适合小学生。请使用严格的JSON格式返回，包含一个 'ideas' 数组，每个对象有 'name' (创意名称), 'description' (一句话描述), 'elements' (3个关键词，用逗号分隔)。
                例如: {{"ideas": [{{"name": "...", "description": "...", "elements": "..."}}]}}"""

        # 还原为原始的 payload 结构
        payload = {
            "model": QWEN_LLM_ID,
            "messages": [{"role": "user", "content": text_prompt}],  #
            "max_tokens": 500,
            "temperature": 0.8,
        }

        text_response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=get_headers(api_key),
            json=payload,  #
        )
        text_response.raise_for_status()

        ideas_data = text_response.json()
        content = ideas_data["choices"][0]["message"]["content"]
        json_string = content.replace("```json\n", "").replace("```", "").strip()
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


# --- 5. 启动服务器 (不变) ---
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)