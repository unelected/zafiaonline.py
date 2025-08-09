# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.

import unittest

from zafiaonline import Client
from zafiaonline.structures.packet_data_keys import PacketDataKeys


class TestClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = Client()
        self.user_id = "user_57e6cce718056"
        self.nickname = "wow1one"

    async def test_get_user(self):
        await self.client.create_connection()
        get_user = await self.client.get_user(self.user_id)
        self.assertIn(self.user_id, get_user[PacketDataKeys.USER][
            PacketDataKeys.OBJECT_ID])
        await self.client.disconnect()

if __name__ == "__main__":
    unittest.main()
