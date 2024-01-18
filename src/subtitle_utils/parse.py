# -*- coding: utf-8 -*-
# @Time    : 12/31/22 9:53 AM
# @FileName: parse.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
import os
import tempfile
from abc import ABC
from typing import Union, IO

import pysrt
import pyvtt
from pysrt import SubRipFile
from pyvtt import WebVTTFile


class Parser(ABC):
    """
    Base Parser
    """

    def parse(self, content: Union[str, IO]):
        raise NotImplementedError


class SrtParse(Parser):

    def parse(self, content: Union[str, IO]) -> SubRipFile:
        if isinstance(content, str):
            return pysrt.from_string(content)
        # write to temp file
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=True) as f:
            f.write(content.read())
            f.close()
            return pysrt.open(f.name)


class BccParser(Parser):

    @staticmethod
    def _parse(content: str):
        try:
            return json.loads(content)
        except Exception as e:
            raise e

    def parse_file(self, files):
        path = files if files else ""
        if not os.path.exists(path):
            return
        with open(files, "r") as f:
            return self._parse(f.read())

    def parse_str(self, sentence):
        strs = sentence if sentence else ""
        return self._parse(strs)

    def parse(self, content: Union[str, IO]) -> dict:
        """
        Parse bcc
        :param content: str or IO
        :return: json
        """
        if isinstance(content, str):
            return self.parse_str(content)
        return self.parse_file(content)


class VttParser(Parser):

    def parse(self, content: Union[str, IO]) -> WebVTTFile:
        """
        :param content:  str or IO
        :return:  pyvtt.WebVTTFile
        """
        if isinstance(content, str):
            return pyvtt.from_string(content)
        # write to temp file
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=True) as f:
            f.write(content.read())
            f.close()
            return pyvtt.open(f.name)
