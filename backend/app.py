import os
import time
import requests
import json
import base64
from io import BytesIO
from flask import Flask, request, jsonify, send_file, send_from_directory, current_app
from dotenv import load_dotenv
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from requests.exceptions import HTTPError
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# --- 1. 导入本地模块 ---
from prompt import PROMPTS
from utils import (
    ApiKeyMissingError,
    get_api_key,
    get_headers,
    handle_api_errors,
    get_ai_config,
    calculate_adaptive_size
)
from services import (
    validate_modelscope_key,
    upload_to_r2,
    translate_text_tencent,
    generate_english_prompt,
    get_style_prompt_from_image,
    submit_sync_generation,
    submit_async_generation_task,
    poll_generation_result,
    run_llm_chat,
    run_llm_generation
)

# --- 2. 配置 ---
load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')

CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": "*" }}
)

# --- 2.1 应用配置 ---
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["API_KEY_SALT"] = os.getenv("API_KEY_SALT")

# 将 ts 序列化器放入 app config，以便 utils 可以访问
app.config["ts"] = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# --- 2.2 模型和 API 配置 ---
app.config["MODEL_SCOPE_BASE_URL"] = "https://api-inference.modelscope.cn/"
app.config["FLUX_MODEL_ID"] = "black-forest-labs/FLUX.1-Krea-dev"
app.config["QWEN_LLM_ID"] = "Qwen/Qwen3-30B-A3B-Instruct-2507"
app.config["QWEN_VL_ID"] = "Qwen/Qwen3-VL-8B-Instruct"
app.config["MET_API_BASE"] = "https://collectionapi.metmuseum.org/public/collection/v1"


# --- 3. 核心路由 (认证与代理) ---

@app.route("/api/set_key", methods=["POST"])
def set_key():
    try:
        data = request.json
        api_key = data.get("api_key")
        if not api_key:
            return jsonify({"error": "API key is required"}), 400

        # 调用 services 中的验证函数
        if not validate_modelscope_key(api_key):
            return jsonify({"error": "API Key 无效、已过期或网络错误"}), 401

        # 使用 utils 中的序列化器
        ts = current_app.config["ts"]
        token = ts.dumps(api_key, salt=current_app.config["API_KEY_SALT"])

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
        return handle_api_errors(e)


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


# --- 4. AI 功能路由 ---

@app.route("/api/colorize-lineart", methods=["POST"])
def handle_colorize_lineart():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)
        base64_image = data.get("base64_image")
        prompt = data.get("prompt")

        if not base64_image:
            return jsonify({"error": "线稿图片是必需的"}), 400

        public_url, w, h = upload_to_r2(base64_image)
        adaptive_size = calculate_adaptive_size(w, h)

        full_prompt = PROMPTS["COLORIZE_PROMPT_CN"].format(
            prompt=prompt,
            age_range=config["age_range"]
        )
        english_prompt = generate_english_prompt(
            headers, config, full_prompt, "Coloring a lineart image."
        )

        body = {
            "model": config["image_model"],
            "prompt": english_prompt,
            "negative_prompt": "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, grayscale, monochrome, sketch, unfinished, lineart",
            "image_url": public_url,
            "size": adaptive_size,
        }

        task_id = submit_async_generation_task(headers, body)
        image_url = poll_generation_result(headers, task_id)

        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/generate-style", methods=["POST"])
def handle_generate_style():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)
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
            headers, config,
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

        task_id = submit_async_generation_task(headers, body)
        image_url = poll_generation_result(headers, task_id)

        return jsonify(
            {
                "imageUrl": image_url,
                "styleDescription": style_desc.get(style, "这是一种独特的艺术风格"),
            }
        )
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/self-portrait", methods=["POST"])
def handle_self_portrait():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
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
            headers, config,
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
        task_id = submit_async_generation_task(headers, body)
        image_url = poll_generation_result(headers, task_id)
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/art-fusion", methods=["POST"])
def handle_art_fusion():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)
        content_image_b64 = data.get("content_image")
        style_image_b64 = data.get("style_image")

        if not content_image_b64 or not style_image_b64:
            return jsonify({"error": "内容图片和风格图片都是必需的"}), 400

        content_url, w, h = upload_to_r2(content_image_b64)
        adaptive_size = calculate_adaptive_size(w, h)

        style_description = get_style_prompt_from_image(
            headers, config, style_image_b64
        )
        full_prompt = PROMPTS["ART_FUSION_PROMPT_EN"].format(style_description=style_description)

        body = {
            "model": config["image_model"],
            "prompt": full_prompt,
            "negative_prompt": "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, bad anatomy",
            "image_url": content_url,
            "size": adaptive_size,
            "strength": 0.6
        }

        task_id = submit_async_generation_task(headers, body)
        image_url = poll_generation_result(headers, task_id)
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/ask-question", methods=["POST"])
def handle_ask_question():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)
        messages = data.get("messages")

        if not messages:
            return jsonify({"error": "Messages are required"}), 400

        system_prompt = PROMPTS["ART_QA_USER"].format(
            age_range=config["age_range"]
        )

        response_json = run_llm_chat(headers, config, messages, system_prompt)
        return jsonify(response_json)
    except Exception as e:
        return handle_api_errors(e)

