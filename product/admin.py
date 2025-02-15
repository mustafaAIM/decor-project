from django.contrib import admin
from product.models import Product, Color, ProductColor, Rate
from django.utils.safestring import mark_safe

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'get_colors_count', 'get_average_rating')
    search_fields = ('name', 'description')
    readonly_fields = ('uuid',)
    list_per_page = 25

    def get_colors_count(self, obj):
        return obj.product_colors.count()
    get_colors_count.short_description = 'Colors Available'

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            avg = sum(float(rate.score) for rate in ratings) / len(ratings)
            return f"{avg:.1f}"
        return "No ratings"
    get_average_rating.short_description = 'Avg Rating'

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('hex_code', 'uuid', 'color_preview')
    search_fields = ('hex_code',)
    readonly_fields = ('uuid', 'color_preview')
    list_per_page = 25

    def color_preview(self, obj):
        return mark_safe(f'<div style="background-color: {obj.hex_code}; width: 30px; height: 30px; border: 1px solid #000;"></div>')
    color_preview.short_description = 'Color Preview'

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'price', 'quantity', 'uuid')
    list_filter = ('color', 'product')
    search_fields = ('product__name', 'color__hex_code')
    autocomplete_fields = ['product', 'color']
    readonly_fields = ('uuid',)
    list_per_page = 25

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'score')
    list_filter = ('score',)
    search_fields = ('product__name', 'customer__user__email')
    autocomplete_fields = ['product', 'customer']
    list_per_page = 25
