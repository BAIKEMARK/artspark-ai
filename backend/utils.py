import os
import requests
import json
from flask import request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from requests.exceptions import HTTPError


class ApiKeyMissingError(Exception):
    """当 token 验证失败或丢失时引发"""

    pass


def get_serializer():
    """获取 Flask app 上下文中的 ts 序列化器"""
    try:
        return current_app.config["ts"]
    except RuntimeError:
        # 确保在 app 上下文之外（例如，某些测试）时不会崩溃
        raise Exception("Must be run within a Flask application context")


def get_headers(token):
    """辅助函数，创建 API 调用的 headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_api_key():
    """
    从请求中解密 token 并返回原始 API Key。
    如果 token 无效或过期，则引发 ApiKeyMissingError。
    """
    token = request.args.get("token")
    if not token:
        raise ApiKeyMissingError("Token is missing from query parameters. (token=...).")

    try:
        ts = get_serializer()
        salt = current_app.config["API_KEY_SALT"]
        # 解密 Token，有效期 30 天 (2592000 秒)
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
    通用的 API 错误处理器，返回 JSON 响应。
    """
    if isinstance(e, ApiKeyMissingError):
        # Token 解密失败或过期
        return jsonify({"error": str(e)}), 401
    if isinstance(e, HTTPError):
        # ModelScope 返回了 4xx 或 5xx 错误
        if e.response.status_code == 401:
            # 将 ModelScope 的 401 错误传递给前端
            return jsonify({"error": "API Key 无效或已过期 (来自 ModelScope)"}), 401
        else:
            # ModelScope 的其他错误 (如 500, 400)
            return jsonify(
                {
                    "error": f"ModelScope API 错误 (HTTP {e.response.status_code}): {str(e)}"
                }
            ), 502

    # 检查是否是腾讯云 SDK 异常
    try:
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
            TencentCloudSDKException,
        )

        if isinstance(e, TencentCloudSDKException):
            return jsonify({"error": f"Tencent Cloud API 错误: {e.message}"}), 502
    except ImportError:
        pass  # 如果没导入 SDK，则忽略

    print(f"An unexpected error occurred: {e}")
    return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


def get_ai_config(data):
    """从请求数据中提取 AI 配置，并提供默认值"""
    config = {
        "chat_model": data.get("chat_model", current_app.config["QWEN_LLM_ID"]),
        "vl_model": data.get("vl_model", current_app.config["QWEN_VL_ID"]),
        "image_model": data.get("image_model", current_app.config["FLUX_MODEL_ID"]),
        "age_range": data.get("age_range", "6-8岁"),
    }
    return config


# --- 图像尺寸辅助函数 ---


def round_to_64(x):
    """将尺寸调整为 64 的最接近倍数，最小为 64"""
    return max(64, int(round(x / 64.0)) * 64)


def calculate_adaptive_size(width, height, target_dim=1024):
    """根据原始宽高比计算新的尺寸，使最长边为 target_dim，并圆整到 64"""
    if width == 0 or height == 0:
        return f"{target_dim}x{target_dim}"  # 备用

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