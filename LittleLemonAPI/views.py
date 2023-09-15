from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, DjangoModelPermissions
from django.contrib.auth.models import Group
from django.core.serializers import serialize
from datetime import datetime
from django.forms.models import model_to_dict
from django.http import QueryDict
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
import json
from . import models
from . import serializers

# Create your views here.
def test(request):
  return HttpResponse('test successful')

class MenuItemView(generics.ListCreateAPIView):
  throttle_classes = [AnonRateThrottle, UserRateThrottle]
  permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
  queryset = models.MenuItem.objects.all()
  serializer_class = serializers.MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
  throttle_classes = [AnonRateThrottle, UserRateThrottle]
  permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
  queryset = models.MenuItem.objects.all()
  serializer_class = serializers.MenuItemSerializer

class ManagerView(generics.ListCreateAPIView):
  throttle_classes = [AnonRateThrottle, UserRateThrottle]
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
@throttle_classes([AnonRateThrottle, UserRateThrottle])
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
  throttle_classes = [AnonRateThrottle, UserRateThrottle]
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
@throttle_classes([AnonRateThrottle, UserRateThrottle])
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
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def CartView(request):
  if request.method == 'GET':
    user = request.user
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
    user = request.user
    queryset = models.Cart.objects.filter(user=user)
    for item in queryset:
      item.delete()
    return Response("Current user's menu items deleted!", status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def OrderView(request):
  if request.method == 'GET':
    user = request.user
    queryset = None
    if request.user.groups.filter(name='Manager').exists():
      queryset = models.Order.objects.all()
    elif request.user.groups.filter(name='Delivery Crew'):
      queryset = models.Order.objects.filter(delivery_crew=request.user)
    else:
      queryset = models.Order.objects.filter(user=user)
    serialized_data = serialize("json", queryset)
    serialized_data = json.loads(serialized_data)
    return Response(serialized_data, status=status.HTTP_200_OK)


  elif request.method == 'POST':
    user = request.user
    order = models.Order(user=user, delivery_crew=None, status=False, total='0', date=datetime.now())
    order.save()
    order_id = order.id
    order = models.Order.objects.get(id=order_id)
    queryset = models.Cart.objects.filter(user=user)
    for item in queryset:
      menuitem = item.menuitem
      quantity = item.quantity
      unit_price = item.unit_price
      price = item.price
      order_item = models.OrderItem(order=order, menuitem=menuitem, quantity=quantity, unit_price=unit_price, price=price)
      order_item.save()
      item.delete()
    return Response("User orders placed, and user cart empited.", status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def SingleOrderView(request, pk):
  if request.method == 'GET':
    user = request.user
    queryset = None
    try:
      queryset = models.Order.objects.get(id=pk)
    except:
      return Response("Order does not exist.", status=status.HTTP_404_NOT_FOUND)
    if queryset.user.id != user.id:
      return Response("User does not have access to this order.", status=status.HTTP_403_FORBIDDEN)
    return Response(model_to_dict(queryset), status=status.HTTP_200_OK)

  elif request.method == 'PUT':
    if not request.user.groups.filter(name='Manager').exists():
      return Response("User does not have access to edit this order.", status=status.HTTP_403_FORBIDDEN)
    data = QueryDict(request.body)
    username = data.get('username')
    user = models.User.objects.get(username=username)
    username = data.get('delivery_crew')
    delivery_crew = models.User.objects.get(username=username)
    order_status = data.get('status')
    total = data.get('total')
    date = data.get('date')
    queryset = None
    try:
      queryset = models.Order.objects.get(id=pk)
    except:
      return Response("Order does not exist.", status=status.HTTP_404_NOT_FOUND)
    queryset.user = user
    queryset.delivery_crew = delivery_crew
    queryset.status = order_status
    queryset.total = total
    queryset.date = date
    queryset.save()
    return Response("Order updated successfully.", status=status.HTTP_200_OK)

  elif request.method == 'PATCH':
    if request.user.groups.filter(name='Delivery Crew').exists():
      data = QueryDict(request.body)
      order_status = data.get('status')
      queryset = None
      try:
        queryset = models.Order.objects.get(id=pk)
      except:
        return Response("Order does not exist.", status=status.HTTP_404_NOT_FOUND)
      queryset.status = order_status
      queryset.save()
      return Response("Order updated successfully.", status=status.HTTP_200_OK)

    elif request.user.groups.filter(name='Manager').exists():
      data = QueryDict(request.body)
      username = data.get('delivery_crew')
      delivery_crew = models.User.objects.get(username=username)
      order_status = data.get('status')
      queryset = None
      try:
        queryset = models.Order.objects.get(id=pk)
      except:
        return Response("Order does not exist.", status=status.HTTP_404_NOT_FOUND)
      queryset.delivery_crew = delivery_crew
      queryset.status = order_status
      queryset.save()
      return Response("Order updated successfully.", status=status.HTTP_200_OK)

    else:
      return Response("User does not have access to edit this order.", status=status.HTTP_403_FORBIDDEN)

  elif request.method == 'DELETE':
    if not request.user.groups.filter(name='Manager').exists():
      return Response("User does not have access to edit this order.", status=status.HTTP_403_FORBIDDEN)
    queryset = None
    try:
      queryset = models.Order.objects.get(id=pk)
    except:
      return Response("Order does not exist.", status=status.HTTP_404_NOT_FOUND)
    queryset.delete()
    return Response("Order successfully deleted.", status=status.HTTP_200_OK)