from django.urls import path, include

from .views import chatusers, comments, languages, rooms, tags

urlpatterns = [
    # Srachat endpoints

    # Room endpoints
    path('rooms/', rooms.RoomList.as_view(), name="list_rooms"),
    path('rooms/<int:pk>/', rooms.RoomDetail.as_view(), name="room_details"),
    path('rooms/<int:pk>/vote/', rooms.RoomVoteTeam.as_view(), name="vote_team"),
    path('rooms/<int:pk>/deactivate/', rooms.RoomDeactivate.as_view(), name="deactivate_room"),

    # Comment endpoints
    path('rooms/<int:pk>/comments/', comments.CommentList.as_view(), name="room_comments"),
    path('comments/<int:pk>/', comments.CommentDetail.as_view(), name="comment_details"),

    # User endpoints
    path('rooms/<int:pk>/users/', chatusers.RoomUserList.as_view(), name="list_room_users"),
    path('rooms/<int:pk>/users/ban/', chatusers.RoomBanUser.as_view(), name="ban_user"),
    path('users/', chatusers.ChatUserList.as_view(), name="list_users"),
    path('users/<int:pk>/', chatusers.ChatUserDetail.as_view(), name="user_details"),

    # Tag endpoints
    path('tags/', tags.TagList.as_view(), name="list_tags"),

    # Language endpoints
    path('languages/', languages.LanguageList.as_view(), name="list_languages"),


    # Rest auth endpoints
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]
