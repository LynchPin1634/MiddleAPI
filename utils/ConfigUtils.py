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

import logging
import yaml
import os

from utils.LogUtils import LogUtils

logger = LogUtils.get_logger("ConfigUtils")


class ConfigTools:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self._create_empty_config()

    def _create_empty_config(self):
        """

        Returns: None

        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            yaml.dump({}, f, default_flow_style=False, allow_unicode=True)

    def read_config(self):
        """

        Returns: Config context.

        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return 1

    def write_config(self, config_data):
            """

            Args:
                config_data: new config data.

            Returns: status.

            """
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        config_data,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=True
                        )
                return 0
            except yaml.YAMLError:
                logger.error("写入配置文件失败！")
                return 1

    def get_value(self, key, default=None):
        """

        Args:
            key: Config key.
            default: If no value use this value.

        Returns:

        """
        config = self.read_config()
        return config.get(key, default)