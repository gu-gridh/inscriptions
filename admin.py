from django.contrib.gis.db import models
from .models import *
from django.utils.html import format_html
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from saintsophia.utils import get_fields, DEFAULT_FIELDS, DEFAULT_EXCLUDE
# from admin_auto_filters.filters import AutocompleteFilter
# from rangefilter.filters import NumericRangeFilter
# from django.contrib.admin import EmptyFieldListFilter

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin,):
    display_raw = True
    list_display = ['name', 'geometry']
    search_fields = ['name']