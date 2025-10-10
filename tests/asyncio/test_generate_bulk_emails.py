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
class TestAsyncEmailGeneratorGenerateBulkEmails:

    async def test_valid_call_returns_list_of_emails(self):
        """Should return a list of valid email strings for valid emails_number."""
        mock_generators = AsyncMock()
        mock_generators.generate_bulk_emails.return_value = [
            "user1@example.com", "user2@example.com"
        ]

        gen = await AsyncEmailGenerator()
        gen._generators = mock_generators

        result = await gen.generate_bulk_emails("200")

        assert isinstance(result, list)
        assert all(isinstance(email, str) for email in result)
        assert len(result) == 2
        mock_generators.generate_bulk_emails.assert_awaited_once_with("200")

    async def test_invalid_emails_number_raises_valueerror(self):
        """Should raise ValueError when emails_number is not one of allowed values."""
        gen = await AsyncEmailGenerator()
        gen._generators = AsyncMock()

        with pytest.raises(ValueError, match="Invalid emails_number"):
            await gen.generate_bulk_emails("999")

    async def test_generator_returns_non_list_raises_runtimeerror(self):
        """Should raise RuntimeError if generator returns non-list data."""
        mock_generators = AsyncMock()
        mock_generators.generate_bulk_emails.return_value = "not-a-list"

        gen = await AsyncEmailGenerator()
        gen._generators = mock_generators

        with pytest.raises(RuntimeError, match="invalid data type"):
            await gen.generate_bulk_emails("100")

    async def test_generator_returns_empty_list_raises_runtimeerror(self):
        """Should raise RuntimeError if generator returns empty list."""
        mock_generators = AsyncMock()
        mock_generators.generate_bulk_emails.return_value = []

        gen = await AsyncEmailGenerator()
        gen._generators = mock_generators

        with pytest.raises(RuntimeError, match="empty list"):
            await gen.generate_bulk_emails("300")

    async def test_generator_returns_list_with_invalid_items_raises_runtimeerror(self):
        """Should raise RuntimeError if list contains non-string elements."""
        mock_generators = AsyncMock()
        mock_generators.generate_bulk_emails.return_value = ["ok@example.com", 123]

        gen = await AsyncEmailGenerator()
        gen._generators = mock_generators

        with pytest.raises(RuntimeError, match="invalid data type"):
            await gen.generate_bulk_emails("100")
