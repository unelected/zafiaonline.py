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
async def test_generate_email_success():
    gen = await AsyncEmailGenerator()
    gen._generators.generate_email = AsyncMock(return_value=["test@example.com", "x@example.com"])

    result = await gen.generate_email()

    assert result == "test@example.com"
    gen._generators.generate_email.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_email_empty_list():
    gen = await AsyncEmailGenerator()
    gen._generators.generate_email = AsyncMock(return_value=[])

    with pytest.raises(RuntimeError, match="no valid addresses"):
        await gen.generate_email()

@pytest.mark.asyncio
async def test_generate_email_none_returned():
    gen = await AsyncEmailGenerator()
    gen._generators.generate_email = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="no valid addresses"):
        await gen.generate_email()

@pytest.mark.asyncio
async def test_generate_email_raises_from_inner():
    gen = await AsyncEmailGenerator()

    async def fail():
        raise RuntimeError("Internal failure")

    gen._generators.generate_email = fail

    with pytest.raises(RuntimeError, match="Internal failure"):
        await gen.generate_email()
