from django.http import JsonResponse
from django.db.models import Sum, Count
from datetime import datetime
from employee.models import Employee
from customer.models import Customer
from order.models import Order
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth import get_user_model
from django.utils import timezone

User  = get_user_model()

def dashboard_data(request):
    total_sales = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_employees = Employee.objects.count()
    active_clients = Customer.objects.filter(user__is_active=True).count()

    # Count currently active users with valid access tokens
    # Ensure you are filtering based on the correct field
    valid_tokens = OutstandingToken.objects.filter(expires_at__gt=timezone.now())
    active_users_count = User.objects.filter(id__in=valid_tokens.values('user_id'), is_active=True).count()

    # Get monthly sales and client counts
    current_year = datetime.now().year
    monthly_sales = Order.objects.filter(created_at__year=current_year).values('created_at__month').annotate(total_sales=Sum('total_amount')).order_by('created_at__month')
    
    monthly_clients = Customer.objects.filter(user__date_joined__year=current_year).values('user__date_joined__month').annotate(client_count=Count('id')).order_by('user__date_joined__month')

    sales_data = {month['created_at__month']: month['total_sales'] for month in monthly_sales}
    clients_data = {month['user__date_joined__month']: month['client_count'] for month in monthly_clients}

    data = {
        'total_sales': total_sales,
        'total_employees': total_employees,
        'active_clients': active_clients,
        'active_users': active_users_count,
        'monthly_sales': sales_data,
        'monthly_clients': clients_data,
    }
    return JsonResponse(data)