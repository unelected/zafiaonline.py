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
        get_user = await self.client.get_user(self.user_id) # ⚠️ temporary unwork
        self.assertIn(self.user_id, get_user[PacketDataKeys.USER][
            PacketDataKeys.OBJECT_ID])

if __name__ == "__main__":
    unittest.main()