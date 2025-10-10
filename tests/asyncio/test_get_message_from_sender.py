import pytest
from unittest.mock import AsyncMock

from emailnator.asyncio.email_generator import AsyncEmailGenerator


@pytest.mark.asyncio
async def test_get_message_from_sender_success():
    generator = await AsyncEmailGenerator()
    generator.get_messages = AsyncMock(return_value=[
        {'messageID': '123', 'from': 'Bob', 'subject': 'Hello'}
    ])
    generator.get_message = AsyncMock(return_value="This is the message text")

    result = await generator.get_message_from_sender('Bob', 'test@example.com')
    assert result == "This is the message text"
    generator.get_messages.assert_awaited_once_with('test@example.com')
    generator.get_message.assert_awaited_once_with('test@example.com', '123')


@pytest.mark.asyncio
async def test_get_message_from_sender_not_found():
    generator = await AsyncEmailGenerator()
    generator.get_messages = AsyncMock(return_value=[
        {'messageID': '123', 'from': 'Alice', 'subject': 'Hello'}
    ])
    generator.get_message = AsyncMock()

    result = await generator.get_message_from_sender('Bob', 'test@example.com')
    assert result is None
    generator.get_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_message_from_sender_invalid_sender_email():
    generator = await AsyncEmailGenerator()
    generator.get_messages = AsyncMock()
    generator.get_message = AsyncMock()

    with pytest.raises(ValueError):
        await generator.get_message_from_sender('', 'test@example.com')

    with pytest.raises(ValueError):
        await generator.get_message_from_sender('Bob', '')

    with pytest.raises(ValueError):
        await generator.get_message_from_sender(None, 'test@example.com')

    with pytest.raises(ValueError):
        await generator.get_message_from_sender('Bob', None)


@pytest.mark.asyncio
async def test_get_message_from_sender_invalid_messages_return():
    generator = await AsyncEmailGenerator()
    generator.get_messages = AsyncMock(return_value="not a list")
    generator.get_message = AsyncMock()

    with pytest.raises(ValueError):
        await generator.get_message_from_sender('Bob', 'test@example.com')


@pytest.mark.asyncio
async def test_get_message_from_sender_message_without_id():
    generator = await AsyncEmailGenerator()
    generator.get_messages = AsyncMock(return_value=[
        {'from': 'Bob', 'subject': 'Hello'}
    ])
    generator.get_message = AsyncMock()

    result = await generator.get_message_from_sender('Bob', 'test@example.com')
    assert result is None
    generator.get_message.assert_not_awaited()
