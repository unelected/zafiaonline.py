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
class TestAsyncEmailGeneratorGetMessage:

    async def test_valid_inputs_return_message_content(self):
        """Should return message content when email and message_id are valid."""
        mock_message_getter = AsyncMock()
        mock_message_getter.get_message.return_value = "<html>Message body</html>"

        gen = await AsyncEmailGenerator()
        gen._message_getter = mock_message_getter

        result = await gen.get_message("user@example.com", "abc123")

        assert isinstance(result, str)
        assert "<html>" in result
        mock_message_getter.get_message.assert_awaited_once_with("user@example.com", "abc123")

    async def test_empty_email_raises_valueerror(self):
        """Should raise ValueError when email is empty."""
        gen = await AsyncEmailGenerator()
        gen._message_getter = AsyncMock()

        with pytest.raises(ValueError, match="non-empty string"):
            await gen.get_message("", "abc123")

    async def test_invalid_email_format_raises_valueerror(self):
        """Should raise ValueError when email format is invalid."""
        gen = await AsyncEmailGenerator()
        gen._message_getter = AsyncMock()

        with pytest.raises(ValueError, match="Invalid email format"):
            await gen.get_message("invalid-email", "abc123")

    async def test_empty_message_id_raises_valueerror(self):
        """Should raise ValueError when message_id is empty."""
        gen = await AsyncEmailGenerator()
        gen._message_getter = AsyncMock()

        with pytest.raises(ValueError, match="Message ID must be a non-empty string"):
            await gen.get_message("user@example.com", "")

    async def test_message_getter_raises_runtimeerror(self):
        """Should propagate RuntimeError if underlying getter fails."""
        mock_message_getter = AsyncMock()
        mock_message_getter.get_message.side_effect = RuntimeError("Message fetch failed")

        gen = await AsyncEmailGenerator()
        gen._message_getter = mock_message_getter

        with pytest.raises(RuntimeError, match="Message fetch failed"):
            await gen.get_message("user@example.com", "abc123")
