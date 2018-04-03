import pytest

from handlers.messages.message import (parse_msg, check_for_answer, GREETING_KEYWORDS)


@pytest.mark.parametrize(
    "value", (["Hi"], ["hi"], ["hola", "como", "va"], ["holas"], ["hola"])
)
def test_greeting_answer(value):
    assert check_for_answer(value, GREETING_KEYWORDS)


@pytest.mark.parametrize("value", ("Hiasd", "ahi", "ahola", "hdsaolas", "ho la"))
def test_non_greeting_answeri(value):
    assert not check_for_answer(value, GREETING_KEYWORDS)
