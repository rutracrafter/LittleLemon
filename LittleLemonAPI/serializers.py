from rest_framework import serializers
from . import models

class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.MenuItem
    fields = ['title', 'price', 'featured', 'category']
