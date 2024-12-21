from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Sum, F, Count
from ..models import Order, OrderItem
from ..serializers.order_serializers import OrderSerializer, OrderCreateSerializer
from cart.models import Cart
from utils import ResponseFormatter, BadRequestError, NotFoundError
from rest_framework.response import Response

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user.customer
        ).select_related(
            'customer'
        ).prefetch_related(
            'items__product_color__product',
            'items__product_color__color'
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ResponseFormatter.success_response(
            data=serializer.data
        )

    @action(detail=False, methods=['get'])
    def count(self, request):
        count = self.get_queryset().count()
        return ResponseFormatter.success_response(
            data={'count': count}
        )

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request):
        try:
            cart = Cart.objects.get(customer=request.user.customer)
            if not cart.items.exists():
                raise BadRequestError(
                    en_message="Cart is empty",
                    ar_message="السلة فارغة"
                )
            order = Order.objects.create(
                customer=request.user.customer,
                total_amount=0,
                notes=request.data.get('notes', ''),
                phone=request.data.get('phone',''),
                email=request.data.get('email',''),
                address=request.data.get('address',''),
                city=request.data.get('city',''),
                postal_code=request.data.get('postal_code','')
            )
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_color=cart_item.product_color,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product_color.price,
                )

            total_amount = OrderItem.objects.filter(order=order).aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )['total'] or 0

            order.total_amount = total_amount
            order.save()

            cart.items.all().delete()

            return ResponseFormatter.success_response(
                data=OrderSerializer(order).data,
                status_code=status.HTTP_201_CREATED
            )

        except Cart.DoesNotExist:
            raise NotFoundError(
                en_message="Cart not found",
                ar_message="لم يتم العثور على السلة"
            )
        except Exception as e:
            raise e