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


def test_generate_bulk_emails_returns_list():
    gen = EmailGenerator()
    fake_emails = ["a@example.com", "b@example.com", "c@example.com"]

    gen._async.generate_bulk_emails = AsyncMock(return_value=fake_emails)

    result = gen.generate_bulk_emails("200")

    assert isinstance(result, list)
    assert all(isinstance(e, str) for e in result)
    assert result == fake_emails
    gen._async.generate_bulk_emails.assert_awaited_once_with("200")


def test_generate_bulk_emails_default_value():
    gen = EmailGenerator()
    gen._async.generate_bulk_emails = AsyncMock(return_value=["x@example.com"])

    result = gen.generate_bulk_emails()

    assert result == ["x@example.com"]
    gen._async.generate_bulk_emails.assert_awaited_once_with("100")


def test_generate_bulk_emails_raises_runtime_error():
    gen = EmailGenerator()

    gen._async.generate_bulk_emails = AsyncMock(return_value=fake_emails)  # type: ignore[attr-defined]

    with pytest.raises(RuntimeError, match="Failed to generate emails"):
        gen.generate_bulk_emails("300")
