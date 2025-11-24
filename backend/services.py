import os
import json
import boto3
import uuid
import base64
from io import BytesIO

import requests
from PIL import Image
from flask import current_app

# [新增] 导入 pydub 和 DashScope ASR 相关库
from pydub import AudioSegment
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult

from prompt import PROMPTS
from utils import calculate_adaptive_size, ApiKeyMissingError
import api as executors

# 导入腾讯云 SDK (保持不变)
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models

# --- R2 S3 客户端配置 (保持不变) ---
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL_BASE = os.getenv("R2_PUBLIC_URL_BASE")

s3_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)

# ---  腾讯云翻译配置 (保持不变) ---
TENCENT_SECRET_ID = os.getenv("Tencent_SecretId")
TENCENT_SECRET_KEY = os.getenv("Tencent_Secretkey")
TENCENT_REGION = "ap-guangzhou"

# ==============================================================================
# === 0. 平台无关的辅助工具 (保持不变)
# ==============================================================================

def upload_to_r2(base64_string):
    """将 base64 图像字符串上传到 R2 并返回公共 URL 和尺寸。"""
    try:
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        image_bytes = BytesIO(data)
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
            ExtraArgs={"ContentType": mime_type, "ACL": "public-read"},
        )
        public_url = f"{R2_PUBLIC_URL_BASE}/{file_name}"
        return public_url, width, height
    except Exception as e:
        print(f"R2 Upload Error: {e}")
        raise Exception(f"Failed to upload image to R2 OSS: {e}")

def translate_text_tencent(text_list, target_lang="zh"):
    """使用腾讯云API批量翻译文本列表 (用于 MET 画廊)"""
    if not TENCENT_SECRET_ID or not TENCENT_SECRET_KEY:
        print("Warning: Tencent Cloud API keys not configured. Skipping translation.")
        return text_list
    try:
        cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, TENCENT_REGION, clientProfile)
        req = models.TextTranslateBatchRequest()
        params = {
            "Source": "auto", "Target": target_lang, "ProjectId": 0, "SourceTextList": text_list
        }
        req.from_json_string(json.dumps(params))
        resp = client.TextTranslateBatch(req)
        translated_list = resp.TargetTextList
        # 添加长度检查，如果翻译失败则返回原文
        if len(translated_list) == len(text_list):
            return translated_list
        else:
            print(f"Warning: Tencent translation returned {len(translated_list)} results for {len(text_list)} inputs. Returning originals.")
            return text_list
    except Exception as e:
        print(f"Tencent Cloud Translation Error: {e}")
        return text_list


def validate_modelscope_key(api_key):
    """尝试调用 ModelScope 以验证 API Key 的有效性"""
    # 这个函数需要直接调用 API，所以保留在这里
    try:
        from utils import _get_modelscope_headers # 导入内部函数
        headers = _get_modelscope_headers(api_key)
        base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
        model_id = current_app.config["MS_QWEN_LLM_ID"]
        payload = {
            "model": model_id, "messages": [{"role": "user", "content": "Test"}], "max_tokens": 1
        }
        response = requests.post(
            f"{base_url}v1/chat/completions", headers=headers, json=payload, timeout=10
        )
        return response.ok and response.status_code != 401
    except Exception as e:
        print(f"Key validation request failed: {e}")
        return False

def _parse_ideas_from_llm_json(content, is_list=False):
    """(保持不变) 辅助函数，从 LLM 的 (可能含 markdown) 响应中提取 JSON"""
    if is_list:
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        if json_start == -1 or json_end == 0:
            raise Exception("LLM did not return valid JSON list.")
        json_string = content[json_start : json_end]
        return json.loads(json_string)
    else:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            raise Exception("LLM did not return valid JSON object.")
        json_string = content[json_start : json_end]
        return json.loads(json_string).get("ideas", [])

def _parse_single_idea_from_llm_json(content):
    """(新增) 辅助函数，从 LLM 的 (可能含 markdown) 响应中提取单个 JSON 对象"""
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start == -1 or json_end == 0:
        raise Exception("LLM did not return valid JSON object.")
    json_string = content[json_start : json_end]
    return json.loads(json_string)

# ==============================================================================
# === [新增] 语音识别服务 (Paraformer Realtime v2)
# ==============================================================================

