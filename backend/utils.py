from flask import request, jsonify, current_app
from itsdangerous import  SignatureExpired, BadTimeSignature
from requests.exceptions import HTTPError
from openai import OpenAI, AuthenticationError, RateLimitError, APIError


class ApiKeyMissingError(Exception):
    """当 token 验证失败或丢失时引发"""

    pass


def get_serializer():
    """获取 Flask app 上下文中的 ts 序列化器"""
    try:
        return current_app.config["ts"]
    except RuntimeError:
        raise Exception("Must be run within a Flask application context")


def _get_modelscope_headers(modelscope_key):
    """
    (重构) 内部辅助函数，仅用于创建 ModelScope 的 headers。
    """
    if not modelscope_key:
        raise ApiKeyMissingError("ModelScope API Key is missing.")
    return {
        "Authorization": f"Bearer {modelscope_key}",
        "Content-Type": "application/json",
    }


def _get_dashscope_openai_client(config):
    """
    (新增) 内部辅助函数，用于创建 DashScope (OpenAI 兼容) 的 LLM 客户端。
    """
    api_key = config.get("bailian_api_key")
    if not api_key:
        raise ApiKeyMissingError("未在设置中配置阿里云百炼 API Key (Bailian API Key)")

    base_url = current_app.config["DASHSCOPE_OPENAI_BASE_URL"]

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def get_api_key():
    """
    从请求中解密 token 并返回原始 ModelScope API Key。
    此函数仅用于验证用户 *登录状态* (基于 ModelScope Key)。
    """
    token = request.args.get("token")
    if not token:
        raise ApiKeyMissingError("Token is missing from query parameters. (token=...).")

    try:
        ts = get_serializer()
        salt = current_app.config["API_KEY_SALT"]
        api_key = ts.loads(token, salt=salt, max_age=2592000)
        return api_key
    except SignatureExpired:
        raise ApiKeyMissingError("Token has expired. Please re-enter API Key.")
    except BadTimeSignature:
        raise ApiKeyMissingError("Invalid token. Please re-enter API Key.")
    except Exception as e:
        print(f"Token decryption error: {e}")
        raise ApiKeyMissingError("Invalid token.")


def handle_api_errors(e):
    """
    (重构) 通用的 API 错误处理器，现在支持 DashScope 和 OpenAI SDK 异常。
    """

    # 捕获 DashScope 图像 SDK 异常
    try:
        from dashscope.api_entities.errors import (
            InvalidApiKey,
            InvalidParameter,
            RequestTimeOutError,
        )

        if isinstance(e, InvalidApiKey):
            print(f"DashScope Error: InvalidApiKey: {e}")
            return jsonify(
                {
                    "error": f"DashScope API 错误: (InvalidApiKey) API Key 无效。请检查'设置'。"
                }
            ), 401
        if isinstance(e, InvalidParameter):
            print(f"DashScope Error: InvalidParameter: {e}")
            return jsonify(
                {"error": f"DashScope API 错误: (InvalidParameter) 参数无效。 {e}"}
            ), 400
        if isinstance(e, RequestTimeOutError):
            print(f"DashScope Error: RequestTimeOutError: {e}")
            return jsonify(
                {"error": f"DashScope API 错误: (RequestTimeOutError) 请求超时。"}
            ), 504
    except ImportError:
        pass  # dashscope 未安装

    # 捕获 DashScope (OpenAI 兼容) LLM SDK 异常
    if isinstance(e, AuthenticationError):
        print(f"OpenAI/DashScope Error: AuthenticationError: {e}")
        return jsonify(
            {
                "error": f"DashScope LLM API 错误: (AuthenticationError) API Key 无效。请检查'设置'。"
            }
        ), 401
    if isinstance(e, RateLimitError):
        print(f"OpenAI/DashScope Error: RateLimitError: {e}")
        return jsonify(
            {"error": f"DashScope LLM API 错误: (RateLimitError) 达到速率限制。"}
        ), 429
    if isinstance(e, APIError):
        print(f"OpenAI/DashScope Error: APIError: {e}")
        return jsonify(
            {"error": f"DashScope LLM API 错误: (APIError) {e.message}"}
        ), 502

    # 捕获 ModelScope 登录 Token 异常
    if isinstance(e, ApiKeyMissingError):
        return jsonify({"error": str(e)}), 401

    # 捕获 ModelScope (requests) HTTP 异常
    if isinstance(e, HTTPError):
        if e.response.status_code == 401 or e.response.status_code == 403:
            try:
                err_json = e.response.json()
                msg = err_json.get("message", str(e))
                if "code" in err_json:
                    msg = f"{err_json.get('code')}: {msg}"
            except Exception:
                msg = str(e)
            return jsonify({"error": f"ModelScope API Key 无效或无权限: {msg}"}), 401
        else:
            return jsonify(
                {"error": f"上游 API 错误 (HTTP {e.response.status_code}): {str(e)}"}
            ), 502

    # 捕获腾讯云 SDK 异常
    try:
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
            TencentCloudSDKException,
        )

        if isinstance(e, TencentCloudSDKException):
            return jsonify({"error": f"Tencent Cloud API 错误: {e.message}"}), 502
    except ImportError:
        pass

    # 通用回退
    err_str = str(e)
    if "DashScope API 错误" in err_str:
        return jsonify({"error": err_str}), 502

    print(f"An unexpected error occurred: {e}")
    return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


def get_ai_config(data):
    """(重构) 从请求数据中提取 AI 配置，并为两个平台提供默认值"""
    config = {
        # 教学配置
        "age_range": data.get("age_range", "6-8岁"),
        # 平台配置
        "api_platform": data.get("api_platform", "modelscope"),
        "bailian_api_key": data.get("bailian_api_key"),
        # ModelScope 模型 (保持原样)
        "ms_chat_model": data.get("chat_model", current_app.config["MS_QWEN_LLM_ID"]),
        "ms_vl_model": data.get("vl_model", current_app.config["MS_QWEN_VL_ID"]),
        "ms_image_model": data.get(
            "image_model", current_app.config["MS_FLUX_MODEL_ID"]
        ),
        # DashScope 模型
        "ds_llm_id": data.get("ds_llm_id", current_app.config["DS_LLM_ID"]),
        "ds_vl_id": data.get("ds_vl_id", current_app.config["DS_VL_ID"]),
        "ds_image_edit_id": data.get(
            "ds_image_edit_id", current_app.config["DS_WANX21_IMAGE_EDIT_ID"]
        ),
        "ds_text_to_image_id": data.get(
            "ds_text_to_image_id", current_app.config["DS_T2I_TURBO_ID"]
        ),
    }
    return config


# --- 图像尺寸辅助函数 ---


def round_to_64(x):
    return max(64, int(round(x / 64.0)) * 64)


def calculate_adaptive_size(width, height, target_dim=1024):
    if width == 0 or height == 0:
        return f"{target_dim}x{target_dim}"
    if width > height:
        aspect_ratio = height / width
        new_width = target_dim
        new_height = int(new_width * aspect_ratio)
    else:
        aspect_ratio = width / height
        new_height = target_dim
        new_width = int(new_height * aspect_ratio)
    final_width = round_to_64(new_width)
    final_height = round_to_64(new_height)
    if final_width == 0: final_width = 64
    if final_height == 0: final_height = 64
    return f"{final_width}x{final_height}"