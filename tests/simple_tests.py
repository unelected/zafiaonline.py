# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import os

from dotenv import load_dotenv
from zafiaonline import Client
from zafiaonline.structures.packet_data_keys import PacketDataKeys


class TestClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        load_dotenv()
        self.client = Client()
        self.player_user_id = "user_57e6cce718056"
        self.nickname = os.getenv("NICKNAME") or "email"
        self.password = os.getenv("PASSWORD") or "password"

    async def test_get_user(self):
        await self.client.auth.sign_in(self.nickname, self.password)
        user_data: dict | None = await self.client.players.get_user(self.player_user_id)
        if user_data is None:
            raise ValueError
        profile: dict | None = user_data.get(PacketDataKeys.USER_PROFILE)
        if profile is None:
            raise ValueError
        profile_data = profile.get(PacketDataKeys.PROFILE_USER_DATA)
        self.assertIn(self.player_user_id, profile_data.get(PacketDataKeys.OBJECT_ID))

    async def test_sign_in(self):
        data = await self.client.auth.sign_in(self.nickname, self.password)
        self.assertIn(self.client.auth.user.user_id, data.user_id)

if __name__ == "__main__":
    unittest.main()

