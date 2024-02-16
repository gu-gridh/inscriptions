from saintsophia.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import SerializerMethodField
from . import models
from saintsophia.utils import get_fields, DEFAULT_FIELDS
from .models import *


class PanelSerializer(DynamicDepthSerializer):

    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class InscriptionSerializer(DynamicDepthSerializer):

    class Meta:
        model = Inscription
        fields = get_fields(Inscription, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class TIFFImageSerializer(DynamicDepthSerializer):
    
    class Meta:
        model = Image
        fields = get_fields(Image, exclude=DEFAULT_FIELDS)+ ['id']