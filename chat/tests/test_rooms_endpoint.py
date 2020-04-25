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
EMAIL_THIRD = EMAIL + "3"

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

URL_LIST = "list_rooms"
URL_REGISTER = "rest_register"
URL_DETAILS = "room_details"


class RoomsTest(APITestCase):
    def setUp(self):
        url = reverse(URL_REGISTER)

        response = self.client.post(url, data=DATA_USER_FIRST, format="json")
        self.auth_token = response.data["key"]

    def test_room_creation(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_room_creation_without_authenticated(self):
        """
            POST: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_room_list(self):
        """
            GET: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)

    def test_room_list_without_authenticated(self):
        """
            GET: '/pidor/rooms/'
        """

        url = reverse(URL_LIST)

        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 0)

    def test_get_room_info(self):
        """
            GET: '/pidor/rooms/{id}/'
        """

        url = reverse(URL_LIST)
        url_info = reverse(URL_DETAILS, args=[1])

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.auth_token)
        post_response = self.client.post(url, data=DATA_ROOM_FIRST, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        get_response = self.client.get(url_info)
        keys = ["title", "creator"]
        self.assertTrue(all([key in get_response.data.keys() for key in keys]))

        data = get_response.data
        self.assertEqual(data["title"], ROOMNAME_FIRST)
        self.assertEqual(data["creator"], 1)
