from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from product.models import Product, ProductColor, Color
from section.models import Section, Category
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with sample products'

    def handle(self, *args, **kwargs):
        # Create sample sections
        sections_data = [
            {
                'title': 'Men\'s Fashion',
                'description': 'Fashion items for men',
                'categories': [
                    'Clothing',
                    'Shoes',
                    'Accessories',
                    'Sportswear'
                ]
            },
            {
                'title': 'Women\'s Fashion',
                'description': 'Fashion items for women',
                'categories': [
                    'Clothing',
                    'Shoes',
                    'Accessories',
                    'Bags'
                ]
            },
            {
                'title': 'Electronics',
                'description': 'Electronic devices and accessories',
                'categories': [
                    'Smartphones',
                    'Laptops',
                    'Accessories',
                    'Gaming'
                ]
            }
        ]

        # Create sections and their categories
        sections = {}
        categories = []
        
        for section_data in sections_data:
            section, _ = Section.objects.get_or_create(
                title=section_data['title'],
                defaults={'description': section_data['description']}
            )
            sections[section.title] = section
            
            for category_name in section_data['categories']:
                category, _ = Category.objects.get_or_create(
                    title=category_name,
                    section=section,
                    defaults={'description': f'{category_name} in {section.title}'}
                )
                categories.append(category)

        # Create colors
        colors = [
            {'hex_code': '#000000'},  # Black
            {'hex_code': '#FFFFFF'},  # White
            {'hex_code': '#FF0000'},  # Red
            {'hex_code': '#0000FF'},  # Blue
            {'hex_code': '#00FF00'},  # Green
            {'hex_code': '#000080'},  # Navy
            {'hex_code': '#808080'},  # Gray
            {'hex_code': '#F5F5DC'},  # Beige
        ]

        for color_data in colors:
            Color.objects.get_or_create(hex_code=color_data['hex_code'])

        # Product data with category assignments
        products = [
            {
                'name': 'Classic Cotton T-Shirt',
                'description': 'Premium quality cotton t-shirt perfect for everyday wear',
                'price_range': (19.99, 24.99),
                'quantity_range': (50, 200),
                'category': 'Clothing'
            },
            {
                'name': 'Slim Fit Jeans',
                'description': 'Modern slim fit jeans with stretch comfort',
                'price_range': (59.99, 79.99),
                'quantity_range': (30, 150),
                'category': 'Clothing'
            },
            {
                'name': 'Casual Hoodie',
                'description': 'Comfortable hoodie with kangaroo pocket',
                'price_range': (39.99, 49.99),
                'quantity_range': (40, 180),
                'category': 'Clothing'
            },
            {
                'name': 'Running Shoes',
                'description': 'Lightweight running shoes with cushioned sole',
                'price_range': (89.99, 129.99),
                'quantity_range': (20, 100),
                'category': 'Shoes'
            },
            {
                'name': 'Leather Wallet',
                'description': 'Genuine leather wallet with multiple card slots',
                'price_range': (29.99, 49.99),
                'quantity_range': (60, 120),
                'category': 'Accessories'
            },
            {
                'name': 'Backpack',
                'description': 'Durable backpack with laptop compartment',
                'price_range': (49.99, 79.99),
                'quantity_range': (30, 80),
                'category': 'Accessories'
            },
            {
                'name': 'Sunglasses',
                'description': 'UV protection sunglasses with polarized lenses',
                'price_range': (79.99, 149.99),
                'quantity_range': (40, 100),
                'category': 'Accessories'
            },
            {
                'name': 'Winter Jacket',
                'description': 'Warm winter jacket with water-resistant exterior',
                'price_range': (129.99, 199.99),
                'quantity_range': (20, 60),
                'category': 'Clothing'
            },
            {
                'name': 'Athletic Shorts',
                'description': 'Breathable athletic shorts for sports and training',
                'price_range': (24.99, 34.99),
                'quantity_range': (50, 150),
                'category': 'Clothing'
            },
            {
                'name': 'Dress Shirt',
                'description': 'Professional dress shirt with wrinkle-resistant fabric',
                'price_range': (44.99, 69.99),
                'quantity_range': (40, 120),
                'category': 'Clothing'
            },
            {
                'name': 'Canvas Sneakers',
                'description': 'Classic canvas sneakers for casual wear',
                'price_range': (34.99, 49.99),
                'quantity_range': (60, 200),
                'category': 'Shoes'
            },
            {
                'name': 'Wool Sweater',
                'description': 'Warm wool blend sweater for cold weather',
                'price_range': (69.99, 99.99),
                'quantity_range': (30, 90),
                'category': 'Clothing'
            },
            {
                'name': 'Baseball Cap',
                'description': 'Adjustable baseball cap with embroidered logo',
                'price_range': (19.99, 29.99),
                'quantity_range': (100, 300),
                'category': 'Accessories'
            },
            {
                'name': 'Leather Belt',
                'description': 'Classic leather belt with metal buckle',
                'price_range': (29.99, 49.99),
                'quantity_range': (70, 150),
                'category': 'Accessories'
            },
            {
                'name': 'Swim Shorts',
                'description': 'Quick-dry swim shorts with mesh lining',
                'price_range': (24.99, 39.99),
                'quantity_range': (40, 120),
                'category': 'Clothing'
            },
            {
                'name': 'Formal Blazer',
                'description': 'Tailored formal blazer for professional occasions',
                'price_range': (149.99, 249.99),
                'quantity_range': (20, 50),
                'category': 'Clothing'
            },
            {
                'name': 'Yoga Pants',
                'description': 'Stretchy yoga pants with moisture-wicking fabric',
                'price_range': (39.99, 59.99),
                'quantity_range': (50, 150),
                'category': 'Clothing'
            },
            {
                'name': 'Denim Jacket',
                'description': 'Classic denim jacket with button closure',
                'price_range': (69.99, 99.99),
                'quantity_range': (30, 80),
                'category': 'Clothing'
            },
            {
                'name': 'Polo Shirt',
                'description': 'Classic polo shirt with embroidered detail',
                'price_range': (29.99, 44.99),
                'quantity_range': (60, 180),
                'category': 'Clothing'
            },
            {
                'name': 'Winter Scarf',
                'description': 'Soft winter scarf in various patterns',
                'price_range': (19.99, 34.99),
                'quantity_range': (80, 200),
                'category': 'Accessories'
            },
        ]

        # Create products
        for product_data in products:
            # Find appropriate category
            category = random.choice([cat for cat in categories if cat.title == product_data['category']])
            
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                category=category
            )
            
            # Create product colors
            selected_colors = random.sample(list(Color.objects.all()), random.randint(3, 5))
            
            for color in selected_colors:
                ProductColor.objects.create(
                    product=product,
                    color=color,
                    price=Decimal(str(random.uniform(
                        product_data['price_range'][0],
                        product_data['price_range'][1]
                    ))).quantize(Decimal('0.01')),
                    quantity=random.randint(
                        product_data['quantity_range'][0],
                        product_data['quantity_range'][1]
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created product: {product.name} in category {category.title}')
            )
