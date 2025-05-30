#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : MiddleAPI
# @File : LogUtils.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/5/15 23:14

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)

import logging

from typing import Optional, Dict
from pathlib import Path

class LogUtils:
    """统一日志管理工具类"""

    _loggers = {}  # 缓存已创建的Logger实例

    @classmethod
    def init_logging(
            cls,
            name: str = "root",
            level: int = logging.INFO,
            format_str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            log_file: Optional[Path] = None,
            suppress_libs: Optional[Dict[str, int]] = None
    ) -> logging.Logger:
        """
        初始化日志配置
        :param name: Logger名称（如模块名）
        :param level: 日志级别（默认INFO）
        :param format_str: 日志格式
        :param log_file: 日志文件路径（None表示不写入文件）
        :param suppress_libs: 需要抑制的第三方库日志级别（如{"httpx": logging.WARNING}）
        :return: 配置好的Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # 抑制第三方库日志
        if suppress_libs:
            for lib, lib_level in suppress_libs.items():
                logging.getLogger(lib).setLevel(lib_level)

        # 创建Logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 清除旧Handler（避免重复日志）
        if logger.handlers:
            logger.handlers.clear()

        # 控制台Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(console_handler)



        return logger

    @classmethod
    def get_logger(cls, name: str = "root") -> logging.Logger:
        """获取已存在的Logger实例"""
        return cls._loggers.get(name, logging.getLogger(name))

