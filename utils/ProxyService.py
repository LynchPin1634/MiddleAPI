#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : ProxyService.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/4/12 21:42

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)

from typing import Dict, Any, List, Optional
from utils.LogUtils import LogUtils
from pydantic import BaseModel

import aiohttp
import re

from utils.ResponseUtils import ResponseHandler, ErrorTypes

logger = LogUtils.get_logger("GradioUtils")

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None

class TTSRequest(BaseModel):
    input: str
    voice: str = "中文"

async def handle_proxy_request(
    request_data: ChatRequest,
    api_key: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    核心代理请求处理方法
    1. 清理请求数据
    2. 调用TTS服务
    3. 等待响应
    """
    try:
        data = _sanitize_request(request_data.dict(), config)
        logger.info(f"处理代理请求: model={data.get('model')}")

        api_url = config["API_URL"].rstrip('/') + '/chat/completions'

        async with aiohttp.ClientSession() as session:
            api_response = await session.post(
                api_url,  # 使用处理后的完整URL
                json=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=20
            )

            if api_response.status != 200:
                error_text = await api_response.text()
                logger.error(f"API错误: {api_response.status} - {error_text}")
                raise ResponseHandler.error(
                    message="AI服务不可用",
                    code=500,
                    error_type=ErrorTypes.INTERNAL_ERROR,
                    details=error_text
                )

            resp_data = await api_response.json()
            original_text = resp_data["choices"][0]["message"]["content"]
            cleaned_text = _clean_response_text(original_text)

            tts_timeout = _calculate_tts_timeout(cleaned_text, config)
            try:
                await _call_tts_service(
                    session=session,
                    text=cleaned_text,
                    timeout=tts_timeout
                )
            except Exception as tts_error:
                logger.warning(f"TTS服务调用失败: {str(tts_error)}")

            return resp_data

    except aiohttp.ClientError as e:
        logger.error(f"网络错误: {str(e)}")
        raise ResponseHandler.error(
            message="网络服务不可用",
            code=500,
            error_type=ErrorTypes.INTERNAL_ERROR,
            details=str(e)
        )

def _sanitize_request(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """清理请求数据"""
    if "messages" not in data:
        return data

    for msg in data["messages"]:
        if msg.get("role") == "system":
            msg["content"] = msg["content"][:config["MAX_SYSTEM_PROMPT_LENGTH"]]

    if config["CLEAN_HISTORY"]:
        data["messages"] = [
            msg for msg in data["messages"]
            if not (msg.get("role") == "assistant" and "disconnected" in msg.get("content", ""))
        ]

    data.pop("stop", None)
    return data

def _clean_response_text(text: str) -> str:
    """清理响应文本"""
    return re.sub(r'!\w+\([^)]*\)', '', text)

def _calculate_tts_timeout(text: str, config: Dict[str, Any]) -> int:
    """计算动态TTS超时时间"""
    char_count = len(text.strip())
    estimated_duration = char_count * config["SPEECH_RATE"]
    return min(
        max(config["MIN_TTS_TIMEOUT"], estimated_duration + 5),
        config["MAX_TTS_TIMEOUT"]
    )

async def _call_tts_service(
    session: aiohttp.ClientSession,
    text: str,
    timeout: int
):
    """调用TTS服务"""
    tts_response = await session.post(
        'http://localhost:8000/audio/speech',
        json={'input': text, 'voice': '中文'},
        timeout=timeout
    )
    if tts_response.status != 200:
        logger.warning(f"TTS服务警告: {await tts_response.text()}")