class ASRCallback(RecognitionCallback):
    """
    DashScope 语音识别回调类
    用于收集识别结果
    """
    def __init__(self):
        super().__init__()
        self.sentences = []
        self.error = None

    def on_open(self) -> None:
        print("ASR Connection open.")

    def on_close(self) -> None:
        print("ASR Connection close.")

    def on_event(self, result: RecognitionResult) -> None:
        # 当一句话结束时，收集结果
        if result.get_sentence().get('text') and result.is_sentence_end(result):
            text = result.get_sentence()['text']
            print(f"ASR Sentence: {text}")
            self.sentences.append(text)

    def on_error(self, result: RecognitionResult) -> None:
        self.error = result.get_sentence().get('text', 'Unknown Error')
        print(f"ASR Error: {self.error}")

def transcribe_audio_dashscope(config, audio_file_obj):
    """
    使用 paraformer-realtime-v2 模型将音频文件转为文字。

    Args:
        config (dict): 包含 api_key 的配置字典
        audio_file_obj (FileStorage): Flask 上传的文件对象
    """
    api_key = config.get("bailian_api_key")
    if not api_key:
        # 如果没配置百炼 Key，尝试使用 ModelScope Key (虽然通常这是两个体系，但为了兼容)
        api_key = config.get("modelscope_key")

    if not api_key:
        raise ApiKeyMissingError("未找到有效的 API Key (需配置阿里云百炼 API Key)")

    try:
        # 1. 格式转换: WebM/WAV -> 16000Hz, Mono, 16-bit PCM
        # 使用 pydub 读取上传的文件
        print("ASR: Converting audio format...")
        audio = AudioSegment.from_file(audio_file_obj)
        # 强制转换为 16k 采样率, 单声道, 16bit
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # 导出为 raw pcm 数据
        pcm_data = audio.raw_data

        # 2. 准备识别
        callback = ASRCallback()
        recognition = Recognition(
            model='paraformer-realtime-v2',
            format='pcm',
            sample_rate=16000,
            callback=callback,
            # [优化] 开启语气词过滤
            disfluency_removal_enabled=True,
            # [优化] 语言提示 (中英混合)
            language_hints=['zh', 'en']
        )

        # 3. 模拟实时流发送
        print("ASR: Starting recognition...")
        recognition.start(api_key=api_key)

        # 分块发送数据 (模拟 stream.read)
        chunk_size = 3200 # 3200 bytes 约等于 100ms 音频
        offset = 0
        total_len = len(pcm_data)

        while offset < total_len:
            end = min(offset + chunk_size, total_len)
            chunk = pcm_data[offset:end]
            recognition.send_audio_frame(chunk)
            offset = end

        # 发送完毕，停止
        recognition.stop()

        if callback.error:
            raise Exception(f"DashScope ASR Error: {callback.error}")

        # 拼接所有句子
        full_text = "".join(callback.sentences)
        print(f"ASR Result: {full_text}")

        if not full_text:
             # 如果没有识别出句子（可能时间太短），尝试获取流中的最后内容
             # (注：Paraformer v2 通常在 stop 后会触发最后的 on_event)
             return ""

        return full_text
    except Exception as e:
        print(f"Audio Transcription Failed: {e}")
        # 简单的错误透传
        raise Exception(f"语音识别失败: {str(e)}")


# ==============================================================================
# === DashScope 图像尺寸调整辅助函数
# ==============================================================================
def _resize_image_for_dashscope(base64_string, min_dim=512, max_dim=4096):
    """
    辅助函数：解码Base64图像，检查宽高。
    如有必要则调整，确保图像的 *两个维度* 都在 [min_dim, max_dim] 范围内，并保持宽高比。
    """
    try:
        header, encoded = base64_string.split(",", 1)
        mime_type = header.split(";")[0].split(":")[-1]

        data = base64.b64decode(encoded)
        image_bytes = BytesIO(data)

        with Image.open(image_bytes) as img:
            width, height = img.size

            new_width = width
            new_height = height

            needs_resize = False

            # 1. 检查是否过大 (Oversized)
            if new_width > max_dim or new_height > max_dim:
                needs_resize = True
                # 计算缩小比例，确保两个边都小于 max_dim
                ratio_w = max_dim / new_width
                ratio_h = max_dim / new_height
                scale = min(ratio_w, ratio_h) # 取较小的比例，确保都装得下
                new_width = int(new_width * scale)
                new_height = int(new_height * scale)

            # 2. 检查是否过小 (Undersized)
            if new_width < min_dim or new_height < min_dim:
                needs_resize = True
                # 计算放大比例，确保两个边都大于 min_dim
                ratio_w = min_dim / new_width
                ratio_h = min_dim / new_height
                scale = max(ratio_w, ratio_h) # 取较大的比例，确保都达标
                new_width = int(new_width * scale)
                new_height = int(new_height * scale)

            # 如果不需要调整尺寸
            if not needs_resize:
                return base64_string # 尺寸合适，返回原图

            print(f"DashScope Resizer: Original size {width}x{height}. Final size {new_width}x{new_height}.")

            # 使用 LANCZOS 进行高质量缩放
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            output_bytes = BytesIO()
            # 尝试保留原始格式
            pil_format = img.format if img.format else "PNG"

            if pil_format == "JPEG":
                if img_resized.mode != "RGB":
                    img_resized = img_resized.convert("RGB")

            img_resized.save(output_bytes, format=pil_format, quality=95)
            encoded_resized = base64.b64encode(output_bytes.getvalue()).decode('utf-8')
            return f"{header},{encoded_resized}"

    except Exception as e:
        print(f"Error during image resize for DashScope: {e}")
        raise Exception(f"图像调整失败: {e}")

