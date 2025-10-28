import time
from http import HTTPStatus

import requests
from flask import current_app
import dashscope
from dashscope import MultiModalConversation, ImageSynthesis

from utils import (
    _get_modelscope_headers,
    _get_dashscope_openai_client,
    ApiKeyMissingError,
)

# ==============================================================================
# === 1. ModelScope 平台“执行器”
# ==============================================================================
def run_llm_chat_modelscope(config, ms_key, messages, system_prompt):
    """ModelScope LLM 聊天执行器"""
    headers = _get_modelscope_headers(ms_key)
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
    payload = {
        "model": config["ms_chat_model"],
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 500,
        "temperature": 0.7,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()
    return response.json()


def run_llm_generation_modelscope(config, ms_key, prompt, max_tokens=800, temp=0.5):
    """ModelScope LLM 单轮生成执行器 (用于翻译、创意生成等)"""
    headers = _get_modelscope_headers(ms_key)
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]
    payload = {
        "model": config["ms_chat_model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temp,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def run_vl_chat_modelscope(config, ms_key, system_prompt, messages_content):
    """ModelScope VL (识图) 执行器"""
    headers = _get_modelscope_headers(ms_key)
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    messages = []
    if system_prompt:
         messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    messages.append({"role": "user", "content": messages_content})

    payload = {
        "model": config["ms_vl_model"],
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.6,
    }
    response = requests.post(
        f"{base_url}v1/chat/completions", headers=headers, json=payload
    )
    response.raise_for_status()
    data = response.json()
    if data.get("choices") and data["choices"][0].get("message"):
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Qwen-VL API Error: {data.get('message', 'Unknown error')}")


def run_image_gen_modelscope(config, ms_key, body, sync=False):
    """ModelScope 图像生成 执行器"""
    headers = _get_modelscope_headers(ms_key)
    base_url = current_app.config["MODEL_SCOPE_BASE_URL"]

    if sync:
        response = requests.post(
            f"{base_url}v1/images/generations", headers=headers, json=body
        )
        response.raise_for_status()
        data = response.json()
        if data.get("images") and data["images"][0].get("url"):
            return data["images"][0]["url"]
        raise Exception(f"API Error (Sync): {data.get('message', 'Unknown error')}")
    else:
        async_headers = {**headers, "X-ModelScope-Async-Mode": "true"}
        response = requests.post(
            f"{base_url}v1/images/generations", headers=async_headers, json=body
        )
        response.raise_for_status()
        task_id = response.json()["task_id"]
        poll_headers = {**headers, "X-ModelScope-Task-Type": "image_generation"}
        start_time = time.time()
        timeout = 180
        while time.time() - start_time < timeout:
            result = requests.get(f"{base_url}v1/tasks/{task_id}", headers=poll_headers)
            result.raise_for_status()
            data = result.json()
            if data["task_status"] == "SUCCEED":
                return data["output_images"][0]
            elif data["task_status"] == "FAILED":
                raise Exception(f"ModelScope Task failed: {data.get('task_message', 'Unknown error')}")
            time.sleep(3)
        raise Exception(f"ModelScope Task polling timed out after {timeout} seconds.")

# ==============================================================================
# === 2. 阿里云 DashScope 平台“执行器” (保持最新)
# ==============================================================================

def run_llm_chat_dashscope(config, messages, system_prompt):
    """DashScope LLM 聊天执行器 (OpenAI 兼容)"""
    client = _get_dashscope_openai_client(config)
    all_messages = []
    if system_prompt:
        all_messages.append({"role": "system", "content": system_prompt})
    all_messages.extend(messages)
    completion = client.chat.completions.create(
        model=config["ds_llm_id"], messages=all_messages
    )
    return completion.choices[0].message


def run_llm_generation_dashscope(config, prompt, max_tokens=800, temp=0.5):
    """DashScope LLM 单轮生成执行器 (OpenAI 兼容)"""
    client = _get_dashscope_openai_client(config)
    completion = client.chat.completions.create(
        model=config["ds_llm_id"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temp,
    )
    return completion.choices[0].message.content


def run_vl_chat_dashscope(config, messages_content):
    """DashScope VL (识图) 执行器 (qwen-vl-plus)"""
    api_key = config.get("bailian_api_key")
    if not api_key:
        raise ApiKeyMissingError("未在设置中配置阿里云百炼 API Key (Bailian API Key)")
    dashscope.base_http_api_url = current_app.config["DASHSCOPE_API_BASE_URL"]
    response = MultiModalConversation.call(
        api_key=api_key,
        model=config["ds_vl_id"],
        messages=[{"role": "user", "content": messages_content}],
    )
    if response.status_code == 200:
        try:
            return response.output.choices[0].message.content[0]['text']
        except (IndexError, KeyError, TypeError):
            print(f"DashScope VL returned unexpected content format: {response.output.choices[0].message.content}")
            return response.output.choices[0].message.content
    else:
        raise Exception(f"DashScope VL API 错误 (HTTP {response.status_code}): {response.code} - {response.message}")


def run_image_edit_wanx21_dashscope(config, function, base_image_b64, prompt=None, is_sketch=None, strength=None, size="1024*1024"):
    """DashScope 通用图像编辑执行器 (wanx2.1-imageedit)。"""
    dashscope.base_http_api_url = current_app.config["DASHSCOPE_API_BASE_URL"]
    api_key = config.get("bailian_api_key")
    if not api_key:
        raise ApiKeyMissingError("未在设置中配置阿里云百炼 API Key (Bailian API Key)")

    model_id = current_app.config["DS_WANX21_IMAGE_EDIT_ID"]

    print(f"DashScope: Calling model {model_id} via ImageSynthesis with function '{function}'...")

    call_params = {
        "api_key": api_key,
        "model": model_id,
        "function": function,
        "base_image_url": base_image_b64,
        "n": 1,
        "size": size,
    }
    if function in ["description_edit", "colorization", "doodle", "remove_watermark", "stylization_all"]:
        if not prompt: raise ValueError(f"'prompt' is required for function '{function}'.")
        call_params["prompt"] = prompt

    if function == "doodle" and is_sketch is not None:
        call_params["is_sketch"] = is_sketch
        print(f"Parameter added for doodle: is_sketch={is_sketch}")
    if function == "stylization_all" and strength is not None:
         call_params["strength"] = strength
         print(f"Parameter added for stylization_all: strength={strength}")

    # 3. 调用 API (使用同步 call，传递 **kwargs)
    try:
        response = ImageSynthesis.call(**call_params)
    except Exception as e:
        print(f"DashScope SDK call failed for {model_id}/{function}: {e}")
        raise e

    # 4. 处理响应
    if response and response.status_code == 200:
        try:
            image_url = response.output.results[0].url
            print(f"DashScope {model_id}/{function} (SDK): Success, image URL: {image_url}")
            return image_url
        except (IndexError, KeyError, TypeError):
             print(response)
             raise Exception(f"DashScope {model_id}/{function} Error: Could not parse image URL from successful SDK response.")
    elif response:
        print(f"DashScope {model_id}/{function} Error: Code={response.code}, Message={response.message}")
        raise Exception(f"DashScope {model_id}/{function} API 错误 (HTTP {response.status_code}): {response.code} - {response.message}")
    else:
        raise Exception(f"DashScope {model_id}/{function}: Unknown error, SDK call returned None.")


def run_text_to_image_dashscope(config, prompt, size="1024*1024"):
    """
    DashScope 文生图执行器 (wanx2.1-t2i-turbo)。
    """
    api_key = config.get("bailian_api_key")
    if not api_key:
        raise ApiKeyMissingError("未在设置中配置阿里云百炼 API Key (Bailian API Key)")

    model_id = current_app.config["DS_T2I_TURBO_ID"]
    dashscope.base_http_api_url = current_app.config["DASHSCOPE_API_BASE_URL"]

    print(f"DashScope: Submitting async task for {model_id}...")

    # 1. 准备异步调用参数
    async_call_params = {
      "api_key": api_key,
      "model": model_id,
      "prompt": prompt,
      "n": 1,
      "size": size,
      'prompt_extend': True
    }

    # 2. 提交异步任务
    try:
        task = ImageSynthesis.async_call(**async_call_params)

        if task.status_code != HTTPStatus.OK:
            print(f"Failed to submit task. Response: {task}")
            raise Exception(f"DashScope 任务提交失败: {task.code} - {task.message}")

        print(f"Task submitted successfully, task_id: {task.output.task_id}")

    except Exception as e:
        print(f"DashScope SDK async_call failed for {model_id}: {e}")
        raise e

    try:
        dashscope.api_key = api_key
        response = ImageSynthesis.wait(task)

        if response.status_code == HTTPStatus.OK:
            for result in response.output.results:
                if result and hasattr(result, 'url') and result.url:
                    image_url = result.url
                    break # 只需要第一张图片
        if image_url:
            return image_url
    except Exception as e:
        print(f"DashScope SDK wait failed for {model_id}: {e}")
        raise e
    finally:
        dashscope.api_key = None

def run_portrait_stylization_dashscope(config, base_image_b64, style_image_b64=None, style_index=None):
    """
    (重写 v2 - 适配官方异步 REST API 示例)
    DashScope 人像风格化执行器 (wanx-style-repaint-v1)。
    使用 requests 提交异步任务并轮询结果。
    """
    api_key = config.get("bailian_api_key")
    if not api_key:
        raise ApiKeyMissingError("未在设置中配置阿里云百炼 API Key (Bailian API Key)")

    # 使用官方示例的 API 端点和模型 ID
    model_id = "wanx-style-repaint-v1"
    submit_url = f"{current_app.config['DASHSCOPE_API_BASE_URL']}/services/aigc/image-generation/generation"

    print(f"DashScope: Calling model {model_id} via REST API...")

    # 1. 准备 Headers (包含异步标志)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable" # 启用异步
    }

    # 2. 构建 input 对象
    input_data = {
        "image_url": base_image_b64,
        "style_index": style_index
    }

    if style_index == -1:
        input_data["style_ref_url"] = style_image_b64

    # 3. 构建请求体
    payload = {
        "model": model_id,
        "input": input_data
    }
    try:
        response = requests.post(submit_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        submit_data = response.json()
        task_id = submit_data.get('output', {}).get('task_id')
        if not task_id:
            raise Exception(f"Failed to submit task. Response: {submit_data}")
        print(f"Task submitted successfully, task_id: {task_id}")

    except requests.exceptions.RequestException as e:
        print(f"DashScope task submission failed: {e}")
        # 如果请求体有问题，API 可能直接返回 400 Bad Request
        if e.response is not None:
             print(f"Response status: {e.response.status_code}, Response body: {e.response.text}")
             raise Exception(f"DashScope task submission failed with status {e.response.status_code}: {e.response.text}")
        else:
             raise Exception(f"DashScope task submission failed: {e}")
    except Exception as e:
        # 捕获 JSON 解析等其他错误
         print(f"DashScope task submission processing failed: {e}")
         raise e


    # 5. 轮询任务结果
    query_url = f"{current_app.config['DASHSCOPE_API_BASE_URL']}/tasks/{task_id}"
    query_headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    timeout = 180
    print("Polling task status...")
    while time.time() - start_time < timeout:
        try:
            query_response = requests.get(query_url, headers=query_headers, timeout=10)
            query_response.raise_for_status()
            query_data = query_response.json()
            task_status = query_data.get('output', {}).get('task_status')
            if task_status == 'SUCCEEDED':
                print("Task SUCCEEDED!")
                results = query_data.get('output', {}).get('results', [])
                if results and results[0].get('url'):
                    image_url = results[0]['url']
                    print(f"DashScope {model_id}: Success, image URL: {image_url}")
                    return image_url
                else:
                    raise Exception(f"Task succeeded but no result URL found in response: {query_data}")
            elif task_status == 'FAILED':
                print(f"Task FAILED. Response: {query_data}")
                error_msg = query_data.get('output', {}).get('message', 'Unknown error')
                raise Exception(f"DashScope task {task_id} failed: {error_msg}")
            elif task_status in ['PENDING', 'RUNNING']:
                print(f"Task status: {task_status}, waiting...")
                time.sleep(5) # 等待 5 秒
            else:
                # 处理未知的状态
                print(f"Unknown task status: {task_status}. Response: {query_data}")
                raise Exception(f"DashScope task {task_id} returned unknown status: {task_status}")

        except requests.exceptions.RequestException as e:
            print(f"Polling failed: {e}")
            time.sleep(5)
        except Exception as e:
             print(f"Polling processing failed: {e}")
             raise e

    # 如果超时
    raise Exception(f"DashScope task {task_id} polling timed out after {timeout} seconds.")
