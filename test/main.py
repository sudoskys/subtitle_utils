# -*- coding: utf-8 -*-
# @Time    : 1/2/23 11:48 AM
# @FileName: main.py
# @Software: PyCharm
# @Github    ：sudoskys
from test_method_get import get_convert

if __name__ == "__main__":
    name = "srt2bcc"
    pre = name.split("2")[0]
    aft = name.split("2")[1]
    with open(f"test.{pre}", "r") as f:
        pre_content = f.read()
    result = get_convert(pre=pre, aft=aft, input_str=pre_content)
    print(result)