# ==============================================================================
# === 3. 功能“管理器” (Public) - 由 app.py 调用 (已适配新的执行器)
# ==============================================================================

def generate_colorization(config, ms_key, base64_image, chinese_prompt):
    """AI 智能上色“管理器”"""
    platform = config.get("api_platform", "modelscope")

    doodle_prompt = f"{chinese_prompt}风格。"
    if config["age_range"] in ["6-8岁", "9-10岁"]:
        doodle_prompt += " 色彩明亮, 卡通风格。"
    elif config["age_range"] in ["13-15岁", "16-18岁"]:
         doodle_prompt += " 细节丰富, 写实光影。"

    if platform == "bailian":
        print("DashScope Manager: Calling wanx2.1-imageedit (doodle) for colorization.")

        resized_base64_image = _resize_image_for_dashscope(base64_image)

        return executors.run_image_edit_wanx21_dashscope(
            config=config,
            function="doodle",
            base_image_b64=resized_base64_image,
            prompt=doodle_prompt,
            is_sketch='false'
        )

    else:
        print("ModelScope Manager: Uploading to R2 and calling LLM/ImageGen for colorization.")
        public_url, w, h = upload_to_r2(base64_image)
        adaptive_size = calculate_adaptive_size(w, h)
        full_chinese_prompt_for_translator = PROMPTS["COLORIZE_PROMPT_CN"].format(
            prompt=chinese_prompt, age_range=config["age_range"]
        )
        translator_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
            context="Coloring a lineart image.",
            chinese_description=full_chinese_prompt_for_translator
        )
        english_prompt = executors.run_llm_generation_modelscope(
            config, ms_key, translator_prompt
        )

        ms_negative_prompt = "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, grayscale, monochrome, sketch, unfinished, lineart"
        body = {
            "model": config["ms_image_model"],
            "prompt": english_prompt,
            "negative_prompt": ms_negative_prompt,
            "image_url": public_url,
            "size": adaptive_size,
        }
        return executors.run_image_gen_modelscope(config, ms_key, body)


