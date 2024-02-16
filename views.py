from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q
from saintsophia.abstract.views import DynamicDepthViewSet, GeoViewSet
from saintsophia.abstract.models import get_fields, DEFAULT_FIELDS
from django.db.models import Q
from django.http import HttpResponse
import json


class PanelViewSet(DynamicDepthViewSet):
    queryset = models.Panel.objects.all().order_by('title')
    serializer_class = serializers.PanelSerializer
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS+['spatial_position', 'spatial_direction'])
    
    
class InscriptionViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all().order_by('title')
    serializer_class = serializers.InscriptionSerializer
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS)
    
    
class IIIFImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    
    queryset = models.Image.objects.all().order_by('id')
    serializer_class = serializers.TIFFImageSerializer
    filterset_fields = get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])