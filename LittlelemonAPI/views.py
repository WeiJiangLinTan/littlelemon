from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from . import serializers
from . import models
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsManager, IsDeliveryCrew
from django.shortcuts import get_object_or_404
import math
from datetime import date

# Create your views here.
class CreateNewUser(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    

class ShowUser(generics.ListAPIView):
    def get(self, request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)
  

"""class UserLoginView(APIView):
    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)
    def get(self, request):
        user = User.objects.get(username=request.user)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)"""

        
"""class UserLoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)"""
        
class MenuItem(generics.ListCreateAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        return [permission() for permission in permission_classes]
    """def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        elif (self.request.user.groups.filter(name="Manager")):
            return []

        return [IsAdminUser()]"""
    
class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        return [permission() for permission in permission_classes]
    
class ManagersView(generics.ListCreateAPIView):
    queryset = models.User.objects.filter(groups__name='Manager')
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminUser | IsManager]
    
    def post(self, request):
        username = request.data['username']

        if username:
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name="Manager")
            manager.user_set.add(user)
            return Response({'message':'User added to Managers'}, status.HTTP_201_CREATED)
        
        
class RemoveManagersView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminUser | IsManager]
    queryset = models.User.objects.filter(groups__name='Manager')
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        manager = Group.objects.get(name='Manager')
        manager.user_set.remove(user)
        return Response({'message':'User remove from Managers'}, status.HTTP_200_OK)
    
      
class DelivertCrewView(generics.ListCreateAPIView):
    queryset = models.User.objects.filter(groups__name='Delivery crew')
    serializer_class = serializers.UserSerializer
    permissions_class = [IsAdminUser | IsManager]
    
    def post(self, request):
        username = request.data['username']
        
        if username:
            user = get_object_or_404(User, username=username)
            deliveryCrew = Group.objects.get(name="Delivery crew")
            deliveryCrew.user_set.add(user)
            return Response({'message':'User add to delivery crew'}, status.HTTP_201_CREATED)
        

    
class RemoveDeliveryCrewView(generics.RetrieveDestroyAPIView):
    queryset = models.User.objects.filter(groups__name='Delivery crew')
    serializer_class = serializers.UserSerializer
    permissions_class = [IsAdminUser | IsManager]
    
    def delete(self,request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        deliveryCrew = Group.objects.get(name='Delivery crew')
        deliveryCrew.user_set.remove(user)
        return Response({'message':'User remove from delivery crew'}, status.HTTP_200_OK)
    
class CartView(generics.ListCreateAPIView,generics.RetrieveDestroyAPIView):
    serializer_class = serializers.CartSerializer
    
    def get_queryset(self):
        return models.Cart.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        serialized_item = serializers.CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(models.MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            models.Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return Response({'message':'Item already in cart'}, status.HTTP_409_CONFLICT)
        return Response({'message':'Item added to cart!'}, status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        if not request.data:
            models.Cart.objects.filter(user=request.user).delete()
            return Response({'message':'All Items removed from cart'}, status.HTTP_200_OK)
        if request.data['menuitem']:
           serialized_item = serializers.CartRemoveSerializer(data=request.data)
           serialized_item.is_valid(raise_exception=True)
           menuitem = request.data['menuitem']
           cart = get_object_or_404(models.Cart, user=request.user, menuitem=menuitem )
           cart.delete()
           return Response({'message':'Item removed from cart'}, status.HTTP_200_OK)

class OrderView(generics.ListCreateAPIView):
    serializer_class = serializers.OrderSerializer
    
    def get_queryset(self):
        user= self.request.user
        if user.is_superuser or user.groups.filter(name="Manager").exists():
            return models.Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return models.Order.objects.filter(delivery_crew = user)
        else:
            return models.Order.objects.filter(user=user)
        
    def get_permissions(self):
        if self.request.method == "GET" or "POST":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def post(self, request, *args, **kwargs):
        cart = models.Cart.objects.filter(user=request.user)
        value_list=cart.values_list()
        if len(value_list) == 0:
            return Response({'message':'nothing on the cart'})
        total = math.fsum([float(value[-1]) for value in value_list])
        order = models.Order.objects.create(user=request.user, status=False, total=total,date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(models.MenuItem, id=i['menuitem_id'])
            unit_price = i['unit_price']
            price = unit_price * i['quantity']
            orderitem = models.OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'],unit_price=unit_price, price=price)
            orderitem.save()
        cart.delete()
        return Response({'message':f'Your order has been placed. Your id is {str(order.id)}'}, status.HTTP_201_CREATED)
    
class SingleOrderView(generics.RetrieveUpdateAPIView):
    serializer_class=serializers.SingleSerializer
    
    def get_permissions(self):
        user= self.request.user
        method = self.request.method
        order = models.Order.objects.get(pk=self.kwargs['pk'])
        if user == order.user and method == "GET":
            permission_classes = [IsAuthenticated]
        elif method == 'PUT' or method == 'DELETE':
            permission_classes = [IsManager | IsAdminUser]
        else:
            permission_classes = [IsDeliveryCrew | IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_quertset(self, *args, **kwargs):
        query = models.OrderItem.objects.filter(order_id=self.kwargs['pk'])
        return query
    
    def patch(self, request, *args, **kwargs):
        order = models.Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response({'message':'Status of order #' + str(order.id) + ' change to '+str(order.status)}, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        serialized_item = serializers.OrderInsertSerializer(date=request.date)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.date['delivery_crew']
        order = get_object_or_404(models.Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return Response({'message':str(crew.username)+' was assigned to order #'+str(order.id)}, status.HTTP_201_CREATED) 
    
    def delete(self, request, *args, **kwargs):
        order = models.Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return Response({'message':f'Order #{order_number} was deleted'}, status.HTTP_200_OK)