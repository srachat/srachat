from django.urls import path, include

from chat.views import chatusers, comments, rooms

urlpatterns = [
    # Chat endpoints

    # Room endpoints
    path('rooms/', rooms.RoomList.as_view(), name="list_rooms"),
    path('rooms/<int:pk>/', rooms.RoomDetail.as_view(), name="room_details"),

    # Comment endpoints
    path('rooms/<int:pk>/comments/', comments.CommentList.as_view(), name="room_comments"),
    path('comments/<int:pk>/', comments.CommentDetail.as_view(), name="comment_details"),

    # User endpoints
    path('rooms/<int:pk>/users/', chatusers.RoomUserList.as_view(), name="list_room_users"),
    path('users/', chatusers.ChatUserList.as_view(), name="list_users"),
    path('users/<int:pk>/', chatusers.ChatUserDetail.as_view(), name="user_details"),


    # Rest auth endpoints
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]
