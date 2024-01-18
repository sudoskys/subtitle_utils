# -*- coding: utf-8 -*-
# @Time    : 2024/1/18 下午4:22
# @Author  : sudoskys
# @File    : schema.py
# @Software: PyCharm
from abc import ABC
from enum import Enum


class SubtitleType(Enum):
    ASS = "ass"
    BCC = "bcc"
    SRT = "srt"
    VTT = "vtt"


class Convert(ABC):
    pass
