from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.admin import EmptyFieldListFilter
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from saintsophia.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
from leaflet.admin import LeafletGeoAdmin
from django.conf import settings
# from admin_auto_filters.filters import AutocompleteFilter
# from rangefilter.filters import NumericRangeFilter
# from django.contrib.admin import EmptyFieldListFilter

DEFAULT_LONGITUDE =  30.514299
DEFAULT_LATITUDE  = 50.452890
DEFAULT_ZOOM = 20
MAX_ZOOM = 24
MIN_ZOOM = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['text', 'text_ukr']
    search_fields = ['text', 'text_ukr']
    
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['text', 'text_ukr']
    search_fields = ['text', 'text_ukr']
    
    
@admin.register(ImageType)
class ImageTypeAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']
    
    
@admin.register(InscriptionType)
class InscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ['text', 'text_ukr']
    search_fields = ['text', 'text_ukr']
    

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['text', 'text_ukr']
    search_fields = ['text', 'text_ukr']
    

@admin.register(WritingSystem)
class WritingSystemAdmin(admin.ModelAdmin):
    list_display = ['text', 'text_ukr']
    search_fields = ['text', 'text_ukr']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname']
    search_fields = ['firstname', 'lastname', 'firstname_ukr', 'lastname_ukr']
    

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['short_title']
    search_fields = ['short_title', 'observation']
    

@admin.register(Panel)
class PanelAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    display_raw = True
    fields = [*get_fields(Panel, exclude=['id'])]
    readonly_fields = [*DEFAULT_FIELDS]
    filter_horizontal = ['tags']
    list_display = ['title', 'room', 'data_available']
    search_fields = ['title', 'room']
    filter_horizontal = ['tags']
    list_filter = [ ('spatial_position', EmptyFieldListFilter), ('spatial_direction', EmptyFieldListFilter), ("data_available")]
    
    settings_overrides = {
       'DEFAULT_CENTER': (DEFAULT_LATITUDE, DEFAULT_LONGITUDE),
       'DEFAULT_ZOOM': DEFAULT_ZOOM,
       'MAX_ZOOM': MAX_ZOOM,
       'MIN_ZOOM': MIN_ZOOM,
       'TILES' : [('GROUND FLOOR', 'https://data.dh.gu.se/tiles/saint_sophia_ground_floor/{z}/{x}/{y}.png', {'attribution': '&copy; GRIDH', 'maxNativeZoom':24, 'maxZoom': 25})],
       'OVERLAYS': [('SECOND FLOOR', 'https://data.dh.gu.se/tiles/saint_sophia_second_floor/{z}/{x}/{y}.png', {'attribution': '&copy; GRIDH', 'maxNativeZoom':24, 'maxZoom': 25})]
    }
    
    change_form_template = 'apps/inscriptions/panel_change_form.html'
    

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin,):
    filter_horizontal = ['tags', 'genre']
    # readonly_fields = ['panel']
    list_display = ['panel', 'id', 'language', 'title']
    search_fields = ['id', 'language__text', 'panel__title']
    autocomplete_fields = ['panel']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin,):
    fields              = ['image_preview', *get_fields(Image, exclude=['id'])]
    readonly_fields     = ['iiif_file', 'uuid', 'image_preview', *DEFAULT_FIELDS]
    autocomplete_fields = ['panel', 'inscription']
    list_display = ['panel', 'inscription', 'type_of_image']
    search_fields = ['panel__title', 'type_of_image__text', 'iiif_file']
    list_per_page = 10
    
    def image_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="300" />')
    
    def thumbnail_preview(self, obj):
        return format_html(f'<img src="{settings.IIIF_URL}{obj.iiif_file}/full/full/0/default.jpg" height="100" />')
    

@admin.register(ObjectRTI)
class ObjectRTIAdmin(admin.ModelAdmin):
    autocomplete_fields = ['panel']
    list_display = ['panel']
    search_fields = ['panel__title', 'url']
    
    
@admin.register(ObjectMesh3D)
class ObjectMesh3DAdmin(admin.ModelAdmin):
    autocomplete_fields = ['panel']
    list_display = ['panel']
    search_fields = ['panel__title', 'url']
    
    
@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['inscription']
    list_display = ['inscription']
    search_fields = ['inscription__panel__title', 'text', 'language__text', 'language__text_ukr', 'inscription__title']
    
    
@admin.register(Description)
class DescriptionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['inscription']
    list_display = ['inscription', 'language']
    search_fields = ['inscription__panel__title', 'text', 'language__text', 'language__text_ukr', 'inscription__title']