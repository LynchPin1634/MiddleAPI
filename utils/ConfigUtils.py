#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project : 2025-MiddleAPI
# @File : ConfigUtils.py
# @IDE : PyCharm
# @Author : DeckDes (deckdes@outlook.com)
# @Co-Author : Ashley Lee (nekokecore@emtips.net)
# @Date : 2025/4/12 21:42

# Copyright 2025 DeckDes (deckdes@outlook.com)
# Copyright 2025 Ashley Lee (nekokecore@emtips.net)


from collections import OrderedDict

import logging
import yaml
import os


logger = logging.getLogger("MiddleAPI")


class ConfigTools:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self._create_empty_config()

    def _create_empty_config(self):
        # 严格按照要求的顺序和结构创建配置
        default_config = OrderedDict([
            ("cutting", OrderedDict([("cutting_mode", "Slice once every 4 sentences")])),
            ("global", OrderedDict([("use_new_api", False)])),
            ("gpt", OrderedDict([
                ("temperature", 0.25),
                ("top_k", 1),
                ("top_p", 0),
                ("speed", 1),
                ("if_freeze", False)
            ])),
            ("reference", OrderedDict([
                ("no_reference_mode", False),
                ("reference_audio_local", ""),
                ("reference_audio_url", ""),
                ("reference_audio_language", "Chinese"),
                ("reference_audio_text", ""),
                ("inp_refs", None)
            ])),
            ("inference", OrderedDict([("inference_text_language", "中英混合")])),
            ("minecraft_api_key", OrderedDict([("minecraft_api_key", "")])),
            ("mode", OrderedDict([("mode", "tts")]))
        ])
        self.write_config(default_config)

    def read_config(self):
        """读取config.yaml内容的方法"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.load(f, Loader=yaml.SafeLoader) or OrderedDict()
        except (yaml.YAMLError, FileNotFoundError) as e:
            logger.error(f"读取配置文件失败: {e}")
            return OrderedDict()

    def write_config(self, config_data):
        """写入config.yaml内容的方法"""
        def represent_ordereddict(dumper, data):
            return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

        def represent_none(dumper, _):
            return dumper.represent_scalar('tag:yaml.org,2002:null', '')
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

            # 确保配置有完整的结构
            full_config = self._ensure_full_structure(config_data)

            with open(self.file_path, 'w', encoding='utf-8') as f:
                yaml.add_representer(OrderedDict,
                                     lambda dumper, data: dumper.represent_mapping(
                                         'tag:yaml.org,2002:map', data.items()))

                yaml.dump(full_config, f,
                          default_flow_style=False,
                          allow_unicode=True,
                          sort_keys=False,
                          width=1000,  # 避免自动换行
                          indent=2)  # 缩进2个空格
            return 0
        except Exception as e:
            logger.error(f"写入配置文件失败: {e}")
            return 1

    def _ensure_full_structure(self, config_data):
        """确保配置包含所有必要的部分和键，并保持顺序"""
        # 严格顺序
        template = OrderedDict([
            ("cutting", OrderedDict([("cutting_mode", "")])),
            ("global", OrderedDict([("use_new_api", "")])),
            ("gpt", OrderedDict([
                ("temperature", ""),
                ("top_k", ""),
                ("top_p", ""),
                ("speed", ""),
                ("if_freeze", "")
            ])),
            ("reference", OrderedDict([
                ("no_reference_mode", ""),
                ("reference_audio_local", ""),
                ("reference_audio_url", ""),
                ("reference_audio_language", ""),
                ("reference_audio_text", ""),
                ("inp_refs", None)

            ])),
            ("inference", OrderedDict([("inference_text_language", "")])),
            ("minecraft_api_key", OrderedDict([("minecraft_api_key", "")])),
            ("mode", OrderedDict([("mode", "")]))
        ])

        # 合并传入配置到模板中
        for section in template:
            if section in config_data:
                for key in template[section]:
                    if key in config_data[section]:
                        if section == "reference" and key == "inp_refs":
                            val = config_data[section][key]
                            template[section][key] = None if val in ("", None) else val
                        else:
                            template[section][key] = config_data[section][key]


        return template


    def get_value(self, key, default=None):
        """

        Args:
            key: Config key.
            default: If no value use this value.

        Returns:

        """
        config = self.read_config()
        return config.get(key, default)