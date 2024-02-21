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
        
        
class PanelGeoSerializer(GeoFeatureModelSerializer):
    attached_photograph = SerializerMethodField()
    attached_RTI = SerializerMethodField()
    attached_3Dmesh = SerializerMethodField()   
    
    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS)+ ['id', 'attached_photograph', 'attached_RTI', 'attached_3Dmesh']
        geo_field = 'geometry'
        depth = 1
        
    def get_attached_photograph(self, obj):
        return obj.images.filter(published=True).values()
    
    def get_attached_RTI(self, obj):
        return obj.rti.filter(published=True).values()
    
    def get_attached_3Dmesh(self, obj):
        return obj.mesh.filter(published=True).values()
        
        
class InscriptionSerializer(DynamicDepthSerializer):

    class Meta:
        model = Inscription
        fields = get_fields(Inscription, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class TIFFImageSerializer(DynamicDepthSerializer):
    
    class Meta:
        model = Image
        fields = get_fields(Image, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class ObjectRTISerializer(DynamicDepthSerializer):

    class Meta:
        model = ObjectRTI
        fields = get_fields(ObjectRTI, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class ObjectMesh3DSerializer(DynamicDepthSerializer):

    class Meta:
        model = ObjectMesh3D
        fields = get_fields(ObjectMesh3D, exclude=DEFAULT_FIELDS)+ ['id']