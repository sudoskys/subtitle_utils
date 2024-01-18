# -*- coding: utf-8 -*-
# @Author  : sudoskys,智伤帝
# @File    : bcc.py

import re
from datetime import datetime
from typing import Union, IO

from loguru import logger

from ..parse import VttParser, BccParser, SrtParse
from ..schema import Convert

#####
# BCC2SRT
# SRT2BCC
# VTT2BCC
#####

item = {
    "from": 0,
    "to": 0,
    "location": 2,
    "content": "",
}


class BccConvert(Convert):

    @staticmethod
    def _merge_timeline(time_line: list):
        """
        防止时间码重合，压扁时间轴
        :param time_line: 时间轴
        :return: 压扁后的时间轴
        """
        # 制作爆破点
        _time_dot = {}
        for items in time_line:
            _start = items["from"]
            _end = items["to"]
            _content = items["content"]
            _uid = _start + _end
            import uuid
            uid1 = uuid.uuid1()
            uid2 = uuid.uuid1()
            uid = uuid.uuid1()
            _time_dot[uid1.hex] = {"time": _start, "type": "start", "content": _content, "group": uid}
            _time_dot[uid2.hex] = {"time": _end, "type": "end", "content": _content, "group": uid}

        # 查找当前点的字幕。
        def sub_title_now(dot_: float):
            sub_title_n = []
            rev = False
            for it in time_line:
                if it["from"] <= dot_ < it["to"]:
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

    def _process_body(self, subs, about: str = None):
        """
        处理字幕内容
        :param subs: 字幕列表
        :param about:  关于字幕
        :return:  处理后的字幕内容
        """

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
        _fix = self._merge_timeline(_origin)
        return _fix

    @staticmethod
    def _time2str(time: float):
        return datetime.utcfromtimestamp(time).strftime("%H:%M:%S,%f")[:-3]

    def srt2bcc(self, content: Union[str, IO], about: str = None):
        """
        srt2bcc 将 srt 转换为 bcc B站字幕格式
        :param content: srt format
        :return:
        """
        subs = SrtParse().parse(content)
        body = self._process_body(subs, about=about)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": body
        }
        return bcc if subs else {}

    def bcc2srt(self, content: Union[str, IO]):
        """
        bcc2srt 将 bcc 转换为 srt 字幕格式
        :param content: bcc format
        :return:
        """
        subs = BccParser().parse(content)
        srt = ""
        count = 0
        for single_str in subs["body"]:
            count += 1
            content_str = single_str['content']
            from_str = single_str['from']
            to_str = single_str['to']
            srt += f"{count}\n"
            srt += f"{self._time2str(from_str)} --> {self._time2str(to_str)}\n"
            srt += f"{content_str}\n\n"
        return srt[:-1] if subs else ""

    def vtt2bcc(self, content: Union[str, IO], threshold=0.1, word=True, about: str = None):
        """
        vtt2bcc 将 vtt 转换为 bcc B站字幕格式
        :param content:  vtt format
        :param threshold:  两个字幕之间的间隔时间
        :param word:  是否按照断词模式分隔字幕
        :param about:  关于字幕
        :return:  bcc format
        """
        subs = VttParser().parse(content)
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
                except Exception as e:
                    logger.trace(e)
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
        body = self._process_body(caption_list, about=about)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": body,
        }
        return bcc if subs else {}