def generate_creative_workshop(config, ms_key, base64_content_image=None, base64_style_image=None, chinese_prompt=None):
    """创意工坊“管理器” - 处理非人像的风格迁移"""
    platform = config.get("api_platform", "modelscope")

    if platform == "bailian":

        resized_content_image = _resize_image_for_dashscope(base64_content_image)

        if base64_style_image:
            # --- 模式二: 图像风格 ---
            print("DashScope Manager: Simulating style transfer using VL and wanx2.1-imageedit (stylization_all).")

            resized_style_image = _resize_image_for_dashscope(base64_style_image)

            # 1. 调用 VL 分析风格图 (获取文本描述)
            style_analysis_content = [
                {"image": resized_style_image},
                {"text": PROMPTS["STYLE_ANALYSIS_USER"] + " 请用中文描述风格。"}
            ]
            style_description_cn = executors.run_vl_chat_dashscope(config, style_analysis_content)
            # 2. 构造 stylization_all 的 prompt
            stylization_prompt = f"转换成 [{style_description_cn}] 风格"
            # 3. 调用 stylization_all
            return executors.run_image_edit_wanx21_dashscope(
                config=config,
                function="stylization_all",
                base_image_b64=resized_content_image, # 使用调整后的内容图
                prompt=stylization_prompt,
                strength=0.6
            )
        elif chinese_prompt:
             # --- 模式一: 文本指令 ---
             return executors.run_image_edit_wanx21_dashscope(
                 config=config,
                 function="stylization_all",
                 base_image_b64=resized_content_image, # 使用调整后的内容图
                 prompt=chinese_prompt
             )
        else:
             raise ValueError("Creative workshop requires either a style image or a text prompt.")

    else:
        print("ModelScope Manager: Calling LLM/VL/ImageGen for creative workshop.")

        public_content_url = None
        w, h = 0, 0

        if base64_content_image:
            public_content_url, w, h = upload_to_r2(base64_content_image)

        if base64_style_image:
            # --- 模式二: 图像风格  ---
            print("ModelScope Creative Workshop: Image Style Mode")
            public_style_url, _, _ = upload_to_r2(base64_style_image)
            style_analysis_content = [
                {"type": "image_url", "image_url": {"url": public_style_url}},
                {"type": "text", "text": PROMPTS["STYLE_ANALYSIS_USER"]}
            ]
            style_description_en = executors.run_vl_chat_modelscope(
                config, ms_key, PROMPTS["STYLE_ANALYSIS_SYSTEM"], style_analysis_content
            )
            final_english_prompt = PROMPTS["ART_FUSION_PROMPT_EN"].format(style_description=style_description_en)

        elif chinese_prompt:
            # --- 模式一: 文本指令 ---
            print("ModelScope Creative Workshop: Text Instruction Mode")
            translator_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
                context=f"Applying creative style based on user instruction.",
                chinese_description=chinese_prompt
            )
            final_english_prompt = executors.run_llm_generation_modelscope(
                 config, ms_key, translator_prompt
            )
        else:
             raise ValueError("Creative workshop requires either a style image or a text prompt.")

        ms_negative_prompt = "text, watermark, signature, blurry, low quality, worst quality, deformed, ugly, bad anatomy"
        body = {
            "model": config["ms_image_model"],
            "prompt": final_english_prompt,
            "negative_prompt": ms_negative_prompt,
        }
        adaptive_size = calculate_adaptive_size(w, h) if w > 0 else "1024x1024"
        body["size"] = adaptive_size
        if public_content_url:
            body["image_url"] = public_content_url
            body["strength"] = 0.6

        return executors.run_image_gen_modelscope(config, ms_key, body)


def generate_portrait_workshop(config, base64_portrait_image, base64_style_image=None, preset_style_index=None):
    """人像工坊“管理器”"""
    platform = config.get("api_platform", "modelscope")
    ms_key = config.get("modelscope_key")

    if platform == "bailian":
        print("DashScope Manager: Calling wanx-style-cosplay for portrait workshop.")

        resized_portrait_image = _resize_image_for_dashscope(base64_portrait_image)

        if base64_style_image is not None:
            # --- 自定义风格模式 ---
            print("DashScope Manager: Custom style mode selected.")

            resized_style_image = _resize_image_for_dashscope(base64_style_image)

            return executors.run_portrait_stylization_dashscope(
                config=config,
                base_image_b64=resized_portrait_image,
                style_image_b64=resized_style_image,
                style_index=-1
            )
        elif preset_style_index is not None:
            # --- 预设风格模式 ---
            print(f"DashScope Manager: Preset style mode selected (Index: {preset_style_index}).")
            return executors.run_portrait_stylization_dashscope(
                config=config,
                base_image_b64=resized_portrait_image,
                style_image_b64=None,
                style_index=preset_style_index
            )
        else:
             # 此情况理论上已被 app.py 捕获，但作为防御添加
             raise ValueError("Portrait workshop requires either a style image or a preset style index.")

    else: # ModelScope 平台逻辑 (保持不变)
        # ... (省略 ModelScope 的模拟逻辑) ...
        print("ModelScope Manager: Simulating portrait workshop using LLM/ImageGen.")
        if not ms_key: raise ApiKeyMissingError("ModelScope Key not found in config for portrait workshop.")

        if preset_style_index is not None:
             style_map = {
                0: "复古漫画", 1: "3D童话", 2: "二次元", 3: "小清新", 4: "未来科技",
                5: "国画古风", 6: "将军百战", 7: "炫彩卡通", 8: "清雅国风",
                9: "喜迎新年", 14: "国风工笔", 15: "恭贺新禧", 30: "童话世界",
                31: "黏土世界", 32: "像素世界", 33: "冒险世界", 34: "日漫世界",
                35: "3D世界", 36: "二次元世界", 37: "手绘世界", 38: "蜡笔世界",
                39: "冰箱贴世界", 40: "吧唧世界"
             }
             style_name = style_map.get(preset_style_index, f"预设风格{preset_style_index}")
             chinese_prompt = PROMPTS["SELF_PORTRAIT_PROMPT_CN"].format(style_prompt=style_name)
             context_desc = f"Stylizing a portrait into preset style {style_name}."

             translator_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
                 context=context_desc, chinese_description=chinese_prompt
             )
             final_english_prompt = executors.run_llm_generation_modelscope(
                 config, ms_key, translator_prompt
             )

        elif base64_style_image:
             public_style_url, _, _ = upload_to_r2(base64_style_image)
             style_analysis_content = [
                 {"type": "image_url", "image_url": {"url": public_style_url}},
                 {"type": "text", "text": PROMPTS["STYLE_ANALYSIS_USER"]}
             ]
             style_description_en = executors.run_vl_chat_modelscope(
                 config, ms_key, PROMPTS["STYLE_ANALYSIS_SYSTEM"], style_analysis_content
             )
             final_english_prompt = f"A portrait in the style of [{style_description_en}], masterpiece, best quality. Must preserve face features."
        else:
            raise ValueError("Portrait workshop requires either a style image or a preset style index.")

        return _execute_modelscope_portrait_simulation(
            config,
            base64_portrait_image,
            final_english_prompt
        )

