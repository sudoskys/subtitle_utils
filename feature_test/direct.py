# -*- coding: utf-8 -*-
# @Time    : 2024/1/19 上午12:01
# @Author  : sudoskys
# @File    : direct.py
# @Software: PyCharm
from subtitle_utils import srt2bcc

_result = srt2bcc(content="1\n00:00:00,000 --> 00:00:01,000\nHello World")
print(_result)
