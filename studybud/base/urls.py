from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('user-register/', views.registerView, name="user-register"),
    path('user-login/', views.loginView, name="user-login"),
    path('user-logout/', views.logoutView, name="user-logout"),
    path('room/<str:pk>/', views.room, name="room"),
    path('user-profile/<str:pk>/', views.userPorfile, name="user-profile"),
    path('update-user/<str:pk>', views.updateUser, name="update-user"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.upateRoom, name="update-room"),
    path('delete-room/<str:pk>', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>', views.delete_user_message, name="delete-message"),
    path('topics', views.topicsView, name="topics"),
    path('recent-activity', views.recentActivityView, name="recent-activity"),
]