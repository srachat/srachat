import json

from channels.testing import HttpCommunicator
from django.urls import reverse

from root.asgi import application
from srachat.tests.utils import SrachatTestCase, UrlUtils


class TestRoomWebsockets(SrachatTestCase):
    async def test_connect(self):
        communicator = HttpCommunicator(
            application, "POST", reverse(UrlUtils.Users.REGISTER),
            body=json.dumps({"username": "username"}).encode("utf-8")
        )
        response = await communicator.get_response()
        print(response)
        self.assertEqual(response["status"], 200)