def _execute_modelscope_portrait_simulation(config, base64_portrait_image, english_prompt):
    """
     辅助函数，执行 ModelScope 的人像风格化模拟。
    从 config 获取 ms_key。
    """
    ms_key = config.get("modelscope_key")
    if not ms_key:
        raise ApiKeyMissingError("Internal Error: ModelScope Key not found in config for simulation.")

    public_portrait_url, w, h = upload_to_r2(base64_portrait_image)
    adaptive_size = calculate_adaptive_size(w, h)
    ms_negative_prompt = "text, watermark, signature, blurry, ugly, deformed, disfigured, worst quality, low quality, multiple heads, bad anatomy, extra limbs, mutation, gender swap"

    body = {
        "model": config["ms_image_model"],
        "prompt": english_prompt,
        "negative_prompt": ms_negative_prompt,
        "image_url": public_portrait_url,
        "size": adaptive_size,
        "strength": 0.65
    }
    return executors.run_image_gen_modelscope(config, ms_key, body)

def run_chat_completion(config, ms_key, messages):
    """艺术知识问答“管理器” (多轮对话)"""
    platform = config.get("api_platform", "modelscope")
    system_prompt = PROMPTS["ART_QA_USER"].format(age_range=config["age_range"])

    if platform == "bailian":
        print("DashScope Manager: Running LLM Chat.")
        message_obj = executors.run_llm_chat_dashscope(config, messages, system_prompt)
        return { "choices": [{"message": {"role": message_obj.role, "content": message_obj.content}}] }
    else:
        print("ModelScope Manager: Running LLM Chat.")
        return executors.run_llm_chat_modelscope(config, ms_key, messages, system_prompt)


def generate_ideas(config, ms_key, theme):
    """创意灵感生成器“管理器”"""
    platform = config.get("api_platform", "modelscope")

    # 1. 生成创意文本
    text_prompt = PROMPTS["IDEA_GENERATOR_USER"].format(
        theme=theme,
        age_range=config["age_range"]
    )
    ideas = []
    if platform == "bailian":
        print("DashScope Manager: Generating idea text...")
        content = executors.run_llm_generation_dashscope(config, text_prompt)
        ideas = _parse_ideas_from_llm_json(content)
    else:
        print("ModelScope Manager: Generating idea text...")
        content = executors.run_llm_generation_modelscope(config, ms_key, text_prompt)
        ideas = _parse_ideas_from_llm_json(content)

    # 2. 并发生成图像
    processed_ideas = []
    # TODO: 并发处理
    for idea in ideas:
        try:
            img_prompt_cn = PROMPTS["IDEA_IMAGE_PROMPT_CN"].format(
                name=idea['name'],
                description=idea['description'],
                elements=idea['elements'],
                age_range=config["age_range"]
            )
            ms_negative_prompt = "text, watermark, signature, blurry, low quality, ugly, deformed"

            if platform == "bailian":
                 print(f"DashScope Manager: Generating image for idea '{idea['name']}'...")
                 idea["exampleImage"] = executors.run_text_to_image_dashscope(
                     config,
                     prompt=img_prompt_cn,
                 )
            else:
                print(
                    f"ModelScope Manager: Generating image for idea '{idea['name']}'..."
                )
                translator_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
                    context=f"Generating an image for creative idea: {idea['name']}",
                    chinese_description=img_prompt_cn,
                )
                english_prompt = executors.run_llm_generation_modelscope(
                    config, ms_key, translator_prompt
                )
                img_body = {
                    "model": config["ms_image_model"],
                    "prompt": english_prompt,
                    "negative_prompt": ms_negative_prompt,
                    "size": "1024x1024",
                }
                idea["exampleImage"] = executors.run_image_gen_modelscope(
                    config, ms_key, img_body, sync=True
                )

        except Exception as img_err:
            print(
                f"{platform.capitalize()} Manager: Failed to generate image for idea '{idea['name']}': {img_err}"
            )
            idea["exampleImage"] = None
        processed_ideas.append(idea)

    return processed_ideas


