from django.contrib import admin
from section.models import Section, Category

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'uuid', 'description')
    search_fields = ('title', 'description')
    list_per_page = 25
    readonly_fields = ('uuid',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'uuid')
    list_filter = ('section',)
    search_fields = ('title', 'description', 'section__title')
    autocomplete_fields = ['section']
    list_per_page = 25
    readonly_fields = ('uuid',)
