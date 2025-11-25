import os
import requests # 确保导入 requests
from io import BytesIO
from flask import Flask, request, jsonify, send_file, send_from_directory, current_app
from dotenv import load_dotenv
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer


# --- 1. 导入本地模块 ---
from utils import (
    get_api_key,
    handle_api_errors,
    get_ai_config,
)
from services import (
    validate_modelscope_key,
    translate_text_tencent,
    generate_colorization,
    generate_creative_workshop,
    generate_portrait_workshop,
    run_chat_completion,
    generate_ideas,
    generate_mood_painting,
    generate_artwork_explanation,
    transcribe_audio_dashscope,
    critique_student_work
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
app.config["ts"] = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# --- 2.2 模型和 API 配置 (最终版) ---
# ModelScope
app.config["MODEL_SCOPE_BASE_URL"] = "https://api-inference.modelscope.cn/"
app.config["MS_FLUX_MODEL_ID"] = "black-forest-labs/FLUX.1-Krea-dev"
app.config["MS_QWEN_LLM_ID"] = "Qwen/Qwen3-30B-A3B-Instruct-2507"
app.config["MS_QWEN_VL_ID"] = "Qwen/Qwen3-VL-8B-Instruct"

# 阿里云 DashScope (灵积)
app.config["DASHSCOPE_API_BASE_URL"] = "https://dashscope.aliyuncs.com/api/v1"
app.config["DASHSCOPE_OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
app.config["DS_LLM_ID"] = "qwen-plus" # LLM 默认
app.config["DS_VL_ID"] = "qwen-vl-plus" # 识图
app.config["DS_WANX21_IMAGE_EDIT_ID"] = "wanx2.1-imageedit" # 通用编辑 (上色, 创意工坊)
app.config["DS_PORTRAIT_STYLE_ID"] = "wanx-style-cosplay-v1" # 人像风格化 (人像工坊)
app.config["DS_T2I_TURBO_ID"] = "wanx2.1-t2i-turbo" # 用于创意灵感的文生图模型

# 第三方
app.config["MET_API_BASE"] = "https://collectionapi.metmuseum.org/public/collection/v1"


# --- 3. 核心路由 (认证与代理) ---

@app.route("/api/set_key", methods=["POST"])
def set_key():
    try:
        data = request.json
        api_key = data.get("api_key")
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        if not validate_modelscope_key(api_key):
            return jsonify({"error": "API Key 无效、已过期或网络错误"}), 401
        ts = current_app.config["ts"]
        token = ts.dumps(api_key, salt=current_app.config["API_KEY_SALT"])
        return jsonify({"message": "API key set successfully", "token": token}), 200
    except UnicodeEncodeError:
        return jsonify({"error": "API Key 包含非法字符，请输入有效的Key"}), 400
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/check_key", methods=["GET"])
def check_key():
    try:
        get_api_key() # 尝试解密 ModelScope Key (登录凭证)
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
        return jsonify({"error": f"Failed to fetch image: {e}"}), 500

@app.route("/api/audio-to-text", methods=["POST"])
def handle_audio_to_text():
    """语音转文字接口"""
    try:
        # 获取 Key (支持登录态或 Header)
        ms_key = get_api_key() # 验证 Token

        if 'file' not in request.files:
            return jsonify({"error": "No audio file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # 获取配置 (包含 API Key)
        # 注意：这里我们构造一个假的 config 请求体来复用 get_ai_config
        # 实际生产中可能需要从 User Setting 数据库读，但这里我们用前端传来的 params 或默认值
        # 为了简化，我们假设前端设置已保存或使用默认
        # 这里稍微 Hack 一下，复用 get_ai_config 逻辑，但数据来源为空（使用默认值或环境变量）
        # 更好的方式是前端 FormData 传一个 JSON 字符串，但对于文件上传稍显麻烦
        # 我们暂时只依赖 get_api_key 校验权限，Key 本身在 services 里会尝试��取 bailian_api_key

        # 如果用户在前端设置了百炼 Key，我们需要前端把这个 Key 传过来，或者存储在 Token 里？
        # 目前 Token 里存的是 ModelScope Key。
        # 解决方案：简单起见，利用 get_ai_config 的默认行为（从 app.config 读取默认 Key）
        # 如果用户在前端配置了自定义 Key，需要前端在 Header 传递或 FormData 传递��
        # 这里为了保持一致性，我们尝试从请求的 form data 读取 'bailian_api_key'

        data = request.form.to_dict()
        config = get_ai_config(data)

        # 补充：如果 services.py 需要 Token 里的 key
        config['modelscope_key'] = ms_key

        text = transcribe_audio_dashscope(config, file)
        return jsonify({"text": text})
    except Exception as e:
        return handle_api_errors(e)

# --- 4. AI 功能路由 (最终版，调用管理器) ---

@app.route("/api/colorize-lineart", methods=["POST"])
def handle_colorize_lineart():
    """AI 智能上色"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        base64_image = data.get("base64_image")
        prompt = data.get("prompt")
        if not base64_image or not prompt:
            return jsonify({"error": "线稿图片和风格提示是必需的"}), 400

        image_url = generate_colorization(
            config=config, ms_key=ms_key, base64_image=base64_image, chinese_prompt=prompt
        )
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)

@app.route("/api/creative-workshop", methods=["POST"])
def handle_creative_workshop():
    """ 创意工坊 (非人像风格迁移)"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)

        base64_content_image = data.get("content_image") # 内容图 (必须)
        base64_style_image = data.get("style_image")     # 风格图 (模式二可选)
        chinese_prompt = data.get("prompt")              # 文本指令 (模式一可选)

        if not base64_content_image:
            return jsonify({"error": "内容图片是必需的"}), 400
        if not base64_style_image and not chinese_prompt:
             return jsonify({"error": "风格图片或文本指令至少需要一个"}), 400

        image_url = generate_creative_workshop(
            config=config,
            ms_key=ms_key,
            base64_content_image=base64_content_image,
            base64_style_image=base64_style_image,
            chinese_prompt=chinese_prompt
        )

        # 风格描述暂时移除，因为输入可能是图片
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/portrait-workshop", methods=["POST"])
def handle_portrait_workshop():
    """ 人像工坊"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        config["modelscope_key"] = ms_key

        base64_portrait_image = data.get("portrait_image")
        base64_style_image = data.get("style_image")
        preset_style_index = data.get("preset_style_index")

        if not base64_portrait_image:
            return jsonify({"error": "人像图片是必需的"}), 400
        if base64_style_image is None and preset_style_index is None:
             return jsonify({"error": "自定义风格图片或预设风格索引至少需要一个"}), 400

        image_url = generate_portrait_workshop(
            config=config,
            base64_portrait_image=base64_portrait_image,
            base64_style_image=base64_style_image,
            preset_style_index=preset_style_index
        )
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/ask-question", methods=["POST"])
def handle_ask_question():
    """艺术知识问答"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        messages = data.get("messages")
        if not messages:
            return jsonify({"error": "Messages are required"}), 400

        response_json = run_chat_completion(
            config=config, ms_key=ms_key, messages=messages
        )
        return jsonify(response_json)
    except Exception as e:
        return handle_api_errors(e)


@app.route("/api/generate-ideas", methods=["POST"])
def handle_generate_ideas():
    """创意灵感生成"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        theme = data.get("theme")
        if not theme:
            return jsonify({"error": "灵感主题是必需的"}), 400

        processed_ideas = generate_ideas(config=config, ms_key=ms_key, theme=theme)
        return jsonify(processed_ideas)
    except Exception as e:
        return handle_api_errors(e)

@app.route("/api/critique-homework", methods=["POST"])
def handle_critique_homework():
    """新功能：AI 老师点评作业"""
    try:
        # 复用现有的鉴权逻辑
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)

        config['modelscope_key'] = ms_key

        theme = data.get("theme", "自由创作")
        student_image = data.get("student_image") # Base64

        if not student_image:
            return jsonify({"error": "请上传作业图片"}), 400

        result = critique_student_work(config, ms_key, theme, student_image)
        return jsonify(result)
    except Exception as e:
        return handle_api_errors(e)

@app.route("/api/mood-painting", methods=["POST"])
def handle_mood_painting():
    """(新增) 心情画板"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)
        theme = data.get("theme")
        mood = data.get("mood")
        if not theme or not mood:
            return jsonify({"error": "心情和主题是必需的"}), 400

        processed_idea = generate_mood_painting(
            config=config, ms_key=ms_key, mood=mood, theme=theme
        )
        return jsonify(processed_idea)
    except Exception as e:
        return handle_api_errors(e)

# --- 5. 名画鉴赏室路由  ---

@app.route("/api/gallery/search", methods=["POST"])
def handle_gallery_search():
    try:
        data = request.json
        met_api_base = current_app.config["MET_API_BASE"]
        search_params = {
            "q": data.get("q", "*"), "hasImages": "true", "isPublicDomain": "true"
        }
        if data.get("departmentId"): search_params["departmentId"] = data.get("departmentId")
        if data.get("isHighlight"): search_params["isHighlight"] = data.get("isHighlight")
        if data.get("medium"): search_params["medium"] = data.get("medium")
        if data.get("geoLocation"): search_params["geoLocation"] = data.get("geoLocation")
        if data.get("dateBegin"): search_params["dateBegin"] = data.get("dateBegin")
        if data.get("dateEnd"): search_params["dateEnd"] = data.get("dateEnd")

        search_url = f"{met_api_base}/search"
        search_res = requests.get(search_url, params=search_params, timeout=10)
        search_res.raise_for_status()
        search_data = search_res.json()
        object_ids = search_data.get("objectIDs", [])
        if not object_ids:
            return jsonify({"artworks": [], "total": 0})

        artworks_raw = []
        for obj_id in object_ids[:20]: # 只获取前20个
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
                        "imageUrl": obj_data.get("primaryImageSmall"),
                        "metUrl": obj_data.get("objectURL", "#"),
                        "original_title": obj_data.get("title", "N/A"),
                        "original_artist": obj_data.get("artistDisplayName", "Unknown"),
                        "original_medium": obj_data.get("medium", "N/A"),
                    })
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch object {obj_id}: {e}")
                continue

        # 批量翻译 (平台无关)
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
    """名画鉴赏室 - AI 讲解"""
    try:
        ms_key = get_api_key()
        data = request.json
        config = get_ai_config(data)

        art_info_en = {
            "title": data.get("title", "N/A"),
            "artist": data.get("artist", "N/A"),
            "medium": data.get("medium", "N/A"),
            "date": data.get("date", "N/A"),
        }

        result_data = generate_artwork_explanation(
            config=config, ms_key=ms_key, art_info_en=art_info_en
        )
        return jsonify(result_data)
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