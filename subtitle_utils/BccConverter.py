# -*- coding: utf-8 -*-
# @Time    : 12/30/22 2:39 PM
# @FileName: BccConvert.py
# @Software: PyCharm
# @Github    ：sudoskys

import re
import os
import json
import pyvtt
import pysrt

from typing import Union
from datetime import datetime
from loguru import logger


#####
# BCC2SRT
# SRT2BCC
# VTT2BCC
#####


class BccParser(object):
    def __init__(self):
        pass

    def _parse(self, content: str):
        try:
            return json.loads(content)
        except Exception as e:
            raise Exception(e)

    def parseFile(self, files):
        path = files if files else ""
        if not os.path.exists(path):
            return
        with open(files, "r") as f:
            return self._parse(f.read())

    def parseStr(self, files):
        strs = files if files else ""
        return self._parse(strs)


class BccConvert(object):
    def __init__(self):
        self.item = {
            "from": 0,
            "to": 0,
            "location": 2,
            "content": "",
        }

    def merge_timeline(self, time_line: list):
        """
        防止时间码重合，压扁时间轴
        :param time_line:
        :param additive: 附加字幕
        :return:
        """
        # 制作爆破点
        _time_dot = {}
        for item in time_line:
            _start = item["from"]
            _end = item["to"]
            _content = item["content"]
            _uid = _start + _end
            import uuid
            uid1 = uuid.uuid1()
            uid2 = uuid.uuid1()
            uid = uuid.uuid1()
            _time_dot[uid1.hex] = {"time": _start, "type": "start", "content": _content, "group": uid}
            _time_dot[uid2.hex] = {"time": _end, "type": "end", "content": _content, "group": uid}

        # 查找当前点的字幕。
        def sub_title_now(dot: float):
            sub_title_n = []
            rev = False
            for it in time_line:
                if it["from"] <= dot < it["to"]:
                    if "字幕" in it["content"] and len(it["content"]) > 7:
                        rev = True
                    sub_title_n.append(it["content"])
            if rev:
                sub_title_n = reversed(sub_title_n)
            return "\n".join(sub_title_n)

        # 开始遍历时间轴划分Start End
        tmp_cap = []
        _sorted_timeline = sorted(_time_dot.items(), key=lambda x: x[1]["time"], reverse=False)
        for key, time in _sorted_timeline:
            _type = time["type"]
            _time = time["time"]
            _group = time["group"]
            _content = time["content"]
            tmp_cap.append(_time)
        _result = []
        for dot in range(0, len(tmp_cap) - 1):
            _now = tmp_cap[dot]
            _next = tmp_cap[dot + 1]
            _text = sub_title_now(_now)
            if not _text:
                continue
            _from = _now
            _to = _next
            _item = {
                "from": _from,
                "to": _to,
                "location": 2,
                "content": _text,
            }
            _result.append(_item)

        # 归并内容
        def merge(timeline: list):
            merged = False
            for it in range(0, len(timeline) - 1):
                now = timeline[it]
                ext = timeline[it + 1]
                if now["to"] == ext["from"]:
                    if now["content"] == ext["content"]:
                        merged = True
                        now["to"] = ext["to"]
                        timeline.remove(ext)
                        break
            if merged:
                return merge(timeline)
            else:
                return timeline

        def merge_large(timeline: list):
            merge_out = False
            while not merge_out:
                _merge = False
                for it in range(0, len(timeline) - 1):
                    now = timeline[it]
                    ext = timeline[it + 1]
                    if now["to"] == ext["from"]:
                        if now["content"] == ext["content"]:
                            _merge = True
                            now["to"] = ext["to"]
                            timeline.remove(ext)
                            break
                merge_out = False if _merge else True
            return timeline

        return merge_large(_result)

    def process_body(self, subs, about: str = None):
        _origin = []
        if about:
            _origin.append({
                "from": 0.0,
                "to": 5,
                "location": 2,
                "content": about,
            })
        _origin.extend([
            {
                "from": sub.start.ordinal / 1000,
                "to": sub.end.ordinal / 1000,
                "location": 2,
                "content": sub.text,
            }
            for sub in subs
        ])
        _fix = self.merge_timeline(_origin)
        return _fix

    def time2str(self, time: float):
        return datetime.utcfromtimestamp(time).strftime("%H:%M:%S,%f")[:-3]

    def srt2bcc(self, files: Union[str], about: str = None):
        """
        srt2bcc 将 srt 转换为 bcc B站字幕格式
        :return:
        """
        path = files if files else ""
        if os.path.exists(path):
            subs = pysrt.open(path=files)
        else:
            subs = pysrt.from_string(source=files)
        body = self.process_body(subs, about=about)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": body
        }
        return bcc if subs else {}

    def bcc2srt(self, files: Union[str]):
        """
        bcc2srt 将 bcc 转换为 srt 字幕格式
        :return:
        """
        path = files if files else ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                subs = json.load(f)
        else:
            subs = json.loads(path)
        srt = ""
        count = 0
        for single_str in subs["body"]:
            count += 1
            content_str = single_str['content']
            from_str = single_str['from']
            to_str = single_str['to']
            srt += f"{count}\n"
            srt += f"{self.time2str(from_str)} --> {self.time2str(to_str)}\n"
            srt += f"{content_str}\n\n"
        return srt[:-1] if subs else ""

    def vtt2bcc(self, files, threshold=0.1, word=True, about: str = None):
        path = files if files else ""
        if os.path.exists(path):
            subs = pyvtt.open(path)
        else:
            subs = pyvtt.from_string(path)
        # NOTE 按照 vtt 的断词模式分隔 bcc
        caption_list = []
        if not word:
            caption_list = [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text_without_tags.split("\n")[-1],
                }
                for sub in subs
            ]
        else:
            for i, sub in enumerate(subs):
                text = sub.text

                start = sub.start.ordinal / 1000
                end = sub.end.ordinal / 1000
                try:
                    idx = text.index("<")
                    pre_text = text[:idx]
                    regx = re.compile(r"<(.*?)><c>(.*?)</c>")
                    for t_str, match in regx.findall(text):
                        pre_text += match
                        t = datetime.strptime(t_str, r"%H:%M:%S.%f")
                        sec = (
                                t.hour * 3600
                                + t.minute * 60
                                + t.second
                                + t.microsecond / 10 ** len((str(t.microsecond)))
                        )
                        final_text = pre_text.split("\n")[-1]

                        if caption_list and (
                                sec - start <= threshold
                                or caption_list[-1]["content"] == final_text
                        ):
                            caption_list[-1].update(
                                {
                                    "to": sec,
                                    "content": final_text,
                                }
                            )
                        else:
                            caption_list.append(
                                {
                                    "from": start,
                                    "to": sec,
                                    "location": 2,
                                    "content": final_text,
                                }
                            )
                        start = sec
                except:
                    final_text = sub.text.split("\n")[-1]
                    if caption_list and caption_list[-1]["content"] == final_text:
                        caption_list[-1].update(
                            {
                                "to": end,
                                "content": final_text,
                            }
                        )
                    else:
                        if caption_list and end - start < threshold:
                            start = caption_list[-1]["to"]
                        caption_list.append(
                            {
                                "from": start,
                                "to": end,
                                "location": 2,
                                "content": final_text,
                            }
                        )

        # print(len(caption_list))
        # NOTE 避免超出视频长度
        last = caption_list[-1]
        last["to"] = last.get("from") + 0.1
        body = self.process_body(caption_list, about=about)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": body,
        }
        return bcc if subs else {}


"""
# 部分原始代码协议:https://github.com/FXTD-ODYSSEY/bilibili-subtile-uploader/blob/main/LICENSE
MIT License

Copyright (c) 2020 智伤帝

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
