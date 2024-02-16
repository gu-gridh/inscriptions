from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from saintsophia.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from leaflet.admin import LeafletGeoAdmin
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
    

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname']
    search_fields = ['firstname', 'lastname']
    

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['short_title']
    search_fields = ['short_title', 'observation']
    

@admin.register(Panel)
class PanelAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    display_raw = True
    list_display = ['title', 'room']
    search_fields = ['title', 'room']
    filter_horizontal = ['tags']
    

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin,):
    display_raw = True
    list_display = ['title', 'language', 'panel']
    search_fields = ['title', 'language', 'panel']
    
    
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin,):
    display_raw = True
    list_display = ['panel', 'inscription', 'type_of_image']
    search_fields = ['panel', 'inscription', 'type_of_image']
    

@admin.register(ObjectRTI)
class ObjectRTIAdmin(admin.ModelAdmin):
    display_raw = True
    list_display = ['panel']
    search_fields = ['panel', 'url']
    
    
@admin.register(ObjectMesh3D)
class ObjectMesh3DAdmin(admin.ModelAdmin):
    display_raw = True
    list_display = ['panel']
    search_fields = ['panel', 'url']