from django.urls import path, include
from . import views
# from rest_framework.authtoken.views  import obtain_auth_token

urlpatterns = [
  path('test/', views.test),
  path('menu-items/', views.MenuItemView.as_view()),
  path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
  path('groups/manager/users/', views.ManagerView.as_view()),
  path('groups/manager/users/<int:pk>', views.SingleManagerView),
  path('groups/delivery-crew/users/', views.DeliveryCrewView.as_view()),
  path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewView),
  path('cart/menu-items/', views.CartView),
  path('', include('djoser.urls')),
  path('', include('djoser.urls.authtoken')),
]