def _process_idea_image_worker(idea, api_key, image_model, base_url):
    """
    (工作线程) 在单独的线程中为单个 "idea" 生成图像。
    接收所有必需的上下文作为参数。
    """
    img_prompt_en = idea.get("img_prompt_en")
    if not img_prompt_en:
        idea["exampleImage"] = None
        return idea
    try:
        img_body = {
            "model": image_model,
            "prompt": img_prompt_en,
            "negative_prompt": "text, watermark, signature, blurry, low quality, ugly, deformed",
            "size": "1024x1024",
        }
        idea_headers = get_headers(api_key)

        idea["exampleImage"] = submit_sync_generation(
            idea_headers,
            img_body,
            base_url
        )
    except Exception as img_err:
        print(f"Failed to generate image for idea '{idea['name']}': {img_err}")
        idea["exampleImage"] = None
        if (
            isinstance(img_err, HTTPError)
            and img_err.response.status_code == 401
        ):
            # 向上抛出认证错误，以便主线程捕获
            raise ApiKeyMissingError("Auth failed during parallel image gen.")
    idea.pop("img_prompt_en", None)
    return idea

@app.route("/api/generate-ideas", methods=["POST"])
def handle_generate_ideas():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)
        theme = data.get("theme")

        image_model = config["image_model"]
        base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

        # 1. 生成创意文本
        text_prompt = PROMPTS["IDEA_GENERATOR_USER"].format(
            theme=theme,
            age_range=config["age_range"]
        )
        ideas_data = run_llm_generation(headers, config, text_prompt)
        content = ideas_data["choices"][0]["message"]["content"]

        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            raise Exception("LLM did not return valid JSON.")
        json_string = content[json_start : json_end]
        ideas = json.loads(json_string).get("ideas", [])

        # 2. 批量翻译提示词
        chinese_prompts_list = []
        for idea in ideas:
            img_prompt_cn = PROMPTS["IDEA_IMAGE_PROMPT_CN"].format(
                name=idea['name'],
                description=idea['description'],
                elements=idea['elements'],
                age_range=config["age_range"]
            )
            chinese_prompts_list.append(img_prompt_cn)

        batch_translator_prompt = PROMPTS["BATCH_PROMPT_TRANSLATOR"].format(
            json_input_list=json.dumps(chinese_prompts_list)
        )

        translate_response = run_llm_generation(
            headers, config, batch_translator_prompt, max_tokens=1000, temp=0.5
        )

        content = translate_response["choices"][0]["message"]["content"]
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        if json_start == -1 or json_end == 0:
            raise Exception("LLM did not return valid JSON list for translation.")
        translated_prompts_list = json.loads(content[json_start : json_end])

        if len(translated_prompts_list) != len(ideas):
            raise Exception("Batch translation returned a different number of prompts.")

        ideas_with_prompts = []
        for i, idea in enumerate(ideas):
            idea["img_prompt_en"] = translated_prompts_list[i]
            ideas_with_prompts.append(idea)

        # --- 3. 并发生成图像 ---
        worker_with_context = partial(
            _process_idea_image_worker,
            api_key=api_key,
            image_model=image_model,
            base_url=base_url
        )

        processed_ideas = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(worker_with_context, ideas_with_prompts)
            processed_ideas = list(results)

        return jsonify(processed_ideas)
    except Exception as e:
        return handle_api_errors(e)


# --- 5. 名画鉴赏室路由 (MET API) ---

