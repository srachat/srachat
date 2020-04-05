from django.urls import path, include

from chat.views import chatusers, comments, rooms

urlpatterns = [
    # Chat endpoints

    # Room endpoints
    path('rooms/', rooms.RoomList.as_view()),
    path('rooms/<int:pk>/', rooms.RoomDetail.as_view()),

    # Comment endpoints
    path('rooms/<int:pk>/comments/', comments.CommentList.as_view()),
    path('comments/<int:pk>/', comments.CommentDetail.as_view()),

    # User endpoints
    path('rooms/<int:pk>/users/', chatusers.RoomUserList.as_view()),
    path('users/', chatusers.ChatUserList.as_view()),
    path('users/<int:pk>/', chatusers.ChatUserDetail.as_view()),


    # Rest auth endpoints
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]
