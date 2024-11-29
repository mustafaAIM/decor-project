from datetime import timezone
from django.db import transaction
from ..models import Order, OrderItem
from cart.models import Cart
from utils.api_exceptions import BadRequestError

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, shipping_address, phone_number):
        """Create an order from user's cart"""
        cart = Cart.objects.filter(user=user).first()
        
        if not cart or cart.items.count() == 0:
            raise BadRequestError(
                en_message="Cart is empty",
                ar_message="السلة فارغة"
            )

        total_amount = sum(item.subtotal for item in cart.items.all())
        
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            shipping_address=shipping_address,
            phone_number=phone_number,
            status=Order.OrderStatus.PAYMENT_PENDING
        )

        for cart_item in cart.items.all():
            if cart_item.quantity > cart_item.product_color.quantity:
                raise BadRequestError(
                    en_message=f"Not enough stock for {cart_item.product_color.product.name}",
                    ar_message=f"لا يوجد مخزون كافٍ من {cart_item.product_color.product.name}"
                )
                
            OrderItem.objects.create(
                order=order,
                product_color=cart_item.product_color,
                quantity=cart_item.quantity,
                price=cart_item.product_color.price
            )
            
            cart_item.product_color.quantity -= cart_item.quantity
            cart_item.product_color.save()

        cart.items.all().delete()
        
        return order

    @staticmethod
    def update_order_status(order, status):
        """Update order status and handle related logic"""
        order.status = status
        if status == Order.OrderStatus.PAID:
            order.paid_at = timezone.now()
        order.save() 