# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
from io import TextIOBase
from typing import Union, IO, Callable, Any

from .convert.ass import AssConvert
from .convert.bcc import BccConvert

FOOTNOTE = None


def srt2bcc(content: Union[str, IO, TextIOBase]
            ) -> str:
    result = BccConvert().srt2bcc(content=content, about=FOOTNOTE)
    result = json.dumps(result, ensure_ascii=False, indent=None)
    return result


def vtt2bcc(content: Union[str, IO, TextIOBase]
            ) -> str:
    result = BccConvert().vtt2bcc(content=content, about=FOOTNOTE)
    result = json.dumps(result, ensure_ascii=False, indent=None)
    return result


def ass2bcc(content: Union[str, IO, TextIOBase]
            ) -> str:
    ass_result = AssConvert().ass2srt(content=content)
    result = BccConvert().srt2bcc(content=ass_result, about=FOOTNOTE)
    result = json.dumps(result, ensure_ascii=False, indent=None)
    return result


def ass2srt(content: Union[str, IO, TextIOBase]
            ) -> str:
    """
    :param content:
    :return: result
    """
    result = AssConvert().ass2srt(content=content)
    return result


def srt2ass(content: Union[str, IO, TextIOBase],
            *,
            header: str = None
            ) -> str:
    """
    :param content: srt str| IO
    :param header: ass subtitle style
    :return:
    """
    result = AssConvert().srt2ass(content=content, header=header)
    return result


def bcc2srt(content: Union[str, IO, TextIOBase],
            ) -> str:
    result = BccConvert().bcc2srt(content=content)
    return result


def bcc2ass(content: Union[str, IO, TextIOBase]
            ) -> str:
    bcc_result = BccConvert().bcc2srt(content=content)
    result = AssConvert().srt2ass(content=bcc_result)
    return result


_to_table = {
    "2srt": {
        "ass": ass2srt,
        "bcc": bcc2srt,
    },
    "2bcc": {
        "vtt": vtt2bcc,
        "srt": srt2bcc,
        "ass": ass2bcc,
    },
    "2ass": {
        "srt": srt2ass,
        "bcc": bcc2ass,
    },
}


def get_method(method: str) -> Callable[..., Any]:
    available_method = show_available()
    assert method in available_method, f"Not available in {available_method}"
    sub_key, key = method.split("2", maxsplit=1)
    top_key = f"2{key}"
    child = _to_table.get(top_key, None)
    assert child, f"{method} NotImplemented for top class"
    method_func = child.get(sub_key, None)
    assert method_func, f"{method} NotImplemented for sub class"
    return method_func


def show_available() -> list:
    """
    查询可用方法，返回功能列表
    :return:
    """
    _method = []
    for it in _to_table.keys():
        _child = _to_table[it]
        if not isinstance(_child, dict):
            continue
        _from = _child.keys()
        for ti in _from:
            _method.append(f"{ti}{it}")
    return _method
