# django
from django.shortcuts import get_object_or_404
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.color_model import Color
from ..models.product_color_model import ProductColor
from section.models.category_model import Category

class ProductUpdateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField(required=False)

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category']
        
    def update(self, instance, validated_data):
        '''
            updates a product instance with the provided validated data. 
            handles the update of product colors, including adding new colors and updating existing ones. 
            If a category UUID is provided, it updates the product's category. 
            returns the updated product instance.
        '''
        
        product_colors_data = self.context['request'].data.get('product_colors', [])
        category_uuid = validated_data.pop('category', None)
        
        if category_uuid:
            category = get_object_or_404(Category, uuid=category_uuid)
        else:
            category = instance.category
        
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.category = category
        instance.save()

        existing_colors = {pc.color.hex_code: pc.color.hex_code for pc in instance.product_colors.all()}
        for product_color_data in product_colors_data:
            color_data = product_color_data.get('color', {})
            color_hex = color_data.get('hex_code')

            if color_hex:
                if color_hex in existing_colors:
                    product_color = existing_colors[color_hex]
                    product_color.price = product_color_data.get('price', product_color.price)
                    product_color.quantity = product_color_data.get('quantity', product_color.quantity)
                    product_color.save()
                else:
                    color = Color.objects.create(hex_code=color_hex)
                    ProductColor.objects.create(
                        product=instance,
                        color=color,
                        price=product_color_data.get('price'),
                        quantity=product_color_data.get('quantity')
                    )

        return instance