import asyncio
from unittest.mock import AsyncMock
from typing import cast
import pytest
from emailnator.sync.email_generator import EmailGenerator

# Допустим, у тебя есть DummyAsync для тестов
class DummyAsync:
    def parse_message_from_sender(self, messages, sender):
        for msg in messages:
            if sender in msg.get("from", ""):
                return msg.get("subject")
        return None

def test_parse_message_from_sender_success():
    messages = [
        {"from": "Mafia Online <mafia@mail.dottap.com>", "subject": "Mafia Online Registration", "time": "Just Now"},
        {"from": "AI TOOLS", "subject": "AI Newsletter", "time": "10 mins ago"}
    ]
    sender = "Mafia Online <mafia@mail.dottap.com>"

    email_gen = EmailGenerator.__new__(EmailGenerator)
    email_gen._loop = asyncio.get_event_loop()
    email_gen._async = cast(AsyncMock, DummyAsync())

    result = email_gen.parse_message_from_sender(messages, sender)
    assert result == "Mafia Online Registration"

def test_parse_message_from_sender_not_found():
    messages = [
        {"from": "AI TOOLS", "subject": "AI Newsletter", "time": "10 mins ago"}
    ]
    sender = "Mafia Online <mafia@mail.dottap.com>"

    email_gen = EmailGenerator.__new__(EmailGenerator)
    email_gen._loop = asyncio.get_event_loop()
    email_gen._async = cast(AsyncMock, DummyAsync())

    result = email_gen.parse_message_from_sender(messages, sender)
    assert result is None

def test_parse_message_from_sender_invalid_messages():
    email_gen = EmailGenerator.__new__(EmailGenerator)
    email_gen._loop = asyncio.get_event_loop()
    email_gen._async = cast(AsyncMock, DummyAsync())

    with pytest.raises(ValueError):
        email_gen.parse_message_from_sender("not a list", "sender@example.com") # type: ignore

def test_parse_message_from_sender_invalid_sender():
    email_gen = EmailGenerator.__new__(EmailGenerator)
    email_gen._loop = asyncio.get_event_loop()
    email_gen._async = cast(AsyncMock, DummyAsync())

    with pytest.raises(ValueError):
        email_gen.parse_message_from_sender([], "")
