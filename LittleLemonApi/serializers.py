from . models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.db import IntegrityError

# If you want nested category title

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Category
#         fields = ['title']

class GetMenuItemSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.title')  # Showing category title instead of ID ()
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price','category','featured']

class CreateMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price','category','featured']

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'groups']

class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

# class CartSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(read_only=True)
#     class Meta:
#         model = Cart
#         fields = ['user','menuitem','quantity','unit_price','price']

class CartCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    unit_price = serializers.DecimalField(source='menuitem.price', read_only=True, max_digits=6, decimal_places=2, min_value=2)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']

    # overriding create function in a serializer class to get desired new object
    def create(self, validated_data):
        user = self.context['request'].user # context attribute is used to provide additional data to serializer beyond serialized model (Cart in this example)
        quantity = validated_data.get('quantity', 1)
        menuitem = validated_data.get('menuitem')

        # Calculate the price based on unit_price and quantity
        unit_price = menuitem.price
        calculated_price = unit_price * quantity
        try:
            # Creating desired Cart object
            cart_instance = Cart.objects.create(
                user=user,
                unit_price=unit_price,
                price=calculated_price,
                **validated_data    # rest of the validated data from validated_data dictionary
            )

            return cart_instance

        except IntegrityError:
            raise serializers.ValidationError('This item is already in the cart for the current user')

class CartListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    menuitem = serializers.CharField(source='menuitem.title')

    class Meta:
        model = Cart
        fields = ['id','user', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_order_items(self, order_instance):  # Custom method created to fetch OrderItem related to Order instance. It is important to use field_name after get to make this work
        order_items = OrderItem.objects.filter(order=order_instance)
        return OrderItemSerializer(order_items, many = True).data    # .data is used to extract only data, not whole serializer instance

class EmptyOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = []

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew', 'status']

class DeliveryUpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']