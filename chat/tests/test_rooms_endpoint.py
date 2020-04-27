import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chat.models import ChatUser, Room

"""
    TODO: add test cases description
"""

USERNAME = "user_name_"
USERNAME_FIRST = USERNAME + "1"
USERNAME_SECOND = USERNAME + "2"

EMAIL = "email1@email.com"
EMAIL_FIRST = EMAIL + "1"
EMAIL_SECOND = EMAIL + "2"

PASSWORD = "ez3}yh^L4%27Dnn]"

ROOMNAME = "room_name_"
ROOMNAME_FIRST = ROOMNAME + "1"
ROOMNAME_SECOND = ROOMNAME + "2"

DATA_USER_FIRST = {
    "username": USERNAME_FIRST,
    "email": EMAIL_FIRST,
    "password1": PASSWORD,
    "password2": PASSWORD
}
DATA_USER_SECOND = {
    "username": USERNAME_SECOND,
    "email": EMAIL_SECOND,
    "password1": PASSWORD,
    "password2": PASSWORD
}
DATA_ROOM_FIRST = {
    "title": ROOMNAME_FIRST,
}
DATA_ROOM_SECOND = {
    "title": ROOMNAME_SECOND,
}

URL_DETAILS = "room_details"
URL_LIST = "list_rooms"
URL_REGISTER = "rest_register"


class RoomCreationTest(APITestCase):
    def setUp(self):
        url_reg = reverse(URL_REGISTER)

        response = self.client.post(url_reg, data=DATA_USER_FIRST, format="json")
        self.auth_token = response.data["key"]

    def test_room_creation_authenticated(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_room_creation_unauthenticated(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)


class RoomsTest(APITestCase):
    def setUp(self):
        url = reverse(URL_LIST)
        url_reg = reverse(URL_REGISTER)

        # Registration of the first user
        reg_response_first = self.client.post(url_reg, data=DATA_USER_FIRST, format="json")
        self.auth_token_first = reg_response_first.data["key"]

        # Registration of the second user
        reg_response_second = self.client.post(url_reg, data=DATA_USER_SECOND, format="json")
        self.auth_token_second = reg_response_second.data["key"]

        # Authorization of the first user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token_first)

        # Creation of the room by the first user
        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_room_list(self):
        """
            GET: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)

    def test_get_room_info(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        url_info = reverse(URL_DETAILS, args=[1])

        get_response = self.client.get(url_info)
        keys = ["title", "creator"]
        self.assertTrue(all([key in get_response.data.keys() for key in keys]))

        data = get_response.data
        self.assertEqual(data["title"], ROOMNAME_FIRST)
        self.assertEqual(data["creator"], 1)

    def test_update_room_info_by_creator(self):
        """
            PATCH: '/pidor/rooms/{id}/'
        """
        updated_title = "updated_title"

        url_info = reverse(URL_DETAILS, args=[1])

        patch_response = self.client.patch(
            path=url_info,
            data={"title": updated_title}
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.data["title"], updated_title)

    '''
        TODO: add test update room info by other user
    '''

    def test_delete_room_info_by_creator(self):
        """
            DELETE: '/pidor/rooms/{id}/'
        """

        url_info = reverse(URL_DETAILS, args=[1])

        delete_response = self.client.delete(url_info)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(url_info)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    '''
        TODO: add test delete room info by other user
    '''