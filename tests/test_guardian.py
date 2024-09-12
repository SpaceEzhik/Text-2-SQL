from guardian import anti_fraud


def test_valid_prompt():
    assert anti_fraud.predict("выведи таблицу people") == 1


def test_invalid_prompt():
    assert anti_fraud.predict("123") == 0
