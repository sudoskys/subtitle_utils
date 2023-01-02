# -*- coding: utf-8 -*-
# @Time    : 12/30/22 2:54 PM
# @FileName: AssConverter.py
# @Software: PyCharm
# @Github    ：sudoskys
import re
from pathlib import Path
from pyasstosrt import Subtitle

from .utils import SrtParse


class AssUtils(object):
    @staticmethod
    def defultHeader() -> str:
        return """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&HF0000000,&H00000000,&HF0000000,1,0,0,0,100,100,0,0.00,1,1,0,2,30,30,10,134

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
"""

    def ass_content(self, content, header: str) -> str:
        """
        字幕转换
        :param timestamps: 时间轴
        :param subtitles: 字幕
        :param header: 头
        :return: 合成字幕
        """
        subs = SrtParse().parse(strs=content)
        timestamps = [[str(sub.start), str(sub.end)] for sub in subs]
        subtitles = [sub.text for sub in subs]
        header = header if header else AssUtils.defultHeader()
        content = header + '\n'
        body = {
            'dialogue': 'Dialogue: ',
            'front_time': '',
            'behind_time': '',
            'default': 'Default',
            'ntp': 'NTP',
            '0000': '0000',
            'sub': ',',
        }
        count = len(subtitles)
        for c in range(count):
            start = timestamps[c][0]  # 字幕起始时间
            start = start[:1] + ',' + start[1:8] + '.' + start[-2:]
            end = timestamps[c][1]  # 字幕结束时间
            end = end[1:8] + '.' + end[-2:]
            timeline = ','.join([start, end])  # 合成时间轴
            subtitle = subtitles[c]  # 当前字幕
            sub_tilte_n = [  # 字幕列表格式化
                body['dialogue'] + timeline,
                body['default'],
                body['ntp'],
                body['0000'],
                body['0000'],
                body['0000'] + ',',
                subtitle]
            content += ','.join(sub_tilte_n)
            content += '\n'
        return content


class AssConvert(object):

    def ass2srt(self, files: str) -> str:
        path = Path(files)
        sub = Subtitle(path)
        dialog = sub.export(output_dialogues=True)
        _result = []
        for dialogue in dialog:
            _result.append(str(dialogue))
        return "".join(_result)

    def srt2ass(self, strs: str, header: str = "") -> str:
        content = AssUtils().ass_content(content=strs, header=header)
        return content

# res = AssConvert().ass2srt(files="../test/sub.ass")
# print(res)
