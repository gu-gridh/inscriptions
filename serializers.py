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


class GenreSerializer(DynamicDepthSerializer):
    class Meta:
        model = Genre
        fields = get_fields(Genre, exclude=DEFAULT_FIELDS) + ['id']


class HistoricalPersonSerializer(DynamicDepthSerializer):
    class Meta:
        model = HistoricalPerson
        fields = get_fields(HistoricalPerson, exclude=DEFAULT_FIELDS) + ['id']


class BibliographyItemSerializer(DynamicDepthSerializer):
    
    class Meta:
        model = BibliographyItem
        fields = get_fields(BibliographyItem, exclude=DEFAULT_FIELDS)+ ['id']
        depth = 1


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


class ObjectRTISerializer(DynamicDepthSerializer):

    class Meta:
        model = ObjectRTI
        fields = get_fields(ObjectRTI, exclude=DEFAULT_FIELDS)+ ['id']


class MeshFromPanelSerializer(DynamicDepthSerializer):
    url_for_download = SerializerMethodField()

    class Meta:
        model = ObjectMesh3D
        fields = get_fields(ObjectMesh3D, exclude=DEFAULT_FIELDS)+ ['id', 'url_for_download']

    def get_url_for_download(self, obj):
        # we can access the panel title from here...
        surface_title = obj.panel.title
        # ...or from here! Let's implement both right now and choose one to visualize, but we can always revert to the other!
        location_url = obj.url
        surface_from_url = (location_url.split('/')[-1]).split('.')[0]

        url_download = f"https://data.dh.gu.se/saintsophia/meshoriginal/{surface_title}.zip"
        
        return url_download


class PanelGeoSerializer(GeoFeatureModelSerializer):
    attached_photograph = SerializerMethodField()
    attached_topography = SerializerMethodField()
    attached_3Dmesh = MeshFromPanelSerializer(many=True)
    attached_RTI = ObjectRTISerializer(many=True)
    
    class Meta:
        model = Panel
        fields = get_fields(Panel, exclude=DEFAULT_FIELDS)+ ['id', 'attached_photograph', 'attached_topography', 'attached_3Dmesh', 'attached_RTI']
        geo_field = 'geometry'
        depth = 1
        
    def get_attached_photograph(self, obj):
        return obj.images.filter(published=True).filter(type_of_image__text="Orthophoto").values()
    
    def get_attached_topography(self, obj):
        return obj.images.filter(published=True).filter(type_of_image__text="Topography").values()
    
    
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
    number_of_inscriptions = SerializerMethodField()
    
    class Meta:
        model = Panel
        fields = ['id', 'title', 'floor', 'number_of_inscriptions', 'published', 'data_available']
        geo_field = 'geometry'
        depth = 1
        
    def get_floor(self, obj):
        # the floor at which each panel can be found is the first character of the title
        return obj.title[0]

    def get_number_of_inscriptions(self, obj):
        return obj.inscriptions.count()
        

class KorniienkoImageSerializer(DynamicDepthSerializer):
    class Meta:
        model = KorniienkoImage
        fields = get_fields(KorniienkoImage, exclude=DEFAULT_FIELDS)+ ['id']
        depth = 2


class InscriptionSerializer(DynamicDepthSerializer):
    
    inscription_iiif_url = SerializerMethodField()
    korniienko_image = KorniienkoImageSerializer(many = True)

    class Meta:
        model = Inscription
        fields = get_fields(Inscription, exclude=DEFAULT_FIELDS)+ ['id', 'inscription_iiif_url', 'korniienko_image']
        
    def get_inscription_iiif_url(self, obj):
        images = obj.panel.images.filter(type_of_image=1).values() # 1 is orthophotos
        
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
        

class ObjectMesh3DSerializer(DynamicDepthSerializer):
    url_for_download = SerializerMethodField()

    class Meta:
        model = ObjectMesh3D
        fields = get_fields(ObjectMesh3D, exclude=DEFAULT_FIELDS)+ ['id', 'url_for_download']

    def get_url_for_download(self, obj):
        # we can access the panel title from here...
        surface_title = obj.panel.title
        
        # ...or from here! Let's implement both right now and choose one to visualize, but we can always revert to the other!
        location_url = obj.url
        surface_from_url = (location_url.split('/')[-1]).split('.')[0]

        url_download = f"https://data.dh.gu.se/saintsophia/meshoriginal/{surface_title}.zip"
        
        return url_download