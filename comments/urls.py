from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:pk>/', views.comment_create, name='comment_create'),

    path('test_form/', views.test_comment_form, name='test_comment_form'),
]
