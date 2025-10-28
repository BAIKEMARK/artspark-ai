import os
import requests
import json
import boto3
import uuid
import base64
import time
from io import BytesIO
from PIL import Image
from flask import current_app
from prompt import PROMPTS
from utils import get_headers  # 导入 utils 中的 get_headers

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.tmt.v20180321 import tmt_client, models

# --- R2 S3 客户端配置 ---
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

# ---  腾讯云翻译配置 ---
TENCENT_SECRET_ID = os.getenv("Tencent_SecretId")
TENCENT_SECRET_KEY = os.getenv("Tencent_Secretkey")
TENCENT_REGION = "ap-guangzhou"

# --- 1. R2 S3 服务 ---


def upload_to_r2(base64_string):
    """
    将 base64 图像字符串上传到 R2 并返回公共 URL 和尺寸。
    """
    try:
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        image_bytes = BytesIO(data)

        # 从字节中读取图像尺寸
        with Image.open(image_bytes) as img:
            width, height = img.size

        image_bytes.seek(0)  # 重置指针
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


# --- 2. 腾讯云翻译服务 ---


def translate_text_tencent(text_list, target_lang="zh"):
    """使用腾讯云API批量翻译文本列表"""
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
            "Source": "auto",
            "Target": target_lang,
            "ProjectId": 0,
            "SourceTextList": text_list,
        }
        req.from_json_string(json.dumps(params))

        resp = client.TextTranslateBatch(req)
        translated_list = resp.TargetTextList

        if len(translated_list) != len(text_list):
            print(
                f"Warning: Tencent translation returned {len(translated_list)} results for {len(text_list)} inputs. Returning originals."
            )
            return text_list

        return translated_list

    except TencentCloudSDKException as err:
        print(f"Tencent Cloud Translation Error: {err}")
        # 出错时返回原始文本
        return text_list
    except Exception as e:
        print(f"An unexpected error occurred during translation: {e}")
        return text_list


# --- 3. ModelScope 服务 ---


def validate_modelscope_key(api_key):
    """尝试调用 ModelScope 以验证 API Key 的有效性"""
    try:
        headers = get_headers(api_key)
        base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
        model_id = current_app.config["QWEN_LLM_ID"]

        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 1,
        }
        response = requests.post(
            f"{base_url}v1/chat/completions", headers=headers, json=payload, timeout=10
        )

        if response.status_code == 401:
            return False
        if response.ok:
            return True
        return False

    except requests.exceptions.RequestException as e:
        print(f"Key validation request failed: {e}")
        return False


def generate_english_prompt(headers, config, chinese_prompt, context_description):
    """调用 Qwen 将中文提示词转为英文"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    full_user_prompt = PROMPTS["PROMPT_TRANSLATOR"].format(
        context=context_description, chinese_description=chinese_prompt
    )
    messages = [{"role": "user", "content": full_user_prompt}]
    payload = {
        "model": config["chat_model"],
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.5,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return content.replace('"', "").strip()


def get_style_prompt_from_image(headers, config, base64_image_url):
    """调用 Qwen-VL 识图以获取风格提示词"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    system_prompt = PROMPTS["STYLE_ANALYSIS_SYSTEM"]
    user_text = PROMPTS["STYLE_ANALYSIS_USER"]

    payload = {
        "model": config["vl_model"],
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
                        "image_url": {"url": base64_image_url},
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        "max_tokens": 1000,
        "temperature": 0.6,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("choices") and data["choices"][0].get("message"):
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Qwen-VL API Error: {data.get('message', 'Unknown error')}")


def submit_sync_generation(headers, body, base_url):
    """提交 ModelScope 同步图像生成"""
    response = requests.post(
        f"{base_url}v1/images/generations",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("images") and data["images"][0].get("url"):
        return data["images"][0]["url"]
    raise Exception(f"API Error (Sync): {data.get('message', 'Unknown error')}")


def submit_async_generation_task(headers, body):
    """提交 ModelScope 异步图像生成任务"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
    async_headers = {**headers, "X-ModelScope-Async-Mode": "true"}

    response = requests.post(
        f"{base_url}v1/images/generations", headers=async_headers, json=body
    )
    response.raise_for_status()
    return response.json()["task_id"]


def poll_generation_result(headers, task_id):
    """轮询 ModelScope 异步任务结果"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
    poll_headers = {**headers, "X-ModelScope-Task-Type": "image_generation"}

    while True:
        result = requests.get(f"{base_url}v1/tasks/{task_id}", headers=poll_headers)
        result.raise_for_status()
        data = result.json()
        if data["task_status"] == "SUCCEED":
            return data["output_images"][0]
        elif data["task_status"] == "FAILED":
            raise Exception(f"Task failed: {data.get('task_message', 'Unknown error')}")
        time.sleep(3)


def run_llm_chat(headers, config, messages, system_prompt):
    """运行 LLM 聊天"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    payload = {
        "model": config["chat_model"],
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 500,
        "temperature": 0.7,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()
    return response.json()


def run_llm_generation(headers, config, text_prompt, max_tokens=800, temp=0.8):
    """运行 LLM 生成（用于灵感生成器）"""
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    payload = {
        "model": config["chat_model"],
        "messages": [{"role": "user", "content": text_prompt}],
        "max_tokens": max_tokens,
        "temperature": temp,
    }

    text_response = requests.post(
        f"{base_url}v1/chat/completions",
        headers=headers,
        json=payload
    )
    text_response.raise_for_status()
    return text_response.json()