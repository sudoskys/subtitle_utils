# -*- coding: utf-8 -*-
# @Time    : 1/2/23 11:13 AM
# @FileName: test.py
# @Software: PyCharm
# @Github    ：sudoskys

import src.subtitle_utils as subtitle_utils

method = subtitle_utils.SeeAvailableMethods()
print(method)


def get_convert(pre: str = "ass", aft: str = "srt", input_str: str = None) -> str:
    _result_group = subtitle_utils.FormatConverter(pre=pre, aft=aft, strs=input_str)
    _result_group: subtitle_utils.Returner
    if not _result_group.status:
        print(_result_group.dict())
        return ""
    result: str
    result = _result_group.data
    print(f"{_result_group.pre}->{print(_result_group.aft)}")
    print(_result_group.msg)
    return result
