# urls.py
from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('write/', views.board_write, name='board_write'),
    path('detail/<int:pk>/', views.board_detail, name='board_detail'),
    path('detail/<int:pk>/delete/', views.board_delete, name='board_delete'),
    path('detail/<int:pk>/modify/', views.board_modify, name='board_modify'),
    path('detail/<int:pk>/comment_delete/', views.comment_delete, name='comment_delete'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('reply_delete/<int:pk>/', views.reply_delete, name='reply_delete'),
    path('board/like/<int:pk>/', views.like_board, name='like_board'),
]
