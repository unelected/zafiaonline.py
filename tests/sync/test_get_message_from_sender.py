import pytest

from emailnator.sync.email_generator import EmailGenerator
from emailnator.asyncio.email_generator import AsyncEmailGenerator
from typing import cast


class DummyAsync:
    async def parse_message_from_sender(self, messages, sender):
        for msg in messages:
            if sender in msg.get('from', ''):
                return msg.get('subject', None)
        return None

@pytest.fixture
def email_gen():
    import asyncio
    gen = EmailGenerator.__new__(EmailGenerator)  # минуем __init__
    gen._loop = asyncio.get_event_loop()
    dummy_async = DummyAsync()
    gen._async = cast(AsyncEmailGenerator, dummy_async)
    return gen

def test_valid_message(email_gen):
    messages = [
        {'from': 'Mafia Online <mafia@mail.dottap.com>', 'subject': 'Mafia Online Registration', 'time': 'Just Now'},
        {'from': 'Other <other@mail.com>', 'subject': 'Hello', 'time': '1h ago'}
    ]
    result = email_gen.parse_message_from_sender(messages, 'Mafia Online')
    assert result == 'Mafia Online Registration'

def test_message_not_found(email_gen):
    messages = [
        {'from': 'Other <other@mail.com>', 'subject': 'Hello', 'time': '1h ago'}
    ]
    result = email_gen.parse_message_from_sender(messages, 'Mafia Online')
    assert result is None

def test_invalid_messages_type(email_gen):
    with pytest.raises(ValueError):
        email_gen.parse_message_from_sender("not a list", "Mafia Online")

def test_invalid_sender_type(email_gen):
    messages = [{'from': 'Mafia Online <mafia@mail.dottap.com>', 'subject': 'Mafia Online Registration'}]
    with pytest.raises(ValueError):
        email_gen.parse_message_from_sender(messages, "")

def test_empty_messages_list(email_gen):
    messages = []
    result = email_gen.parse_message_from_sender(messages, "Mafia Online")
    assert result is None
