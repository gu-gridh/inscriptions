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