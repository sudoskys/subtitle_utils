# subtitle_utils

![cover](https://raw.githubusercontent.com/sudoskys/subtitle_utils/main/src/cover.jpg)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8|9|10|11-green" alt="Python" >
  <img src="https://img.shields.io/pypi/dm/subtitle_utils.svg" alt="Download">
</p>

Subtilte Conversion Utils - ass2srt vtt2bcc srt2bcc ass2bcc and more!

## Install 🥽

```
pip install -U subtitle_utils
```

## Usage ☕️

```python
from subtitle_utils import get_method, show_available, srt2bcc

print("Available methods:")
print(show_available())

with open("test.srt", 'r') as file_io:
    test_result = get_method(method="srt2bcc")(content=file_io)
    print(test_result)

_result = srt2bcc(content="1\n00:00:00,000 --> 00:00:01,000\nHello World")
print(_result)
```
