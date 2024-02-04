from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import GetMenuItemSerializer, CreateMenuItemSerializer, UserGroupSerializer, UsernameSerializer, CartCreateSerializer, CartListSerializer, OrderSerializer, OrderItemSerializer, EmptyOrderItemSerializer, UpdateOrderSerializer,DeliveryUpdateOrderSerializer
from .permissions import IsManager, IsDelivery
from django.contrib.auth.models import User, Group
from rest_framework.throttling import AnonRateThrottle,UserRateThrottle
# Create your views here.

class MenuItemViewSet(viewsets.ModelViewSet):
    '''get method(list):Lists all Menu items
    get method(retrieve): Retrieves single Menu item
    Manager can create and modify menu items'''

    queryset = MenuItem.objects.all()
    serializer_class = GetMenuItemSerializer
    ordering_fields = ['title','price','category']
    search_fields = ['title','category__title']
    throttle_classes = [AnonRateThrottle,UserRateThrottle]

    # Overriding get_permissions method so that only Managers can do other methods than get
    def get_permissions(self):
        if self.action not in ['list', 'retrieve']:
            return [IsManager()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return []

    def get_serializer_class(self):
        if self.action not in ['list', 'retrieve']:
            return CreateMenuItemSerializer
        return GetMenuItemSerializer

class ManagerGroupViewset(viewsets.ModelViewSet):
    ''' /users: API view which shows list of users in a Manager group, when you post username you add user to the Manager group.
    /users/<int:pk> Retrieve user through its ID and by using delete method the User is removed from the Manager group'''

    permission_classes = [IsManager]
    # overriding get_queryset method to only obtain users from the Manager group
    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')

    def get_serializer_class(self):
        if self.action == 'create':
            return UsernameSerializer
        return UserGroupSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username') # getting what was written inside username field
# better version
        user_instance = get_object_or_404(User, username=username)
        manager_group = Group.objects.get(name='Manager') # getting Group object
        manager_group.user_set.add(user_instance)
        return Response({'message:''User successfully added to the manager group'},status=status.HTTP_201_CREATED)

# First version that made me solve it!
        # try:
        #     user_instance = User.objects.get(username=username) # retrieve User object based on the provided username
            # manager_group = Group.objects.get(name='Manager') # getting Group object
            # manager_group.user_set.add(user_instance)
            # return Response({'message:''User successfully added to the manager group'},status=status.HTTP_201_CREATED)

        # except User.DoesNotExist:
        #      return Response({'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)


    def destroy(self, request, *args, **kwargs):
        user_instance = self.get_object() # Get the user to be removed from the Manager group
        manager_group = Group.objects.get(name='Manager') # getting Group object
        manager_group.user_set.remove(user_instance) # removing user from Manager group
        return Response({'message':'User successfully removed from the manager group'},status=status.HTTP_200_OK)
# NOTE: perform_destroy can be called after destroy to handle actions after deletion of the object


class DeliveryCrewViewset(viewsets.ModelViewSet):
    ''' /users: API view which shows list of users in a Delivery crew group, when you post username you add user to the Delivery crew group.
    /users/<int:pk> Retrieve user through its ID and by using delete method the User is removed from the Delivery crew group'''

    permission_classes = [IsManager]

     # overriding get_queryset method to only obtain users from the Delivery_crew group
    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery crew')

    def get_serializer_class(self):
        if self.action == 'create':
            return UsernameSerializer
        return UserGroupSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username') # getting what was written inside username field
        user_instance = get_object_or_404(User, username=username)
        delivery_group = Group.objects.get(name='Delivery crew') # getting Group object
        delivery_group.user_set.add(user_instance)
        return Response({'message':'User successfully added to the Delivery crew group'},status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user_instance = self.get_object() # Get the user to be removed from the Manager group
        delivery_group = Group.objects.get(name='Delivery crew') # getting Group object
        delivery_group.user_set.remove(user_instance) # removing user from Delivery crew group
        return Response({'message':'User successfully removed from the Delivery crew group'},status=status.HTTP_200_OK)

class CartViewset(viewsets.ModelViewSet):
    '''get method: "Lists all items in the cart for current user for list method and single item for retrieve method.
    post method: Add new item into the cart.
    delete method: deletes all items from the cart on list method or single item on retrieve'''

    queryset = Cart.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AnonRateThrottle,UserRateThrottle]

    def get_serializer_class(self):
        if self.action in ['create', 'update','partial_update']:
            return CartCreateSerializer
        return CartListSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user) # Filter just one user who is doing the request

    def destroy(self, request, *args, **kwargs):
        single_item = kwargs.get('pk') # Handles the deletion of the single item URL: api/cart/menu-items/<int:pk>
        if single_item:
            cart_instance = get_object_or_404(Cart, id=single_item)
            cart_instance.delete()
            return Response({'message': 'The item has been removed'})
        else: # Handles the deletion of all items in the cart URL: api/cart/menu-items
            cart_instance = self.get_queryset()
            cart_instance.delete()
            return Response({'message': 'The cart is empty'}, status=status.HTTP_204_NO_CONTENT)

class CustomerOrderViewset(viewsets.ModelViewSet):
    '''get method(list): shows Orders with Order items for current user. (Manager see all orders, Delivery crew member see orders assigned to him)
    get method(retrieve): shows Order and Order items for specific order
    post method(create): creates an order and puts items from the Cart into Order as Order items. Than deletes items from the Cart.
    put,patch methods(update, partial_update): Manager can assign/change delivery crew and status, Delivery crew can change status(just partial update).
    delete method(destroy): Only for manager, can delete specific order(<int:pk> url)'''

    queryset = Order.objects.all()
    permission_classes=[permissions.IsAuthenticated]
    ordering_fields = ['status','total','date']
    search_fields = ['user__username']

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        if self.request.user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user) # Filter just orders for the current delivery crew who is browsing
        else:
            return Order.objects.filter(user=self.request.user) # Filter just one user who is doing the request

    def get_serializer_class(self):
        if self.action == 'create': # Just post button to be visible to confirm order
            return EmptyOrderItemSerializer
        elif self.action in ['update','partial_update'] and self.request.user.groups.filter(name='Manager').exists(): # Manager can update status and assign/change delivery crew
            return UpdateOrderSerializer
        elif self.action == 'partial_update':
            return DeliveryUpdateOrderSerializer # Delivery crew can change only status
        return OrderSerializer

    def get_permissions(self):
        if self.action in ['destroy','update']: # Only a manager can delete, put or patch current Order
            return [IsManager()]
        elif self.action == 'partial_update' and self.request.user.groups.filter(name='Manager').exists():
            return [IsManager()]
        elif self.action == 'partial_update':
            return [IsDelivery()]
        else:
            return [permissions.IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user = self.request.user)
        if not cart_items:
            return Response({'message': 'The cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)

        new_order = Order.objects.create(user=self.request.user, total = 0)

        for cart_item in cart_items:
            order_item_data = {
                'order': new_order.id,
                'menuitem': cart_item.menuitem.id,
                'quantity': cart_item.quantity,
                'unit_price': cart_item.unit_price,
                'price': cart_item.price
            }

            order_item_serializer = OrderItemSerializer(data = order_item_data)
            if order_item_serializer.is_valid():
                order_item_serializer.save()

        new_order.update_total()

        cart_items.delete()

        return Response({'message': 'Checkout successful'}, status=status.HTTP_201_CREATED)


