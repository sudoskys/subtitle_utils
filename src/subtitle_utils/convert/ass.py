# -*- coding: utf-8 -*-
# @Time    : 2024/1/18 下午6:05
# @Author  : sudoskys
# @File    : ass.py
# @Software: PyCharm
import tempfile
from typing import Union, IO

from pyasstosrt import Subtitle

from ..parse import SrtParse
from ..schema import Convert

ASS_HEADER = """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&HF0000000,&H00000000,&HF0000000,1,0,0,0,100,100,0,0.00,1,1,0,2,30,30,10,134

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
"""


class AssConvert(Convert):
    @staticmethod
    def srt2ass(content: Union[str, IO],
                *,
                header: str = None) -> str:
        """
        Subtitle Converter
        :param content: subtitle path or content
        :param header: ASS HEADER (Style)
        :return: processed subtitle
        """
        assert isinstance(content, (str, IO)), "content must be str or IO"
        subs = SrtParse().parse(content=content)
        timestamps = [[str(sub.start), str(sub.end)] for sub in subs]
        subtitles = [sub.text for sub in subs]
        if header is None:
            header = ASS_HEADER
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

    @staticmethod
    def ass2srt(content: Union[str, IO]) -> str:
        assert isinstance(content, (str, IO)), "content must be str or IO"
        # write to temp file
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            if isinstance(content, str):
                f.write(content)
            else:
                f.write(content.read())
            f.close()
            sub = Subtitle(filepath=f.name)
            dialog = sub.export(output_dialogues=True)
            _result = []
            for dialogue in dialog:
                _result.append(str(dialogue))
        return "".join(_result)
