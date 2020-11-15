import logging
from typing import Awaitable, Optional, Union

from channels.db import database_sync_to_async
from channels.sessions import CookieMiddleware, SessionMiddleware
from django.contrib.auth.models import AnonymousUser, User
from django.db import close_old_connections
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(token_key: Optional[str]) -> Union[Awaitable[User], AnonymousUser]:
    if token_key:
        try:
            token = Token.objects.get(key=token_key)
            close_old_connections()
            return token.user
        except Token.DoesNotExist:
            logging.error(f"Someone is trying to use a non-existing token: {token_key}")
    return AnonymousUser()


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 3
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        cookies = scope.get('cookies', {})
        token_key = cookies.get("token", None)
        scope["user"] = await get_user(token_key)
        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))
