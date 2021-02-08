from mail_me_my_sms.main import is_spam, SMS


def test_re():
    inputs = [
        ['您的验证码是123452', False],
        ['您的验证码是123452, 退订回T', False],
        ['blablabal，退订回T', True],
        ['blablabal，退订T', True],
        ['blablabal，回T退订', True],
        ['blablabal，TD退订', True],
    ]
    for text, result in inputs:
        assert is_spam(SMS(text=text)) is result
