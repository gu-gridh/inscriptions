from saintsophia.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import SerializerMethodField
from . import models
from saintsophia.utils import get_fields, DEFAULT_FIELDS
from .models import *
from django.db.models import Q


class LanguageSerializer(DynamicDepthSerializer):
    class Meta:
        model = Language
        fields = get_fields(Language, exclude=DEFAULT_FIELDS) + ['id']
        
        
class WritingSystemSerializer(DynamicDepthSerializer):
    class Meta:
        model = WritingSystem
        fields = get_fields(WritingSystem, exclude=DEFAULT_FIELDS) + ['id']
        

class PanelSerializer(DynamicDepthSerializer):

    list_of_languages = SerializerMethodField()
    number_of_inscriptions = SerializerMethodField()

    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS)+ ['id', 'list_of_languages', 'number_of_inscriptions']
        
    def get_list_of_languages(self, obj):
        inscriptions_on_panel = obj.inscriptions.all()
        
        languages = []
        for inscription in inscriptions_on_panel:
            if inscription.language is not None:
                languages.append(inscription.language.text)
        
        return set(languages)
    
    def get_number_of_inscriptions(self, obj):
        inscriptions_on_panel = obj.inscriptions.all()
        
        return len(inscriptions_on_panel)
        
class PanelGeoSerializer(GeoFeatureModelSerializer):
    attached_photograph = SerializerMethodField()
    attached_topography = SerializerMethodField()
    attached_RTI = SerializerMethodField()
    attached_3Dmesh = SerializerMethodField()

    
    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS)+ ['id', 'attached_photograph', 'attached_topography', 'attached_RTI', 'attached_3Dmesh']
        geo_field = 'geometry'
        depth = 1
        
    def get_attached_photograph(self, obj):
        return obj.images.filter(published=True).filter(type_of_image__text="Orthophoto").values()
    
    def get_attached_topography(self, obj):
        return obj.images.filter(published=True).filter(type_of_image__text="Topography").values()
    
    def get_attached_RTI(self, obj):
        return obj.rti.filter(published=True).values()
    
    def get_attached_3Dmesh(self, obj):
        return obj.mesh.filter(published=True).values()
    
    
class PanelMetadataSerializer(DynamicDepthSerializer):
    
    number_of_inscriptions = SerializerMethodField()
    number_of_languages = SerializerMethodField()
    list_of_languages = SerializerMethodField()
    
    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS +['geometry', 
                                                            'spatial_position', 
                                                            'spatial_direction'])+ ['id', 
                                                                                'number_of_inscriptions', 
                                                                                'number_of_languages',
                                                                                'list_of_languages']
        
    def get_number_of_inscriptions(self, obj):
        return obj.inscriptions.count()
    
    def get_number_of_languages(self, obj):
        inscriptions_on_panel = obj.inscriptions.all()
        
        languages = []
        for inscription in inscriptions_on_panel:
            if inscription.language is not None:
                languages.append(inscription.language.text)
            
        return len(set(languages))
    
    def get_list_of_languages(self, obj):
        inscriptions_on_panel = obj.inscriptions.all()
        
        languages = []
        for inscription in inscriptions_on_panel:
            if inscription.language is not None:
                languages.append(inscription.language.text)
        
        return set(languages)
        
        
class PanelCoordinatesSerializer(GeoFeatureModelSerializer):
    
    floor = SerializerMethodField()
    
    class Meta:
        model = Panel
        fields = ['id', 'title', 'floor', 'published', 'data_available']
        geo_field = 'geometry'
        depth = 1
        
    def get_floor(self, obj):
        # the floor at which each panel can be found is the first character of the title
        return obj.title[0]
        
        
class InscriptionSerializer(DynamicDepthSerializer):
    
    inscription_iiif_url = SerializerMethodField()

    class Meta:
        model = Inscription
        fields = get_fields(Inscription, exclude=DEFAULT_FIELDS)+ ['id', 'inscription_iiif_url']
        
    def get_inscription_iiif_url(self, obj):
        images = obj.panel.images.values()
        
        url = ""
        if len(images) > 0:
            url = f"https://img.dh.gu.se/saintsophia/static/{images[0]['iiif_file']}/{obj.position_on_surface}/"
        
        return url


class InscriptionTagsSerializer(DynamicDepthSerializer):

    class Meta:
        model = Tag
        fields = get_fields(Tag, exclude=DEFAULT_FIELDS)+ ['id']
        
        
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
        

class TranslationSerializer(DynamicDepthSerializer):

    class Meta:
        model = Translation
        fields = get_fields(Translation, exclude=DEFAULT_FIELDS)+ ['id']
        
        
class DescriptionSerializer(DynamicDepthSerializer):

    class Meta:
        model = Description
        fields = get_fields(Description, exclude=DEFAULT_FIELDS)+ ['id']