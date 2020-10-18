from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.language import LanguageChoices


class LanguageList(APIView):
    def get(self, request, format=None):
        languages_dict = {
            short: long for short, long in LanguageChoices.choices
        }
        return Response(languages_dict)
