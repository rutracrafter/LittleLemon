from rest_framework import serializers
from . import models

class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.MenuItem
    fields = ['title', 'price', 'featured', 'category']

class ManagerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.User
    fields = ['username', 'first_name', 'password']

class DeliveryCrewSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.User
    fields = ['username', 'first_name', 'password']

class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Cart
    fields = ['quantity', 'unit_price', 'price', 'menuitem_id', 'user_id']