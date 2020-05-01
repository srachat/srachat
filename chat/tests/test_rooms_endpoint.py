from django.urls import reverse
from rest_framework import status

from chat.models import Room
from chat.tests.utils import UserUtils, RoomUtils, UrlUtils, SrachatTestCase

"""
    RoomCreationTest - POST: '/pidor/rooms/' - test of creation room by authenticated/unauthenticated user
    RoomTest - GET: '/pidor/rooms/' - test of getting room list
    RoomTest - PATCH, PUT, DELETE: '/pidor/rooms/' - testing only safe methods allowed     
    RoomTest - GET: '/pidor/rooms/{id}' - test of getting correct room info
    RoomTest - PATCH: '/pidor/rooms/{id}/' test of update room info by creator room/ other user
    RoomTest - DELETE: '/pidor/rooms/{id}/' test of delete room info by creator room/ other user
    
"""


class RoomCreationTest(SrachatTestCase):
    def setUp(self):
        self.auth_token = self.register_user_return_token(UserUtils.DATA_FIRST)

    def test_room_creation_authenticated(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(UrlUtils.Rooms.LIST)

        self.set_credentials(self.auth_token)
        post_response = self.client.post(url, data=RoomUtils.DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_room_creation_unauthenticated(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(UrlUtils.Rooms.LIST)

        post_response = self.client.post(url, data=RoomUtils.DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)


class RoomsTest(SrachatTestCase):
    def setUp(self):
        url = reverse(UrlUtils.Rooms.LIST)

        # Registration of the first user
        self.auth_token_first = self.register_user_return_token(UserUtils.DATA_FIRST)

        # Registration of the second user
        self.auth_token_second = self.register_user_return_token(UserUtils.DATA_SECOND)

        # Authorization of the first user
        self.set_credentials(self.auth_token_first)

        # Creation of the room by the first user
        post_response = self.client.post(url, data=RoomUtils.DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_room_list(self):
        """
            GET: '/pidor/rooms/'
        """

        url = reverse(UrlUtils.Rooms.LIST)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)

        self.set_credentials(self.auth_token_second)

        post_response = self.client.post(url, data=RoomUtils.DATA_ROOM_SECOND, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_only_safe_methods_allowed(self):
        """
             DELETE, PATCH, PUT: '/pidor/rooms/
        """

        url = reverse(UrlUtils.Rooms.LIST)

        self.check_safe_methods(url)

    def test_get_room_info(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        get_response = self.client.get(url_info)
        keys = ["title", "creator"]
        self.assertTrue(all([key in get_response.data.keys() for key in keys]))

        data = get_response.data
        self.assertEqual(data["title"], RoomUtils.ROOM_NAME_FIRST)
        self.assertEqual(data["creator"], 1)

    def test_post_room_info(self):
        """
            POST: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        post_response = self.client.post(url_info)
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_room_info_by_creator(self):
        """
            PATCH: '/pidor/rooms/{id}/'
        """
        updated_title = "updated_title"

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        patch_response = self.client.patch(
            path=url_info,
            data={"title": updated_title}
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.data["title"], updated_title)

    def test_update_room_info_by_other_user(self):
        """
            PATCH: '/pidor/rooms/{id}/'
        """
        updated_title = "updated_title"

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        self.set_credentials(self.auth_token_second)

        patch_response = self.client.patch(
            path=url_info,
            data={"title": updated_title}
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.data["title"], RoomUtils.ROOM_NAME_FIRST)

    def test_delete_room_info_by_creator(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        delete_response = self.client.delete(url_info)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_room_info_by_other_user(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """

        url_info = reverse(UrlUtils.Rooms.DETAILS, args=[1])

        self.set_credentials(self.auth_token_second)

        delete_response = self.client.delete(url_info)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

        get_response = self.client.get(url_info)
        keys = ["title", "creator"]
        self.assertTrue(all([key in get_response.data.keys() for key in keys]))

        data = get_response.data
        self.assertEqual(data["title"], RoomUtils.ROOM_NAME_FIRST)
        self.assertEqual(data["creator"], 1)
