#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : MiddleAPI.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/4/12 21:42

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)

from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from collections import OrderedDict
from typing import List, Union
from collections import deque
from pathlib import Path

import logging
import aiohttp
import hashlib
import shutil
import os

from starlette.staticfiles import StaticFiles

from utils.ProxyService import handle_proxy_request, ChatRequest  # 导入ProxyService
from utils.GradioUtils import GradioClient
from utils.PydanticUtils import OpenWebUIObj, SetConfigObj, GetConfigObj, ResetConfigObj
from utils.ConfigUtils import ConfigTools
from utils.ResponseUtils import ResponseHandler, ErrorTypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('middleapi.log')
    ]
)
logger = logging.getLogger("MiddleAPI")

AUDIO_STORAGE = Path("../config/middlemod/tts_audio_storage")
AUDIO_STORAGE.mkdir(exist_ok=True, parents=True)
RECENT_FILES = deque(maxlen=5)

PROXY_CONFIG = {
    "API_URL": "https://api.302ai.cn/v1/chat/completions",
    "MAX_SYSTEM_PROMPT_LENGTH": 50000,
    "CLEAN_HISTORY": True,
    "MIN_TTS_TIMEOUT": 25,
    "MAX_TTS_TIMEOUT": 60,
    "SPEECH_RATE": 0.3
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("启动MiddleAPI服务...")
    global client
    client = aiohttp.ClientSession()

    cleanup_old_files(keep_last=0)

    yield

    if client is not None:
        await client.close()
        logger.info("ClientSession已关闭")

app = FastAPI(
    lifespan=lifespan,
    title="MiddleAPI",
    description="主API服务，包含路由注册和核心功能",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.mount("/files", StaticFiles(directory="www/files"), name="files")

def generate_audio_hash(text: str, voice: str) -> str:
    """生成唯一哈希值"""
    return hashlib.md5(f"{text}_{voice}".encode('utf-8')).hexdigest()


def cleanup_old_files(keep_last: int = 5):
    """清理历史音频"""
    try:
        files = sorted(AUDIO_STORAGE.glob("*.wav"), key=os.path.getmtime)
        for old_file in files[:-keep_last] if keep_last > 0 else files:
            old_file.unlink(missing_ok=True)
            logger.info(f"清理文件: {old_file.name}")
    except Exception as e:
        logger.error(f"清理失败: {str(e)}")

def make_http_error(status_code: int, detail: str, error_type: str = None):
    """除setting路由外的统一处理错误响应方法"""
    return ResponseHandler.error(
        message=detail,
        code=status_code,
        error_type=error_type
    )

# ========== 路由注册 ==========
@app.get("/", response_class=HTMLResponse)
@ResponseHandler.handle_errors
async def root(html="index.html"):
    """
    主页和网页注册
    1. 安全检查，防止目录遍历攻击
    2. 支持的页面列表
    3. 如果请求的页面不在支持列表中，返回首页
    """
    if not html.endswith('.html') or '/' in html or '\\' in html:
        html = "index.html"

    supported_pages = {"index.html", "settings.html", "audiolist.html", "cleanup.html","abyss.html","lynchpin.html"}
    html = html if html in supported_pages else "index.html"

    file_path = Path(f'www/{html}')
    if not file_path.exists():
        raise ResponseHandler.error(message="页面不存在", error_type=ErrorTypes.FILE_NOT_FOUND)


    return HTMLResponse(content=file_path.read_text(encoding="utf-8"), media_type="text/html")

# 注册ProxyService路由
@app.post("/v1/chat/completions")
@ResponseHandler.handle_errors
async def proxy_chat(request_data: ChatRequest):
        """代理方法"""
        cm = ConfigTools("config/config.yaml")
        config = cm.read_config()
        api_key = config.get("minecraft_api_key", {}).get("minecraft_api_key", "")

        ResponseHandler.validate_api_key(api_key)  # 统一验证

        result = await handle_proxy_request(
            request_data=request_data,
            api_key=api_key,
            config=PROXY_CONFIG
        )
        return ResponseHandler.success(data=result)


@app.post("/audio/speech")
@ResponseHandler.handle_errors
async def tts(openjson: OpenWebUIObj):
    """
    TTS音频生成接口
    1. 生成音频哈希值
    2. 如果已存在则直接返回
    3. 调用Gradio生成音频
    4. 移动文件到存储目录
    5. 自动清理旧文件
    """

    audio_hash = generate_audio_hash(openjson.input, openjson.voice)
    output_path = AUDIO_STORAGE / f"{audio_hash}.wav"

    if output_path.exists():
        logger.info(f"使用缓存音频: {audio_hash}")
        RECENT_FILES.append(output_path)
        return ResponseHandler.handle_file_response(output_path)

    logger.info(f"生成新音频: {openjson.input[:50]}...")
    temp_path = GradioClient.inference(openjson.voice, openjson.input)
    shutil.move(temp_path, output_path)

    RECENT_FILES.append(output_path)
    if len(RECENT_FILES) >= 5:
        oldest_file = RECENT_FILES.popleft()
        oldest_file.unlink(missing_ok=True)

    return ResponseHandler.handle_file_response(output_path)


@app.post("/audio/cleanup")
@ResponseHandler.handle_errors
async def force_cleanup(keep_last: int = 0):
    """强制清理接口"""
    cleanup_old_files(keep_last)
    return ResponseHandler.success(data={"keep_last": keep_last})


@app.get("/audio-list", response_class=HTMLResponse)
@ResponseHandler.handle_errors
async def audio_list_page():
    """音频文件查看页面"""
    return await root("audiolist.html")

@app.get("/Abyss", response_class=HTMLResponse)
@ResponseHandler.handle_errors
async def abyss_page():
    """ABYSS"""
    return await root("abyss.html")

@app.get("/lynchpin", response_class=HTMLResponse)
@ResponseHandler.handle_errors
async def lynchpin_page():
    """LYNCHPIN"""
    return await root("lynchpin.html")


@app.get("/settings", response_class=HTMLResponse)
@ResponseHandler.handle_errors
async def settings_page():
    """设置页面"""
    return await root("settings.html")


@app.post("/app/setconfig")
@ResponseHandler.handle_errors
async def set_config(config_items: Union[SetConfigObj, List[SetConfigObj]]):
    """设置参数并写入配置的方法"""
    items = [config_items] if isinstance(config_items, SetConfigObj) else config_items
    cm = ConfigTools("config/config.yaml")
    config = cm.read_config()

    for item in items:
        if item.section not in config:
            config[item.section] = OrderedDict()
        config[item.section][item.key] = item.value

    if cm.write_config(config) != 0:
        raise ResponseHandler.error(
            message="配置文件写入失败",
            error_type=ErrorTypes.CONFIG_WRITE_ERROR
        )

    return ResponseHandler.success(data={"updated": len(items)})


@app.post("/app/resetconfig")
@ResponseHandler.handle_errors
async def reset_config(confirm: ResetConfigObj):
    """重置参数并写入配置的方法"""
    if not confirm.confirm:
        raise ResponseHandler.error(
            message="需要确认才能重置",
            error_type=ErrorTypes.VALIDATION_ERROR
        )

    cm = ConfigTools("config/config.yaml")
        # 严格按照顺序
    default_config = OrderedDict([
            ("cutting", OrderedDict([("cutting_mode", "Slice once every 4 sentences")])),
            ("global", OrderedDict([("use_new_api", False)])),
            ("gpt", OrderedDict([
                ("temperature", 0.65),
                ("top_k", 15),
                ("top_p", 0),
                ("speed", 1),
                ("if_freeze", False)
            ])),
            ("reference", OrderedDict([
                ("no_reference_mode", False),
                ("reference_audio_local", ""),
                ("reference_audio_url",
                 "https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1739002890857/audio.wav"),
                ("reference_audio_language", "Chinese"),
                ("reference_audio_text",
                 "阿米娅看上去还是这么瘦弱，这个年纪的孩子，个子是不是应该更高一点才对？她到底有没有好好吃饭呢。"),
                ("inp_refs", None)
            ])),
            ("inference", OrderedDict([("inference_text_language", "中英混合")])),
            ("minecraft_api_key",
             OrderedDict([("minecraft_api_key", "sk-12345678abcdefgh12345678abcdefgh12345678abcdefgh")])),
            ("mode", OrderedDict([("mode", "tts")]))
        ])


    if cm.write_config(default_config) != 0:
        raise ResponseHandler.error(
            message="重置配置失败",
            error_type=ErrorTypes.CONFIG_WRITE_ERROR
        )

    return ResponseHandler.success()


@app.api_route("/app/getconfig", methods=["GET", "POST"])  # 允许两种方法
@ResponseHandler.handle_errors
async def get_config(gc: GetConfigObj = Depends()):
    """获取配置文件参数的方法
    1. 全部 -> 全部config
    2. 部分 -> 部分的config
    3. 否则就是返回值
    Note: 此方法暂不可被统一处理错误响应方法处理
    """
    cm = ConfigTools("config/config.yaml")
    config = cm.read_config()

    if gc.section == "all":
        return {"msg": "OK", "code": 0, "value": config}

    if gc.key is None:
        if gc.section in config:
            return {"msg": "OK", "code": 0, "section": gc.section, "value": config[gc.section]}
        else:
            return {"msg": "FAILED", "code": 1, "detail": "Section not found"}

    if gc.section in config and gc.key in config[gc.section]:
        return {"msg": "OK", "code": 0, "section": gc.section, "key": gc.key, "value": config[gc.section][gc.key]}
    return {"msg": "FAILED", "code": 1, "detail": "Key not found"}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "MiddleAPI:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False, #开发请设置为True
        workers=4
    )
