from subtitle_utils import show_available, get_method


def get_test_subtitle(pre, aft):
    with open(f"test.{pre}", "r") as f:
        pre_content = f.read()
    with open(f"test.{aft}", "r") as f:
        aft_content = f.read()
    return pre_content, aft_content


def test_show_available():
    assert isinstance(show_available()[0], str), "Error Checking show list"


def test_srt2bcc():
    with open("test.bcc", "r") as f:
        bcc_exp = f.read()
    with open("test.srt", 'r') as file_io:
        test_result = get_method(method="srt2bcc")(content=file_io)
        test_result = test_result.replace("\n", "")
        bcc_exp = bcc_exp.replace("\n", "")
        assert test_result == bcc_exp, f"Error Checking srt2ass \n{test_result}"
