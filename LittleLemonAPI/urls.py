from django.urls import path, include
from . import views
# from rest_framework.authtoken.views  import obtain_auth_token

urlpatterns = [
  path('test/', views.test),
  path('menu-items/', views.MenuItemView.as_view()),
  path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
  path('', include('djoser.urls')),
  path('', include('djoser.urls.authtoken')),
]