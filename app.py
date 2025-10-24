import os
import time
import requests
import json
import boto3
import uuid
import base64
from io import BytesIO
from flask import Flask, request, jsonify, send_file, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from requests.exceptions import HTTPError
from PIL import Image
from prompt import PROMPTS

class ApiKeyMissingError(Exception):
    """当 session 中缺少 API key 时引发"""
    pass

# --- 1. 配置 ---
load_dotenv()

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:63342", "http://127.0.0.1:63342"]}}
)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
API_KEY_SALT = os.getenv("API_KEY_SALT")
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

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
    region_name='auto'
)

# --- 2. 核心：API 密钥管理 ---

def get_headers(token):
    """[V11 移至此处] 辅助函数，验证和后续调用都需要用到"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def validate_modelscope_key(api_key):
    """[V11 新增] 尝试调用 ModelScope 以验证 API Key 的有效性"""
    try:
        headers = get_headers(api_key)
        # 使用 Qwen LLM 进行一个轻量级的“测试”调用
        payload = {
            "model": QWEN_LLM_ID,
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 1,
        }
        response = requests.post(
            f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10  # 设置10秒超时
        )

        # 401 = Unauthorized. Key是无效的。
        if response.status_code == 401:
            return False
        if response.ok:
            return True
        return False

    except requests.exceptions.RequestException as e:
        print(f"Key validation request failed: {e}")
        return False


@app.route("/api/set_key", methods=["POST"])
def set_key():
    try:
        data = request.json
        api_key = data.get("api_key")
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        if not validate_modelscope_key(api_key):
            return jsonify({"error": "API Key 无效、已过期或网络错误"}), 401
        token = ts.dumps(api_key, salt=API_KEY_SALT) # 加密 API Key
        return jsonify({"message": "API key set successfully", "token": token}), 200
    except UnicodeEncodeError:
        return jsonify({"error": "API Key 包含非法字符，请输入有效的Key"}), 400
    except Exception as e:
        print(f"set_key error: {e}")
        return handle_api_errors(e)


@app.route("/api/check_key", methods=["GET"])
def check_key():
    try:
        get_api_key() # 尝试解密
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401


# --- 路由：用于解决CORS的图片下载代理 ---
@app.route("/api/proxy-download")
def proxy_download():
    image_url = request.args.get("url")
    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        image_data = BytesIO(response.content)
        mime_type = response.headers.get('Content-Type', 'image/png')

        return send_file(
            image_data,
            mimetype=mime_type,
            as_attachment=True,
            download_name='art-ai-image.png'
        )

    except requests.exceptions.RequestException as e:
        print(f"Proxy download error: {e}")
        return jsonify({"error": f"Failed to fetch image: {e}"}), 500


# --- 3. 内部辅助函数 ---

def get_api_key():
    # [V10 修改] 从 URL Query 参数中获取 token，以兼容创空间环境
    token = request.args.get("token")

    if not token:
        # [V10 修改] 更新错误信息
        raise ApiKeyMissingError("Token is missing from query parameters. (token=...).")

    try:
        # 解密 Token，设置有效期为 30 天 (2592000 秒)
        api_key = ts.loads(token, salt=API_KEY_SALT, max_age=2592000)
        return api_key
    except SignatureExpired:
        raise ApiKeyMissingError("Token has expired. Please re-enter API Key.")
    except BadTimeSignature:
        raise ApiKeyMissingError("Invalid token. Please re-enter API Key.")
    except Exception as e:
        print(f"Token decryption error: {e}")
        raise ApiKeyMissingError("Invalid token.")

def get_ai_config(data):
    """从请求数据中提取 AI 配置，并提供默认值"""
    config = {
        "chat_model": data.get("config_chat_model", QWEN_LLM_ID),
        "vl_model": data.get("config_vl_model", QWEN_VL_ID),
        "image_model": data.get("config_image_model", FLUX_MODEL_ID),
        "age_range": data.get("config_age_range", "6-8岁"), # 默认年龄
    }
    return config

# 尺寸计算辅助函数
def round_to_64(x):
    """将尺寸调整为 64 的最接近倍数，最小为 64"""
    return max(64, int(round(x / 64.0)) * 64)

# 辅助函数：计算自适应尺寸
def calculate_adaptive_size(width, height, target_dim=1024):
    """根据原始宽高比计算新的尺寸，使最长边为 target_dim，并圆整到 64"""
    if width == 0 or height == 0:
        return f"{target_dim}x{target_dim}" # 备用

    if width > height:
        # 横向 (Landscape)
        aspect_ratio = height / width
        new_width = target_dim
        new_height = int(new_width * aspect_ratio)
    else:
        # 纵向或方形 (Portrait or Square)
        aspect_ratio = width / height
        new_height = target_dim
        new_width = int(new_height * aspect_ratio)

    # 圆整到 64 的倍数
    final_width = round_to_64(new_width)
    final_height = round_to_64(new_height)

    # 避免返回 0
    if final_width == 0: final_width = 64
    if final_height == 0: final_height = 64

    return f"{final_width}x{final_height}"

# R2 上传辅助函数
def upload_to_r2(base64_string):
    try:
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        image_bytes = BytesIO(data)
        # 从字节中读取图像尺寸
        with Image.open(image_bytes) as img:
            width, height = img.size
        image_bytes.seek(0)
        mime_type = header.split(";")[0].split(":")[-1]
        extension = mime_type.split("/")[-1]
        file_name = f"uploads/{uuid.uuid4()}.{extension}"
        s3_client.upload_fileobj(
            image_bytes,
            R2_BUCKET_NAME,
            file_name,
            ExtraArgs={
                'ContentType': mime_type,
                'ACL': 'public-read'
            }
        )
        public_url = f"{R2_PUBLIC_URL_BASE}/{file_name}"
        return public_url, width, height
    except Exception as e:
        print(f"R2 Upload Error: {e}")
        raise Exception(f"Failed to upload image to R2 OSS: {e}")

def generate_english_prompt(token, chinese_prompt, context_description):
    """[后端实现] 调用 Qwen 将中文提示词转为英文"""

    full_user_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
        context=context_description,
        chinese_description=chinese_prompt
    )
    data = request.json
    config=get_ai_config(data)
    messages = [{"role": "user", "content": full_user_prompt}]
    payload = {
        "model": config["chat_model"],
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


def get_style_prompt_from_image(token, base64_image_url, vl_model_id):
    system_prompt = PROMPTS["STYLE_ANALYSIS_SYSTEM"]
    user_text = PROMPTS["STYLE_ANALYSIS_USER"]

    payload = {
        "model": vl_model_id,
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": base64_image_url}, # 修正图片部分的结构
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        "max_tokens": 300,
        "temperature": 0.6,
    }
    response = requests.post(
        f"{MODEL_SCOPE_BASE_URL}v1/chat/completions",
        headers=get_headers(token),
        json=payload,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("choices") and data["choices"][0].get("message"):
        return data["choices"][0]["message"]["content"]
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


# --- 4. 面向前端的 API 路由  ---

# 定义一个通用的错误处理函数
def handle_api_errors(e):
    if isinstance(e, ApiKeyMissingError):
        # Token 解密失败或过期
        return jsonify({"error": str(e)}), 401
    if isinstance(e, HTTPError):
        # ModelScope 返回了 4xx 或 5xx 错误
        if e.response.status_code == 401:
            # 关键：将 ModelScope 的 401 错误传递给前端
            return jsonify({"error": "API Key 无效或已过期 (来自 ModelScope)"}), 401
        else:
            # ModelScope 的其他错误 (如 500, 400)
            return jsonify({"error": f"ModelScope API 错误 (HTTP {e.response.status_code}): {str(e)}"}), 502
    # 其他所有 Python 内部错误
    print(f"An unexpected error occurred: {e}")
    return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


# 路由一：AI智能上色
@app.route("/api/colorize-lineart", methods=["POST"])
def handle_colorize_lineart():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        base64_image = data.get("base64_image")
        prompt = data.get("prompt")

        if not base64_image:
            return jsonify({"error": "线稿图片是必需的"}), 400

        public_url, w, h = upload_to_r2(base64_image)
        adaptive_size = calculate_adaptive_size(w, h)

        full_prompt = PROMPTS["COLORIZE_PROMPT_CN"].format(prompt=prompt)
        english_prompt = generate_english_prompt(
            api_key, full_prompt, "Coloring a lineart image."
        )
        body = {
            "model": config["image_model"], # [V17]
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, grayscale, monochrome, sketch, unfinished, lineart",
            "image_url": public_url,
            "size": adaptive_size,
        }

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify({"imageUrl": image_url})

    except Exception as e:
        return handle_api_errors(e)


# 路由二：创意风格工坊
@app.route("/api/generate-style", methods=["POST"])
def handle_generate_style():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data) # [V17]
        style = data.get("style")
        content = data.get("content", "")
        base64_image = data.get("base64_image")

        style_prompts = PROMPTS["STYLE_PROMPTS_CN"]
        style_desc = PROMPTS["STYLE_DESCRIPTIONS_CN"]

        style_prompt_text = style_prompts.get(style, f"{style}风格")

        quality_boost = PROMPTS["STYLE_QUALITY_BOOST_CN"]
        if content:
            full_chinese_prompt = PROMPTS["STYLE_PROMPT_WITH_CONTENT_CN"].format(
                style_text=style_prompt_text,
                quality_boost=quality_boost,
                content=content
            )
        else:
            full_chinese_prompt = PROMPTS["STYLE_PROMPT_WITHOUT_CONTENT_CN"].format(
                style_text=style_prompt_text,
                quality_boost=quality_boost
            )


        english_prompt = generate_english_prompt(
            api_key,
            full_chinese_prompt,
            f"A beautiful artwork in the style of {style}."
        )

        body = {
            "model": config["image_model"],
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, bad anatomy",
        }

        adaptive_size = "1024x1024"
        if base64_image:
            public_url, w, h = upload_to_r2(base64_image)
            body["image_url"] = public_url
            adaptive_size = calculate_adaptive_size(w, h)

        body["size"] = adaptive_size

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify(
            {
                "imageUrl": image_url,
                "styleDescription": style_desc.get(style, "这是一种独特的艺术风格"),
            }
        )
    except Exception as e:
        return handle_api_errors(e)


# 路由三：AI自画像
@app.route("/api/self-portrait", methods=["POST"])
def handle_self_portrait():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        base64_image = data.get("base64_image")
        style_prompt = data.get("style_prompt")

        if not base64_image:
            return jsonify({"error": "照片是必需的"}), 400
        if not style_prompt:
            return jsonify({"error": "风格是必需的"}), 400

        public_url, w, h = upload_to_r2(base64_image)
        adaptive_size = calculate_adaptive_size(w, h)

        full_prompt = PROMPTS["SELF_PORTRAIT_PROMPT_CN"].format(style_prompt=style_prompt)

        english_prompt = generate_english_prompt(
            api_key,
            full_prompt,
            "A stylized portrait, maintaining likeness to the original photo."
        )

        body = {
            "model": config["image_model"],
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, multiple heads, bad anatomy, extra limbs, mutation, gender swap",
            "image_url": public_url,
            "size": adaptive_size,
            "strength": 0.65
        }
        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)
        return jsonify({"imageUrl": image_url})

    except Exception as e:
        return handle_api_errors(e)


# 路由四：艺术融合
@app.route("/api/art-fusion", methods=["POST"])
def handle_art_fusion():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        content_image_b64 = data.get("content_image")
        style_image_b64 = data.get("style_image")

        if not content_image_b64 or not style_image_b64:
            return jsonify({"error": "内容图片和风格图片都是必需的"}), 400

        content_url, w, h = upload_to_r2(content_image_b64)
        adaptive_size = calculate_adaptive_size(w, h)

        # 识图使用动态 VL 模型
        style_description = get_style_prompt_from_image(api_key, style_image_b64, config["vl_model"])

        full_prompt = PROMPTS["ART_FUSION_PROMPT_EN"].format(style_description=style_description)

        body = {
            "model": config["image_model"], # [V17]
            "prompt": full_prompt,
            "negative_prompt": "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, bad anatomy",
            "image_url": content_url,
            "size": adaptive_size,
            "strength": 0.6
        }

        task_id = submit_async_generation_task(api_key, body)
        image_url = poll_generation_result(api_key, task_id)

        return jsonify({"imageUrl": image_url})

    except Exception as e:
        return handle_api_errors(e)


# 路由五：艺术问答
@app.route("/api/ask-question", methods=["POST"])
def handle_ask_question():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data) # [V17]
        question = data.get("question")

        user_prompt = PROMPTS["ART_QA_USER"].format(
            question=question,
            age_range=config["age_range"]
        )

        payload = {
            "model": config["chat_model"], # [V17]
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
        return handle_api_errors(e)


# 路由六：创意灵感
@app.route("/api/generate-ideas", methods=["POST"])
def handle_generate_ideas():
    try:
        api_key = get_api_key()
        data = request.json
        config = get_ai_config(data) # [V17]
        theme = data.get("theme")
        text_prompt = PROMPTS["IDEA_GENERATOR_USER"].format(
            theme=theme,
            age_range=config["age_range"]
        )
        payload = {
            "model": config["chat_model"], # [V17]
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

        # 增加健壮性，防止 JSON.loads 失败
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            raise Exception("LLM did not return valid JSON.")

        json_string = content[json_start : json_end]
        ideas = json.loads(json_string).get("ideas", [])
        processed_ideas = []
        for idea in ideas:
            try:
                img_prompt_cn = PROMPTS["IDEA_IMAGE_PROMPT_CN"].format(
                    name=idea['name'],
                    description=idea['description'],
                    elements=idea['elements']
                )

                img_prompt_en = generate_english_prompt(
                    api_key,
                    img_prompt_cn,
                    "A simple, colorful illustration for a child.",
                )
                img_body = {
                    "model": config["image_model"],
                    "prompt": img_prompt_en,
                    "negative_prompt": "text, watermark, signature, blurry, low quality, ugly, deformed",
                    "size": "1024x1024",
                }
                idea["exampleImage"] = submit_sync_generation(api_key, img_body)
            except Exception as img_err:
                print(f"Failed to generate image for idea '{idea['name']}': {img_err}")
                idea["exampleImage"] = None
                if (
                    isinstance(img_err, HTTPError)
                    and img_err.response.status_code == 401
                ):
                    raise img_err
            processed_ideas.append(idea)

        return jsonify(processed_ideas)

    except Exception as e:
        return handle_api_errors(e)


MET_API_BASE = "https://collectionapi.metmuseum.org/public/collection/v1"


# 路由七：艺术画廊搜索
@app.route("/api/gallery/search", methods=["POST"])
def handle_gallery_search():
    try:
        data = request.json

        # 1. 构建搜索参数
        search_params = {
            "q": data.get("q", "*"), # 从辅助搜索框获取
            "hasImages": "true",
            "isPublicDomain": "true"
        }

        # 动态添加所有筛选条件
        if data.get("departmentId"):
            search_params["departmentId"] = data.get("departmentId")
        if data.get("isHighlight"):
            search_params["isHighlight"] = data.get("isHighlight")
        if data.get("medium"):
            search_params["medium"] = data.get("medium")
        if data.get("geoLocation"):
            search_params["geoLocation"] = data.get("geoLocation")
        if data.get("dateBegin"):
            search_params["dateBegin"] = data.get("dateBegin")
        if data.get("dateEnd"):
            search_params["dateEnd"] = data.get("dateEnd")

        # 2. 调用搜索 API (获取 Object IDs)
        search_url = f"{MET_API_BASE}/search"
        search_res = requests.get(search_url, params=search_params, timeout=10)
        search_res.raise_for_status()
        search_data = search_res.json()

        object_ids = search_data.get("objectIDs", [])
        if not object_ids:
            return jsonify({"artworks": [], "total": 0})

        # 3. 只获取前 20 个作品的详细信息
        artworks = []
        # [修改] 我们只取前20个ID
        for obj_id in object_ids[:20]:
            try:
                obj_url = f"{MET_API_BASE}/objects/{obj_id}"
                obj_res = requests.get(obj_url, timeout=5)
                obj_res.raise_for_status()
                obj_data = obj_res.json()

                # 筛选我们需要的数据，确保有图
                if obj_data.get("primaryImageSmall"):
                    artworks.append(
                        {
                            "id": obj_data.get("objectID"),
                            "title": obj_data.get("title", "N/A"),
                            "artist": obj_data.get("artistDisplayName", "Unknown"),
                            "date": obj_data.get("objectDate", "N/A"),
                            "medium": obj_data.get("medium", "N/A"),
                            "country": obj_data.get("country", "N/A"),
                            "imageUrl": obj_data.get("primaryImageSmall"),  # 使用小图
                            "metUrl": obj_data.get(
                                "objectURL", "#"
                            ),  # 指向Met官网的链接
                        }
                    )
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch object {obj_id}: {e}")
                continue  # 跳过这个作品

        return jsonify({"artworks": artworks, "total": search_data.get("total", 0)})

    except requests.exceptions.RequestException as http_err:
        return jsonify({"error": f"Met API 错误: {str(http_err)}"}), 502
    except Exception as e:
        # 这个不能用 handle_api_errors, 因为它不涉及 ApiKeyMissingError
        print(f"An unexpected error occurred in gallery search: {e}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


# 路由八：获取所有展厅
@app.route("/api/gallery/departments", methods=["GET"])
def handle_gallery_departments():
    try:
        dept_url = f"{MET_API_BASE}/departments"
        dept_res = requests.get(dept_url, timeout=10)
        dept_res.raise_for_status()
        return jsonify(dept_res.json())
    except Exception as e:
        return jsonify({"error": f"Met API 错误: {str(e)}"}), 502

# --- 4.5. 静态文件服务 (为 Docker 部署新增) ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/img/<path:filename>')
def serve_image(filename):
    return send_from_directory('img', filename)


# --- 5. 启动服务器 ---
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=7860)