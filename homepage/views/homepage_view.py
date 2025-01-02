from django.db import models
from django.http import JsonResponse
from product.models.product_model import Product
from product.models.rate_model import Rate


def homepage_data(request):
    # Get the top 10 sold products
    top_sold_products = Product.objects.filter(sold_counter__gt=0).order_by('-sold_counter')[:10]

    # If no sold products, get the newest 10 products
    if not top_sold_products:
        top_sold_products = Product.objects.order_by('-created_at')[:10]

    # # Get 10 random products
    # random_products = Product.objects.order_by('?')[:10]

    top_sold_products_data = [
        {
            'uuid': product.uuid,
            'name': product.name,
            'image': request.build_absolute_uri(product.image) if product.image else None,
            'category': str(product.category),
            'sold_counter': product.sold_counter,
            'created_at': product.created_at,
            'average_rating': get_average_rating(product),
        }
        for product in top_sold_products
    ]

    data = {
        'results': top_sold_products_data,
    }
    return JsonResponse(data)

def get_average_rating(product):
    ratings = Rate.objects.filter(product=product)
    average = ratings.aggregate(models.Avg('score'))['score__avg']
    return average if average is not None else 0.0