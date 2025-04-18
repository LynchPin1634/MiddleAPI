#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : PydanticUtils.py
# @IDE : PyCharm
# @Author : Ashley Lee (nekokecore@emtips.net)
# @Co-Author : DeckDes (deckdes@outlook.com)
# @Date : 2025/4/12 21:42

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)

from typing import Union, Optional, List, Dict
from pydantic import BaseModel
from fastapi import Query

class OpenWebUIObj(BaseModel):
    """
    TTS请求参数模型
    - 用于/audio/speech接口
    """
    input: str  # 文本
    voice: str  # 语音类型

class SetConfigObj(BaseModel):
    section: str  # 必填字段
    key: str      # 必填字段
    value: Union[str, int, float, bool, Dict, List, None]  # 扩展支持的类型

    # 添加配置示例
    class Config:
        json_schema_extra = {
            "example": {
                "section": "global",
                "key": "use_new_api",
                "value": True
            }
        }

class GetConfigObj(BaseModel):
    """
    配置获取参数模型
    - 用于/app/getconfig接口(同时支持GET和POST)
    - GET请求: /app/getconfig?section=global&key=use_new_api
    - POST请求: {"section": "global", "key": "use_new_api"}
    """
    section: str = Query(..., description="要查询的配置节名称", example="global")
    key: Optional[str] = Query(
        None,
        description="可选的具体配置键名",
        example="use_new_api"
    )

class ResetConfigObj(BaseModel):
    """
    配置重置确认模型
    - 用于/app/resetconfig接口
    """
    confirm: bool = Query(True, description="必须为true才会执行重置")

class AudioCleanupObj(BaseModel):
    """
    音频清理参数模型
    - 用于/audio/cleanup接口
    """
    keep_last: int = Query(
        5,
        description="要保留的最新文件数量",
        ge=0  # 值必须大于等于0
    )

# 注意：所有模型都自动支持FastAPI的请求验证和Swagger文档生成