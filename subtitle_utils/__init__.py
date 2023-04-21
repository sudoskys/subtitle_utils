# -*- coding: utf-8 -*-
# @Time    : 12/29/22 10:06 PM
# @FileName: convert.py
# @Software: PyCharm
# @Github    ：sudoskys
import json
import pathlib
from typing import Union
from loguru import logger

# Child
from .BccConverter import BccConvert
from .AssConverter import AssConvert
from pydantic import BaseModel

about = None


class _Converter(object):
    def __init__(self):
        pass

    def srt2bcc(self,
                strs: Union[str],
                **kwargs
                ) -> str:
        result = BccConvert().srt2bcc(files=strs, about=about)
        result = json.dumps(result, ensure_ascii=False, indent=None)
        return result

    def vtt2bcc(self,
                strs: Union[str],
                **kwargs
                ) -> str:
        result = BccConvert().vtt2bcc(files=strs, about=about)
        result = json.dumps(result, ensure_ascii=False, indent=None)
        return result

    def ass2bcc(self,
                files: Union[str],
                **kwargs
                ) -> str:
        result = AssConvert().ass2srt(files=files)
        result = BccConvert().srt2bcc(files=result, about=about)
        result = json.dumps(result, ensure_ascii=False, indent=None)
        return result

    def ass2srt(self,
                files: Union[str],
                **kwargs
                ) -> str:
        result = AssConvert().ass2srt(files=files)
        return result

    def srt2ass(self,
                strs: Union[str],
                header: str = "",
                **kwargs
                ) -> str:
        result = AssConvert().srt2ass(strs=strs, header=header)
        return result

    def bcc2srt(self,
                strs: Union[str],
                **kwargs
                ) -> str:
        result = BccConvert().bcc2srt(files=strs)
        return result

    def bcc2ass(self,
                strs: Union[str],
                **kwargs
                ) -> str:
        result = BccConvert().bcc2srt(files=strs)
        result = AssConvert().srt2ass(strs=result)
        return result


class Returner(BaseModel):
    status: bool = False
    pre: str
    aft: str
    msg: str = "Unknown"
    data: str = None


__kira = _Converter()

_to_table = {
    "2srt": {
        "ass": __kira.ass2srt,
        "bcc": __kira.bcc2srt,
    },
    "2bcc": {
        "vtt": __kira.vtt2bcc,
        "srt": __kira.srt2bcc,
        "ass": __kira.ass2bcc,
    },
    "2ass": {
        "srt": __kira.srt2ass,
        "bcc": __kira.bcc2ass,
    },
}


def SeeAvailableMethods() -> list:
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


def FormatConverter(pre: str, aft: str,
                    files: str = "",
                    strs: str = "",
                    **kwargs
                    ) -> Returner:
    """
    转换管线
    :param strs: 必须是字符串
    :param pre: 先前的格式
    :param aft: 转换为什么
    :param files: 必须是文件绝对路径
    :return: class Returner
    """
    _aft = f"2{aft}"
    if not strs and not files:
        return Returner(status=False, pre=pre, aft=aft, msg="Miss arg")
    # 检查类型
    if not _to_table.get(_aft):
        return Returner(status=False, pre=pre, aft=aft, msg="Unsupported to format")
    if not _to_table.get(_aft).get(pre):
        return Returner(status=False, pre=pre, aft=aft, msg="Unsupported from format")
    # 同步数据
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=True)
    # 调用函数
    func = _to_table[_aft][pre]
    try:
        if not files:
            _b = bytes(strs, 'utf8')
            tmp.write(_b)
            tmp.seek(0)
            files = tmp.name
        if not strs:
            with pathlib.Path(files).open("r") as ori:
                strs = ori.read()
        _result = func(strs=strs, files=files, **kwargs)
    except Exception as e:
        logger.error(f"{pre}->{aft}:{e}")
        return Returner(status=False, pre=pre, aft=aft, msg="Error occur")
    else:
        return Returner(status=True, pre=pre, aft=aft, data=_result, msg="")
    finally:
        tmp.close()
