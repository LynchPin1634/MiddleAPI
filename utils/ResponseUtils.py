#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : ResponseUtils.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/4/13 14:49

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)


from typing import Any, Optional, TypeVar, Callable
from aiohttp.web_fileresponse import FileResponse
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from functools import wraps
from pathlib import Path

import logging

T = TypeVar('T')

class ErrorTypes:
    CONFIG_WRITE_ERROR = "config_write_error"
    FILE_NOT_FOUND = "file_not_found"
    CONFIG_NOT_FOUND = "config_not_found"
    INVALID_API_KEY = "invalid_api_key"
    TTS_FAILED = "tts_error"
    AUDIO_NOT_FOUND = "audio_not_found"
    INTERNAL_ERROR = "server_error"
    VALIDATION_ERROR = "validation_error"

class ResponseHandler:
    """统一响应处理器"""

    @staticmethod
    def success(
            data: Any = None,
            message: str = "操作成功",
            code: int = 200,
            **extra: Any
    ) -> JSONResponse:
        """成功响应"""
        response_data = {
            "status": "success",
            "code": code,
            "message": message,
            "data": data
        }
        response_data.update(extra)
        return JSONResponse(content=response_data, status_code=code)

    @staticmethod
    def error(
            message: str = "操作失败",
            code: int = 500,
            error_type: Optional[str] = None,
            details: Optional[Any] = None,
            **extra: Any
    ) -> HTTPException:
        """错误响应"""
        error_data = {
            "status": "error",
            "code": code,
            "message": message,
            "type": error_type,
            "details": details
        }
        error_data.update(extra)
        return HTTPException(status_code=code, detail=error_data)

    @staticmethod
    def handle_file_response(file_path: Path):
        """统一文件响应处理"""
        if not file_path.exists():
            raise ResponseHandler.error(
                message="文件不存在",
                code=404,
                error_type=ErrorTypes.FILE_NOT_FOUND
            )
        return FileResponse(file_path)

    @staticmethod
    def validate_api_key(api_key: str):
        """API密钥验证"""
        if not api_key:
            raise ResponseHandler.error(
                message="无效的API密钥",
                code=401,
                error_type=ErrorTypes.INVALID_API_KEY
            )

    @staticmethod
    def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
        """统一错误处理装饰器"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as http_exc:
                raise http_exc
            except Exception as exc:
                logging.error(f"处理请求时出错: {str(exc)}", exc_info=True)
                raise ResponseHandler.error(
                    message="内部服务器错误",
                    code=500,
                    error_type=ErrorTypes.INTERNAL_ERROR,
                    details=str(exc)
                )

        return wrapper