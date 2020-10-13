from django.urls import reverse
from rest_framework import status

from ..tests.utils import SrachatTestCase

"""
    TagsTest - GET: '/pidor/tags/' - test of fetching all existing tags 
"""


class TagsTest(SrachatTestCase):
    def test_all_tags_fetching(self):
        """
            GET: '/pidor/tags/'
        """
        url = reverse("list_tags")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIn("name", response.data[0].keys())
