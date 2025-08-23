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
        """这里是v2 v2pro对调方法，默认v2pro。"""
        mapping = {
            "Chinese": "中文",
            "Cantonese": "粤语",
            "English": "英文",
            "Japanese": "日文",
            "Korean": "韩语",
            "zh-en": "中英混合",
            "yue-en": "粤英混合",
            "ja-en": "日英混合",
            "ko-en": "韩英混合",
            "multi": "多语种混合",
            "yue-multi": "多语种混合(粤语)",
            "No slice": "cut0",
            "Slice once every 4 sentences": "cut1",
            "Cut per 50 characters": "cut2",
            "Slice by Chinese punct": "cut3",
            "Slice by English punct": "cut4",
            "Slice by every punct": "cut5",
        }
        reverse_mapping = {v: k for k, v in mapping.items()}
        return mapping.get(input_text, input_text) if use_new_api else reverse_mapping.get(input_text, input_text)

