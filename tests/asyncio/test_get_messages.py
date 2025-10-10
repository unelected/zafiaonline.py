# Copyright (C) 2025 unelected
#
# This file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_generator. If not, see
# <https://www.gnu.org/licenses/>.

import pytest
from unittest.mock import AsyncMock
from emailnator.asyncio.email_generator import AsyncEmailGenerator

@pytest.mark.asyncio
class TestAsyncEmailGeneratorGetMessages:

    async def test_valid_email_returns_messages(self):
        """Should return a list of message dicts when email is valid."""
        mock_message_getter = AsyncMock()
        mock_message_getter.get_message_list.return_value = [
            {"messageID": "abc123", "from": "AI Tools", "subject": "Hello", "time": "Now"}
        ]

        gen = await AsyncEmailGenerator()
        gen._message_getter = mock_message_getter

        result = await gen.get_messages("user@example.com")

        assert isinstance(result, list)
        assert all(isinstance(m, dict) for m in result)
        assert result[0]["messageID"] == "abc123"
        mock_message_getter.get_message_list.assert_awaited_once_with("user@example.com")

    async def test_empty_email_raises_valueerror(self):
        """Should raise ValueError if email is empty."""
        gen = await AsyncEmailGenerator()
        gen._message_getter = AsyncMock()

        with pytest.raises(ValueError, match="non-empty string"):
            await gen.get_messages("")

    async def test_invalid_email_format_raises_valueerror(self):
        """Should raise ValueError if email format is invalid."""
        gen = await AsyncEmailGenerator()
        gen._message_getter = AsyncMock()

        with pytest.raises(ValueError, match="Invalid email format"):
            await gen.get_messages("invalid-email")

    async def test_message_getter_raises_runtimeerror(self):
        """Should propagate RuntimeError if message_getter fails."""
        mock_message_getter = AsyncMock()
        mock_message_getter.get_message_list.side_effect = RuntimeError("API down")

        gen = await AsyncEmailGenerator()
        gen._message_getter = mock_message_getter

        with pytest.raises(RuntimeError, match="API down"):
            await gen.get_messages("user@example.com")
