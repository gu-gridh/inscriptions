from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from saintsophia.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
# from admin_auto_filters.filters import AutocompleteFilter
# from rangefilter.filters import NumericRangeFilter
# from django.contrib.admin import EmptyFieldListFilter

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    
    
@admin.register(MeshTechnique)
class MeshTechniqueAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    
    
@admin.register(ImageType)
class ImageTypeAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    
    
@admin.register(InscriptionType)
class InscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['short_title']
    search_fields = ['short_title', 'observation']
    

@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin,):
    display_raw = True
    list_display = ['title', 'room']
    search_fields = ['title', 'room']