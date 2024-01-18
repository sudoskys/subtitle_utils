# subtitle_utils

![cover](https://raw.githubusercontent.com/sudoskys/subtitle_utils/main/src/cover.jpg)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8|9|10|11-green" alt="Python" >
  <img src="https://img.shields.io/pypi/dm/subtitle_utils.svg" alt="Download">
</p>

Subtilte Conversion utils - ass2srt vtt2bcc srt2bcc ass2bcc and more

## Install

```
pip install -U subtitle_utils
```

## Usage

```python
import subtitle_utils

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
```
