from django.shortcuts import render
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
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
  queryset = models.MenuItem.objects.all()
  serializer_class = serializers.MenuItemSerializer