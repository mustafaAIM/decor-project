import jwt 
# django
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
# channels
from channels.db import database_sync_to_async
# url
from urllib.parse import parse_qs
# models
from authentication.models.user_model import User

class JWTAuthMiddleware:
    """
    Middleware to extract JWT token from the WebSocket connection and authenticate the user.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract the token from the query string
        query_string = scope['query_string'].decode()
        token = self.get_token_from_query(query_string)

        if token:
            user = await self.get_user_from_token(token)
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser ()

        return await self.inner(scope, receive, send)

    def get_token_from_query(self, query_string):
        """
        Extract the token from the query string.
        """
        params = parse_qs(query_string)
        return params.get('token', [None])[0]

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Decode the token and return the user.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])  # Adjust based on your payload structure
            return user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return AnonymousUser ()