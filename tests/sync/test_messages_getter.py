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


def test_get_messages_returns_list_of_dicts():
    gen = EmailGenerator()
    fake_messages = [
        {
            "messageID": "123ABC",
            "from": "AI TOOLS",
            "subject": "New AI tools update",
            "time": "Just Now",
        }
    ]

    gen._async.get_messages = AsyncMock(return_value=fake_messages)

    result = gen.get_messages("test@example.com")

    assert isinstance(result, list)
    assert all(isinstance(m, dict) for m in result)
    assert result == fake_messages

    gen._async.get_messages.assert_awaited_once_with("test@example.com")

def test_get_messages_raises_runtime_error():
    gen = EmailGenerator()

    async def fake_fail(email):
        raise RuntimeError(f"Failed to fetch messages email: {email}")

    gen._async.get_messages = fake_fail

    with pytest.raises(RuntimeError, match="Failed to fetch messages"):
        gen.get_messages("test@example.com")
