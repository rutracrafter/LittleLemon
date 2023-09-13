from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, DjangoModelPermissions
from django.contrib.auth.models import Group
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
    group_name = request.data.get("group")
    user = models.User.objects.get(username=user_name)
    target_group = Group.objects.get(name=group_name)
    user.groups.add(target_group)
    return Response(f"Assigned user {user_name} to group {group_name}", status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
def SingleManagerView(request, pk):
  user_groups = list(request.user.groups.all())
  if not request.user.groups.filter(name='Manager').exists():
    return Response("User does not have permission.", status=status.HTTP_401_UNAUTHORIZED)
  if request.method == "DELETE":
    user = models.User.objects.get(id=pk)
    if user:
      group = Group.objects.get(name="Manager")
      user.groups.remove(group)
      return Response(f"User {user} has been removed from the Manager group.", status=status.HTTP_200_OK)
    return Response(f"User {user} was not found.", status=status.HTTP_404_NOT_FOUND)
  else:
    return Response("That HTTP method is not allowed.", status=status.HTTP_405_METHOD_NOT_ALLOWED)


# REPLICATE ABOVE CODE FOR DELIVERY CREW