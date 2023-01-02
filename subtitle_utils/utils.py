# -*- coding: utf-8 -*-
# @Time    : 12/31/22 9:53 AM
# @FileName: utils.py
# @Software: PyCharm
# @Github    ：sudoskys
import os
import pysrt


class SrtParse(object):
    def __init__(self):
        pass

    def parse(self, files: str = "", strs: str = ""):
        if not any([files, strs]):
            raise Exception("Missing srt?")
        if files:
            return pysrt.open(path=files)
        if strs:
            return pysrt.from_string(source=strs)
