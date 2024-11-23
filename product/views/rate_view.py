# rest framework
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
# models
from ..models.rate_model import Rate 
# serializers
from ..serializers.rate_serializer import RateSerializer

class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
from datetime import datetime
from ..models.product_model import Product
import os

def generate_product_report(request):
    try:
        # Get all products
        products = Product.objects.all()
        
        # Calculate statistics
        products_with_images = products.exclude(image='').count()
        
        # Get base URL for images
        base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        
        # Prepare context for template
        context = {
            'products': products,
            'generated_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'year': datetime.now().year,
            'products_with_images': products_with_images,
            'latest_update': datetime.now().strftime("%d %b %Y"),
            'base_url': "http://localhost:80",  # Add base_url to context
        }
        
        # Render HTML
        html_string = render_to_string('product/product_report.html', context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="product_catalog.pdf"'
        
        # Create PDF with base URL for resolving images
        HTML(string=html_string, base_url="http://localhost:80/media/").write_pdf(
            target=response,
            presentational_hints=True
        )
        
        return response
    except Exception as e:
        print(f"PDF Generation error: {e}")
        raise