@app.route("/api/gallery/search", methods=["POST"])
def handle_gallery_search():
    try:
        data = request.json
        met_api_base = current_app.config["MET_API_BASE"]

        # 1. 构建搜索参数
        search_params = {
            "q": data.get("q", "*"),
            "hasImages": "true",
            "isPublicDomain": "true"
        }
        if data.get("departmentId"): search_params["departmentId"] = data.get("departmentId")
        if data.get("isHighlight"): search_params["isHighlight"] = data.get("isHighlight")
        if data.get("medium"): search_params["medium"] = data.get("medium")
        if data.get("geoLocation"): search_params["geoLocation"] = data.get("geoLocation")
        if data.get("dateBegin"): search_params["dateBegin"] = data.get("dateBegin")
        if data.get("dateEnd"): search_params["dateEnd"] = data.get("dateEnd")

        # 2. 调用搜索 API
        search_url = f"{met_api_base}/search"
        search_res = requests.get(search_url, params=search_params, timeout=10)
        search_res.raise_for_status()
        search_data = search_res.json()

        object_ids = search_data.get("objectIDs", [])
        if not object_ids:
            return jsonify({"artworks": [], "total": 0})

        # 3. 获取前 20 个作品详情
        artworks_raw = []
        for obj_id in object_ids[:20]:
            try:
                obj_url = f"{met_api_base}/objects/{obj_id}"
                obj_res = requests.get(obj_url, timeout=5)
                obj_res.raise_for_status()
                obj_data = obj_res.json()
                if obj_data.get("primaryImageSmall"):
                    artworks_raw.append({
                        "id": obj_data.get("objectID"),
                        "title": obj_data.get("title", "N/A"),
                        "artist": obj_data.get("artistDisplayName", "Unknown"),
                        "date": obj_data.get("objectDate", "N/A"),
                        "medium": obj_data.get("medium", "N/A"),
                        "country": obj_data.get("country", "N/A"),
                        "imageUrl": obj_data.get("primaryImageSmall"),
                        "metUrl": obj_data.get("objectURL", "#"),
                        "original_title": obj_data.get("title", "N/A"),
                        "original_artist": obj_data.get("artistDisplayName", "Unknown"),
                        "original_medium": obj_data.get("medium", "N/A"),
                    })
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch object {obj_id}: {e}")
                continue

        # 4. 批量翻译
        if artworks_raw:
            titles_en = [art.get("original_title", "") for art in artworks_raw]
            artists_en = [art.get("original_artist", "") for art in artworks_raw]
            mediums_en = [art.get("original_medium", "") for art in artworks_raw]

            titles_zh = translate_text_tencent(titles_en)
            artists_zh = translate_text_tencent(artists_en)
            mediums_zh = translate_text_tencent(mediums_en)

            for i, art in enumerate(artworks_raw):
                art["title"] = titles_zh[i] if i < len(titles_zh) else art["original_title"]
                art["artist"] = artists_zh[i] if i < len(artists_zh) else art["original_artist"]
                art["medium"] = mediums_zh[i] if i < len(mediums_zh) else art["original_medium"]

        return jsonify({"artworks": artworks_raw, "total": search_data.get("total", 0)})

    except requests.exceptions.RequestException as http_err:
        return jsonify({"error": f"Met API 错误: {str(http_err)}"}), 502
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/gallery/departments", methods=["GET"])
def handle_gallery_departments():
    try:
        met_api_base = current_app.config["MET_API_BASE"]
        dept_url = f"{met_api_base}/departments"
        dept_res = requests.get(dept_url, timeout=10)
        dept_res.raise_for_status()
        return jsonify(dept_res.json())
    except Exception as e:
        return jsonify({"error": f"Met API 错误: {str(e)}"}), 502

@app.route("/api/gallery/explain", methods=["POST"])
def handle_gallery_explain():
    try:
        api_key = get_api_key()
        headers = get_headers(api_key)
        data = request.json
        config = get_ai_config(data)

        # 1. 获取作品信息 (英文原文)
        art_info_en = {
            "title": data.get("title", "N/A"),
            "artist": data.get("artist", "N/A"),
            "medium": data.get("medium", "N/A"),
            "date": data.get("date", "N/A"),
        }

        # 2. 获取 AI 讲解
        ai_user_prompt = PROMPTS["ARTWORK_EXPLAINER"].format(
            age_range=config["age_range"],
            **art_info_en
        )
        ai_explanation = run_llm_chat(
            headers, config, [], ai_user_prompt
        )["choices"][0]["message"]

        # 3. 翻译原文信息
        try:
            to_translate = [
                f"作品名称: {art_info_en['title']}",
                f"艺术家: {art_info_en['artist']}",
                f"媒介: {art_info_en['medium']}",
                f"创作日期: {art_info_en['date']}"
            ]
            translated_list = translate_text_tencent(to_translate)

            if translated_list and len(translated_list) == len(to_translate):
                original_description_zh = "\n".join(translated_list)
            else:
                original_description_zh = "\n".join([f"Title: {art_info_en['title']}", ...])

        except Exception as e:
            print(f"Error translating original artwork info: {e}")
            original_description_zh = "\n".join([
                f"Title: {art_info_en['title']}",
                f"Artist: {art_info_en['artist']}",
                f"Medium: {art_info_en['medium']}",
                f"Date: {art_info_en['date']}"
            ])

        # 4. 返回结果
        return jsonify({
            "ai_explanation": ai_explanation,
            "original_description_zh": original_description_zh
        })
    except Exception as e:
        return handle_api_errors(e)

# --- 6. 静态文件服务与启动 ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=7860)