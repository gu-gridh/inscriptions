from saintsophia.abstract.serializers import DynamicDepthSerializer, GenericSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import SerializerMethodField
from . import models
from saintsophia.utils import get_fields, DEFAULT_FIELDS
from .models import *
from django.db.models import Q
from django.utils.html import strip_tags
import html
import re

_BR_RE = re.compile(r'<br\s*/?>', re.IGNORECASE)
_BLOCK_RE = re.compile(r'</?(p|div)\s*/?>', re.IGNORECASE)
_TAG_RE = re.compile(r'</?([a-zA-Z0-9]+)(?:\s[^>]*)?>')
_SCRIPT_STYLE_RE = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.IGNORECASE | re.DOTALL)
_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


def _clean_rich_text_keep_p_br(value):
    """Strip HTML while preserving only normalized <p> and <br /> tags."""
    if not value:
        return value

    value = html.unescape(value)
    value = _SCRIPT_STYLE_RE.sub('', value)
    value = _COMMENT_RE.sub('', value)

    def _replace_tag(match):
        raw = match.group(0)
        tag_name = match.group(1).lower()

        if tag_name == 'p':
            return '</p>' if raw.lstrip().startswith('</') else '<p>'
        if tag_name == 'br':
            return '<br />'
        return ''

    return _TAG_RE.sub(_replace_tag, value).strip()


def _clean_rich_text(value, preserve_breaks=False, preserve_tags=False):
    """Strip HTML tags and decode entities from a RichText value.

    When *preserve_breaks* is True, ``<br>`` tags and block boundaries
    (``<p>``, ``</p>``, ``<div>``, …) are converted to newline characters
    before the remaining markup is removed.

    When *preserve_tags* is True, all HTML is stripped except ``<p>``
    and ``<br />`` tags (normalized output).
    """
    if not value:
        return value
    if preserve_tags:
        return _clean_rich_text_keep_p_br(value)
    if preserve_breaks:
        value = _BR_RE.sub('\n', value)
        value = _BLOCK_RE.sub('\n', value)
    return html.unescape(strip_tags(value)).strip()


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


class RTIFromPanelSerializer(DynamicDepthSerializer):
    url_for_download = SerializerMethodField()

    class Meta:
        model = ObjectRTI
        fields = get_fields(ObjectRTI, exclude=DEFAULT_FIELDS) + ['id', 'url_for_download']

    def get_url_for_download(self, obj):
        # we can access the panel title from here...
        surface_title = obj.panel.title
        # ...or from here! Let's implement both right now and choose one to visualize, but we can always revert to the other!
        location_url = obj.url
        surface_from_url = (location_url.split('/')[-2])

        url_download = f"https://data.dh.gu.se/saintsophia/rti/{surface_from_url}.zip"
        
        return url_download


class PanelGeoSerializer(GeoFeatureModelSerializer):
    attached_photograph = SerializerMethodField()
    attached_topography = SerializerMethodField()
    attached_3Dmesh = MeshFromPanelSerializer(many=True)
    attached_RTI = RTIFromPanelSerializer(many=True) # ObjectRTISerializer(many=True)
    
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
    width = SerializerMethodField()
    height = SerializerMethodField()

    RICH_TEXT_FIELDS = [
        'transcription', 'interpretative_edition', 'romanisation',
        'translation_eng', 'translation_ukr', 'comments_eng', 'comments_ukr',
    ]
    # fields where only <p> and <br /> should be preserved
    PRESERVE_BREAKS_FIELDS = ['transcription', 'interpretative_edition', 'translation_eng', 'translation_ukr']
    class Meta:
        model = Inscription
        fields = get_fields(Inscription, exclude=DEFAULT_FIELDS)+ ['id', 'inscription_iiif_url', 'korniienko_image', 'width', 'height']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in self.RICH_TEXT_FIELDS:
            if field in data and data[field]:
                data[field] = _clean_rich_text(
                    data[field],
                    preserve_tags=field in self.PRESERVE_BREAKS_FIELDS,
                )
        return data

    def get_inscription_iiif_url(self, obj):
        images = obj.panel.images.filter(type_of_image=1).values() # 1 is orthophotos
        
        url = ""
        if len(images) > 0:
            url = f"https://img.dh.gu.se/saintsophia/static/{images[0]['iiif_file']}/{obj.position_on_surface}/"
        
        return url
    
    def get_width(self, obj):
        """Calculate inscription width in pixels from IIIF pct region: width = baseWidth * (pctWidth / 100)"""
        images = obj.panel.images.filter(type_of_image=1)
        if not images.exists() or not obj.position_on_surface:
            return None
            
        image = images.first()
        if not image.width:
            return None
            
        try:
            # Parse pct:x,y,width,height format from position_on_surface
            if obj.position_on_surface.startswith('pct:'):
                pct_str = obj.position_on_surface.replace('pct:', '')
                pct_values = pct_str.split(',')
                if len(pct_values) == 4:
                    pct_width = float(pct_values[2])
                    return int(image.width * (pct_width / 100))
        except:
            pass
        return None
    
    def get_height(self, obj):
        """Calculate inscription height in pixels from IIIF pct region: height = baseHeight * (pctHeight / 100)"""
        images = obj.panel.images.filter(type_of_image=1)
        if not images.exists() or not obj.position_on_surface:
            return None
            
        image = images.first()
        if not image.height:
            return None
            
        try:
            # Parse pct:x,y,width,height format from position_on_surface
            if obj.position_on_surface.startswith('pct:'):
                pct_str = obj.position_on_surface.replace('pct:', '')
                pct_values = pct_str.split(',')
                if len(pct_values) == 4:
                    pct_height = float(pct_values[3])
                    return int(image.height * (pct_height / 100))
        except:
            pass
        return None


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


class SummarySerializer(DynamicDepthSerializer):

    RICH_TEXT_FIELDS = [
        'transcription', 'interpretative_edition', 'romanisation',
        'translation_eng', 'translation_ukr', 'comments_eng', 'comments_ukr',
    ]
    PRESERVE_BREAKS_FIELDS = ['transcription']

    class Meta:
        model = Inscription
        fields = ['id']+get_fields(Inscription, exclude=['created_at', 'updated_at', 'inscription_iiif_url', 'korniienko_image'])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in self.RICH_TEXT_FIELDS:
            if field in data and data[field]:
                data[field] = _clean_rich_text(
                    data[field],
                    preserve_breaks=field in self.PRESERVE_BREAKS_FIELDS,
                )
        return data
