import pytest

from emailnator.asyncio.email_generator import AsyncEmailGenerator


@pytest.mark.asyncio
async def test_parse_message_from_sender_valid():
    messages = [
        {'messageID': '1', 'from': 'Alice', 'subject': 'Hello'},
        {'messageID': '2', 'from': 'Bob', 'subject': 'Hi'},
    ]
    generator = await AsyncEmailGenerator()
    result = await generator.parse_message_from_sender(messages, 'Bob')
    assert result == '2'


@pytest.mark.asyncio
async def test_parse_message_from_sender_not_found():
    messages = [
        {'messageID': '1', 'from': 'Alice', 'subject': 'Hello'},
    ]
    generator = await AsyncEmailGenerator()
    result = await generator.parse_message_from_sender(messages, 'Bob')
    assert result is None


@pytest.mark.asyncio
async def test_parse_message_from_sender_empty_messages():
    generator = await AsyncEmailGenerator()
    with pytest.raises(ValueError):
        await generator.parse_message_from_sender([], 'Alice')


@pytest.mark.asyncio
async def test_parse_message_from_sender_invalid_messages_type():
    generator = await AsyncEmailGenerator()
    with pytest.raises(ValueError):
        await generator.parse_message_from_sender("not a list", 'Alice')


@pytest.mark.asyncio
async def test_parse_message_from_sender_invalid_sender_type():
    messages = [
        {'messageID': '1', 'from': 'Alice', 'subject': 'Hello'},
    ]
    generator = await AsyncEmailGenerator()
    with pytest.raises(ValueError):
        await generator.parse_message_from_sender(messages, '')
    with pytest.raises(ValueError):
        await generator.parse_message_from_sender(messages, None)
