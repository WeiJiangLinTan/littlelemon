from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email = validated_data['email'])
        
        return user
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        
class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()
    class Meta:
        model = models.Cart
        fields = ['menuitem', 'quantity', 'price']
        
class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Cart
        fields = ['menuitem']
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']
        
class SingleSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()
    class Meta():
        model = models.Order
        fields = ['menuitem','quantity']
        
class OrderInsertSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Order
        fields = ['delivery_crew']