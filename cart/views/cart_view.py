from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cart.models.cart_model import Cart, CartItem
from cart.serializers import (
    CartSerializer, AddToCartSerializer, 
    UpdateCartItemSerializer
)
from utils.shortcuts import get_object_or_404
from rest_framework.decorators import action
from utils import ResponseFormatter


class CartMixin:
    permission_classes = [IsAuthenticated]
    
    def get_or_create_cart(self):
        cart, _ = Cart.objects.get_or_create(customer=self.request.user.customer)
        return cart

class CartViewSet(CartMixin, viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.customer)

    def list(self, request, *args, **kwargs):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        cart = self.get_or_create_cart()
        return ResponseFormatter.success_response(
            data={'count': cart.total_items}
        )

class CartItemCreateView(CartMixin, generics.CreateAPIView):
    serializer_class = AddToCartSerializer

    def create(self, request, *args, **kwargs):
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        for item_data in serializer.validated_data['items']:
            product_color = item_data['product_color']
            quantity = item_data['quantity']

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_color=product_color,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        return Response(CartSerializer(cart).data)

class CartItemDestroyUpdateView(CartMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateCartItemSerializer
    lookup_field = 'uuid'
    lookup_url_kwarg = 'item_uuid'

    def get_queryset(self):
        cart = self.get_or_create_cart()
        return cart.items.all()

    def update(self, request, *args, **kwargs):
        cart = self.get_or_create_cart()
        cart_item = self.get_object()
        
        data = request.data.copy()
        data['item_uuid'] = kwargs.get('item_uuid')
        
        serializer = self.get_serializer(
            data=data,
            context={'cart': cart}
        )
        serializer.is_valid(raise_exception=True)
        
        quantity = serializer.validated_data['quantity']
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity 
            cart_item.save()

        return Response(CartSerializer(cart).data)
        
    def destroy(self, request, *args, **kwargs):
            cart_item = get_object_or_404(self.get_queryset(), uuid=kwargs.get('item_uuid'))
            cart_item.delete()
            return Response(CartSerializer(self.get_or_create_cart()).data , status=status.HTTP_204_NO_CONTENT)


class CartClearView(CartMixin, generics.DestroyAPIView):
    def destroy(self, request, *args, **kwargs):
        cart = self.get_or_create_cart()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)
