from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemViewSet.as_view({
            'get':'list',
            'post': 'create',
        })),
    path('menu-items/<int:pk>', views.MenuItemViewSet.as_view({
            'get':'retrieve',
            'put':'update',
            'patch':'partial_update',
            'delete':'destroy',
        })),
    path('groups/manager/users', views.ManagerGroupViewset.as_view(
            {
            'get':'list',
            'post': 'create',
            }
        )),
    path('groups/manager/users/<int:pk>', views.ManagerGroupViewset.as_view(
            {
            'get':'retrieve',
            'delete':'destroy',
            }
        )),
    path('groups/delivery-crew/users', views.DeliveryCrewViewset.as_view(
            {
            'get':'list',
            'post': 'create',
            }
        )),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewViewset.as_view(
        {
            'get':'retrieve',
            'delete': 'destroy',
        }
    )),
    path('cart/menu-items', views.CartViewset.as_view(
        {
            'get': 'list',
            'post': 'create',
            'delete': 'destroy',
        }
    )),
    path('cart/menu-items/<int:pk>', views.CartViewset.as_view(
        {
            'get':'retrieve',
            'delete': 'destroy',
            'put':'update',
            'patch':'partial_update',
        }
    )),
    path('orders', views.CustomerOrderViewset.as_view(
        {
            'get': 'list',
            'post': 'create',
        }
    )),
    path('orders/<int:pk>', views.CustomerOrderViewset.as_view(
        {
            'get': 'retrieve',
            'delete': 'destroy',
            'put':'update',
            'patch':'partial_update',
        }
    )),
]
