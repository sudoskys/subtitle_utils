# -*- coding: utf-8 -*-
# @Time    : 1/2/23 11:13 AM
# @FileName: test.py
# @Software: PyCharm
# @Github    ：sudoskys
import sys

sys.path.append("..")

import subtitle_utils


def get_test_subtitle(pre, aft):
    with open(f"test.{pre}", "r") as f:
        pre_content = f.read()
    with open(f"test.{aft}", "r") as f:
        aft_content = f.read()
    return pre_content, aft_content


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


class TestClass:
    def test_SeeAvailableMethods(self):
        method = subtitle_utils.SeeAvailableMethods()
        assert type(method) == list

    def test_module(self):
        names = ["srt2bcc"]
        for name in names:
            pre = name.split("2")[0]
            aft = name.split("2")[1]
            pre_content, aft_content = get_test_subtitle(pre=pre, aft=aft)
            result = get_convert(pre=pre, aft=aft, input_str=pre_content)
            print(result)
            assert aft_content == result


if __name__ == '__main__':
    import pytest

    # 相当于在命令行当前目录中执行了 pytest
    pytest.main()