def generate_mood_painting(config, ms_key, mood, theme):
    """心情画板“管理器”"""
    platform = config.get("api_platform", "modelscope")
    age_range = config["age_range"]

    # 1. 生成创意文本
    text_prompt = PROMPTS["PSYCH_ART_PROMPT"].format(
        mood=mood, theme=theme, age_range=age_range
    )

    idea = {}
    if platform == "bailian":
        print("DashScope Manager: Generating mood painting text...")
        content = executors.run_llm_generation_dashscope(config, text_prompt)
        idea = _parse_single_idea_from_llm_json(content)
    else:
        print("ModelScope Manager: Generating mood painting text...")
        content = executors.run_llm_generation_modelscope(config, ms_key, text_prompt)
        idea = _parse_single_idea_from_llm_json(content)

    # 2. 生成图像
    try:
        img_prompt_cn = PROMPTS["IDEA_IMAGE_PROMPT_CN"].format(
            name=idea["name"],
            description=idea["description"],
            elements=idea["elements"],
            age_range=age_range,
        )
        ms_negative_prompt = "text, watermark, signature, blurry, low quality, ugly, deformed, bad anatomy"

        if platform == "bailian":
             print(f"DashScope Manager: Generating image for mood idea '{idea['name']}'...")
             idea["exampleImage"] = executors.run_text_to_image_dashscope(
                 config,
                 prompt=img_prompt_cn,
             )
        else:
             print(f"ModelScope Manager: Generating image for mood idea '{idea['name']}'...")
             translator_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
                 context=f"Generating an image for creative idea: {idea['name']}",
                 chinese_description=img_prompt_cn
             )
             english_prompt = executors.run_llm_generation_modelscope(config, ms_key, translator_prompt)
             img_body = {
                 "model": config["ms_image_model"],
                 "prompt": english_prompt,
                 "negative_prompt": ms_negative_prompt,
                 "size": "1024x1024",
             }
             idea["exampleImage"] = executors.run_image_gen_modelscope(config, ms_key, img_body, sync=True)

    except Exception as img_err:
        print(f"{platform.capitalize()} Manager: Failed to generate image for mood idea '{idea['name']}': {img_err}")
        idea["exampleImage"] = None

    return idea

def generate_artwork_explanation(config, ms_key, art_info_en):
    """名画鉴赏室“管理器” (AI 讲解)"""
    platform = config.get("api_platform", "modelscope")

    # 1. 获取 AI 讲解 (使用对应平台 LLM)
    ai_user_prompt = PROMPTS["ARTWORK_EXPLAINER"].format(
        age_range=config["age_range"],
        **art_info_en
    )
    ai_explanation = {}
    if platform == "bailian":
        print("DashScope Manager: Generating artwork explanation...")
        content = executors.run_llm_generation_dashscope(config, ai_user_prompt)
        ai_explanation = {"role": "assistant", "content": content}
    else:
        print("ModelScope Manager: Generating artwork explanation...")
        response_json = executors.run_llm_chat_modelscope(config, ms_key, [], ai_user_prompt)
        ai_explanation = response_json["choices"][0]["message"]

    # 2. 翻译原文信息 (平台无关, 使用腾讯云)
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
            raise Exception("Translation list length mismatch")
    except Exception as e:
        print(f"Error translating original artwork info: {e}")
        original_description_zh = "\n".join([ # Fallback to English
            f"Title: {art_info_en['title']}", f"Artist: {art_info_en['artist']}",
            f"Medium: {art_info_en['medium']}", f"Date: {art_info_en['date']}"
        ])

    # 3. 返回结果
    return {
        "ai_explanation": ai_explanation,
        "original_description_zh": original_description_zh
    }