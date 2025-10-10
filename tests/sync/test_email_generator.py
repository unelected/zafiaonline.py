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
from emailnator.sync.email_generator import EmailGenerator


@pytest.mark.asyncio
async def test_generate_email_returns_string():
    gen = EmailGenerator()
    fake_email = "test@example.com"

    gen._async.generate_email = AsyncMock(return_value=fake_email)

    result = gen.generate_email()

    assert isinstance(result, str)
    assert result == fake_email
    gen._async.generate_email.assert_awaited_once()

def test_generate_email_raises_runtime_error():
    gen = EmailGenerator()

    async def fake_fail():
        raise RuntimeError("Generation failed")

    gen._async.generate_email = fake_fail

    with pytest.raises(RuntimeError, match="Generation failed"):
        gen.generate_email()
