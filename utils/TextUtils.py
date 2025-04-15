#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : TextUtils.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/4/12 21:42

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)

import re

class CleanText:
    @staticmethod
    def text(input_text: str) -> str:
        """
        移除文本中的以下内容（支持简单嵌套）：
        1. （中文括号内的内容）
        2. (英文括号内的内容)
        3. [中括号内的内容]
        4. {大括号内的内容}
        5. **双星号内的内容**
        6. *单星号内的内容*
        """

        while "（" in input_text and "）" in input_text:
            input_text = re.sub(r"（[^（）]*）", "", input_text)
        while "(" in input_text and ")" in input_text:
            input_text = re.sub(r"\([^()]*\)", "", input_text)
        while "[" in input_text and "]" in input_text:
            input_text = re.sub(r"\[[^][]*\]", "", input_text)
        while "{" in input_text and "}" in input_text:
            input_text = re.sub(r"\{[^{}]*\}", "", input_text)

        input_text = re.sub(r"\*\*.*?\*\*", "", input_text)
        input_text = re.sub(r"\*.*?\*", "", input_text)

        return input_text.strip()

class OldAPI:
    @staticmethod
    def old_api(use_new_api,input_text):
        """这里是v2 v3对调方法，默认v2。"""
        mapping = {
            "中文": "Chinese",
            "英文": "English",
            "日文": "Japanese",
            "不切": "No slice",
            "凑四句一切": "Slice once every 4 sentences",
            "凑50字一切": "Cut per 50 characters",
            "按中文句号。切": "Slice by Chinese punct",
            "按英文句号.切": "Slice by English punct",
            "按标点符号切": "Slice by every punct",
        }
        reverse_mapping = {v: k for k, v in mapping.items()}
        return mapping.get(input_text, input_text) if use_new_api else reverse_mapping.get(input_text, input_text)