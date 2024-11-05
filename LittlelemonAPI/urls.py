from django.urls import path, include
from . import views

urlpatterns = [
    #path('users/', views.CreateNewUser.as_view()),
    #path('users/me/', views.ShowUser.as_view()),
    path('menu-items/', views.MenuItem.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users/', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.RemoveManagersView.as_view()),
    path('groups/delivery-crew/users/', views.DelivertCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.RemoveDeliveryCrewView.as_view()),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    #path('token/login/', views.UserLoginView.as_view()),
]