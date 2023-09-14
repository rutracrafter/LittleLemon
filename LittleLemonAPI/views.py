from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, DjangoModelPermissions
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.core.serializers import serialize
import json
from . import models
from . import serializers

# Create your views here.
def test(request):
  return HttpResponse('test successful')

class MenuItemView(generics.ListCreateAPIView):
  permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
  queryset = models.MenuItem.objects.all()
  serializer_class = serializers.MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
  queryset = models.MenuItem.objects.all()
  serializer_class = serializers.MenuItemSerializer

class ManagerView(generics.ListCreateAPIView):
  permission_classes = [DjangoModelPermissions]
  queryset = models.User.objects.filter(groups__id='1') # 1 is manager group, 2 is delivery crew group
  serializer_class = serializers.ManagerSerializer

  def post(self, request, *args, **kwargs):
    user_name = request.data.get("username")
    user = models.User.objects.get(username=user_name)
    target_group = Group.objects.get(name="Manager")
    user.groups.add(target_group)
    return Response(f"Assigned user {user_name} to group Manager", status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
def SingleManagerView(request, pk):
  if request.method == "DELETE":
    if not request.user.groups.filter(name='Manager').exists():
      return Response("User does not have permission.", status=status.HTTP_401_UNAUTHORIZED)
    if len(list(models.User.objects.filter(id=pk))) == 0:
      return Response(f"User was not found.", status=status.HTTP_404_NOT_FOUND)
    user = models.User.objects.get(id=pk)
    group = Group.objects.get(name="Manager")
    user.groups.remove(group)
    return Response(f"User {user} has been removed from the Manager group.", status=status.HTTP_200_OK)
  else:
    return Response("That HTTP method is not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)


# REPLICATE ABOVE CODE FOR DELIVERY CREW
class DeliveryCrewView(generics.ListCreateAPIView):
  permission_classes = [DjangoModelPermissions]
  queryset = models.User.objects.filter(groups__id='2') # 1 is manager group, 2 is delivery crew group
  serializer_class = serializers.DeliveryCrewSerializer

  def post(self, request, *args, **kwargs):
    user_name = request.data.get("username")
    user = models.User.objects.get(username=user_name)
    target_group = Group.objects.get(name="Delivery Crew")
    user.groups.add(target_group)
    return Response(f"Assigned user {user_name} to group Delivery Crew", status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
def SingleDeliveryCrewView(request, pk):
  if request.method == "DELETE":
    if not request.user.groups.filter(name='Manager').exists():
      return Response("User does not have permission.", status=status.HTTP_401_UNAUTHORIZED)
    if len(list(models.User.objects.filter(id=pk))) == 0:
      return Response(f"User was not found.", status=status.HTTP_404_NOT_FOUND)
    user = models.User.objects.get(id=pk)
    group = Group.objects.get(name="Delivery Crew")
    user.groups.remove(group)
    return Response(f"User {user} has been removed from the Delivery Crew group.", status=status.HTTP_200_OK)
  else:
    return Response("That HTTP method is not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(["GET", "POST", "DELETE"])
def CartView(request):
  if request.method == 'GET':
    user = Token.objects.get(key=request.auth.key).user
    queryset = models.Cart.objects.filter(user=user)
    serialized_data = serialize("json", queryset)
    serialized_data = json.loads(serialized_data)
    return Response(serialized_data, status=status.HTTP_200_OK)

  elif request.method == 'POST':
    data = request.POST
    title = data.get('title')
    menu_item = models.MenuItem.objects.get(title=title)
    menu_item_id = menu_item.id
    user = request.user
    user_id = user.id
    quantity = data.get('quantity')
    menu_item_price = menu_item.price
    price = float(menu_item.price) * float(data.get('quantity'))
    cart = models.Cart(quantity=quantity, unit_price=menu_item_price, price=price, menuitem_id=menu_item_id, user_id=user_id)
    cart.save()
    return Response("Menu item added to cart!", status=status.HTTP_201_CREATED)

  elif request.method == 'DELETE':
    user = Token.objects.get(key=request.auth.key).user
    queryset = models.Cart.objects.filter(user=user)
    for item in queryset:
      item.delete()
    return Response("Current user's menu items deleted!", status=status.HTTP_200_OK)