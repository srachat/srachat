from django.urls import path, include

from chat.views import comments, rooms

urlpatterns = [
    path('rooms/', rooms.RoomList.as_view()),
    path('rooms/<int:pk>/', rooms.RoomDetail.as_view()),
    path('rooms/<int:pk>/comments/', comments.CommentList.as_view()),
    path('rooms/<int:room_pk>/comments/<int:comment_pk>/', comments.CommentDetail.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]
