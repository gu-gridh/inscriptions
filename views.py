from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q, Value, Case, When
from saintsophia.abstract.views import DynamicDepthViewSet, GeoViewSet
from saintsophia.abstract.models import get_fields, DEFAULT_FIELDS
from django.http import HttpResponse
import json
import django_filters
from rest_framework.response import Response


class LanguageViewSet(DynamicDepthViewSet):
    queryset = models.Language.objects.all().order_by('text')
    serializer_class = serializers.LanguageSerializer
    filterset_fields = get_fields(models.Language, exclude=DEFAULT_FIELDS)


class LanguageWithDataViewSet(DynamicDepthViewSet):
    queryset = models.Language.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text')
    serializer_class = serializers.LanguageSerializer
    filterset_fields = get_fields(models.Language, exclude=DEFAULT_FIELDS)
    

class WritingSystemViewSet(DynamicDepthViewSet):
    queryset = models.WritingSystem.objects.all().order_by('text')
    serializer_class = serializers.WritingSystemSerializer
    filterset_fields = get_fields(models.WritingSystem, exclude=DEFAULT_FIELDS)


class WritingSystemWithDataViewSet(DynamicDepthViewSet):
    queryset = models.WritingSystem.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text')
    serializer_class = serializers.WritingSystemSerializer
    filterset_fields = get_fields(models.WritingSystem, exclude=DEFAULT_FIELDS)


class TagsWithDataViewSet(DynamicDepthViewSet):
    queryset = models.Tag.objects.all().filter(Q(surfaces__isnull=False) and Q(inscriptions__isnull=False)).order_by('text')
    serializer_class = serializers.InscriptionTagsSerializer
    filterset_fields = get_fields(models.Tag, exclude=DEFAULT_FIELDS)


class GenreDataViewSet(DynamicDepthViewSet):
    queryset = models.Genre.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text')
    serializer_class = serializers.GenreSerializer
    filterset_fields = get_fields(models.Tag, exclude=DEFAULT_FIELDS)


class ContributorsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS)
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('id')
        
        inscription_id = self.request.query_params.get('id')
        if inscription_id:
            inscriptions = queryset.filter(id=inscription_id)
            descriptions = models.Description.objects.all().filter(inscription__id=inscription_id)
            translations = models.Translation.objects.all().filter(inscription__id=inscription_id)
        else:
            inscriptions = queryset
            descriptions = models.Description.objects.all()
            translations = models.Translation.objects.all()
            
        inscription_serializer = serializers.InscriptionSerializer(inscriptions, many=True)
        description_serializer = serializers.DescriptionSerializer(descriptions, many=True)
        translation_serializer = serializers.TranslationSerializer(translations, many=True)
        
        formatted_data = []
        list_of_authors = []
        
        for inscription in inscription_serializer.data:    
            inscriptions_authors = inscription.get('author')
            for author_id in inscriptions_authors:
                list_of_authors.append(models.Author.objects.get(id = author_id))
                
        for description in description_serializer.data:
            description_authors = description.get('author')
            for author_id in description_authors:
                list_of_authors.append(models.Author.objects.get(id = author_id))
                
        for translation in translation_serializer.data:
            translation_authors = translation.get('author')
            for author_id in translation_authors:
                list_of_authors.append(models.Author.objects.get(id = author_id))
            
        list_of_authors = set(list_of_authors)
        authors_names = [f"{author.lastname} {author.firstname}" for author in list_of_authors]
        authors_names.sort()
        authors_ids = [author.id for author in list_of_authors]
        
        formatted_data = [
            {
                "authors_ordered": authors_names,
                "author_id": authors_ids
            }
        ]
        
        return Response(formatted_data)


class PanelViewSet(DynamicDepthViewSet):
    # this view is redundant and should be erased in a second time, unless specific fields need to be potrayed in here
    queryset = models.Panel.objects.all().order_by('title')
    serializer_class = serializers.PanelSerializer
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS+['geometry', 'spatial_position', 'spatial_direction'])


class PanelGeoViewSet(GeoViewSet):
    queryset = models.Panel.objects.all().order_by('id')
    serializer_class = serializers.PanelGeoSerializer
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS + ['geometry', 'spatial_position', 'spatial_direction'])
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True
    
    
class PanelMetadataViewSet(DynamicDepthViewSet):
    queryset = models.Panel.objects.all().order_by('title')
    serializer_class = serializers.PanelMetadataSerializer
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS+['geometry', 'spatial_position', 'spatial_direction'])

    
class PanelCoordinatesViewSet(GeoViewSet):
    serializer_class = serializers.PanelCoordinatesSerializer
    # queryset = models.Panel.objects.all().order_by('id')
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS + ['geometry', 'spatial_position', 'spatial_direction', 'published'])
    
    
    def get_queryset(self):
        queryset = models.Panel.objects.all().order_by('id')
        floor = self.request.query_params.get('floor')
        published = self.request.query_params.get('published')
        
        if published == 'true':
            if floor: 
                queryset = queryset.filter(Q(title__startswith=floor) & Q(published=True))
            else:
                queryset = queryset.filter(Q(published=True))
                
        if floor: 
            queryset = queryset.filter(title__startswith=floor)
                
        return queryset
    
    
class PanelInfoViewSet(DynamicDepthViewSet):

    serializer_class = serializers.PanelMetadataSerializer

    def list(self, request):
        # Filtering places 
        number_of_panels = models.Panel.objects.all().filter(published=True).count()
        panels = models.Panel.objects.all()
            
        panels_shown = panels.filter(published=True).count()
        hidden_panels = number_of_panels - panels_shown

        data = {
            'all_panels': number_of_panels,
            'shown_panels': panels_shown,
            'hidden_panels': hidden_panels,
        }

        return HttpResponse(json.dumps(data))
    
    
class PanelStringViewSet(DynamicDepthViewSet):
    serializer_class = serializers.PanelSerializer
    # queryset = models.Panel.objects.all().order_by('id')
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS + ['geometry', 'spatial_position', 'spatial_direction', 'published'])
    
    def get_queryset(self):
        queryset = models.Panel.objects.all().order_by('id')
        str = self.request.query_params.get('str')
        if str: 
            queryset = queryset.filter(title__startswith=str)
            
        return queryset
        
    
    
# class SurfaceTagsViewSet(DynamicDepthViewSet):
#     queryset = models.Panel.objects.all().order_by('title')
#     filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS+['geometry', 'spatial_position', 'spatial_direction'])
    
#     def list(self, request):
#         queryset = models.Panel.objects.all().order_by('title')
#         filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS+['geometry', 'spatial_position', 'spatial_direction'])
        
#         all_tags = models.Tag.objects.all()
        
#         surface = self.request.query_params.get('title')
        
#         if surface:
#              = queryset.filter(panel__title__contains = surface)
#         else:
#             inscriptions = queryset
        
#         serializer = serializers.InscriptionSerializer(inscriptions, many=True)
        
#         formatted_data = []
#         list_of_tags = []
#         for inscription in serializer.data:
            
#             tags = inscription.get('tags')
            
#             for tag_id in tags:
                
#                 selected_tag = all_tags.get(pk=tag_id)
                
#                 if selected_tag.text not in list_of_tags:
#                     data = {
#                         "tag_eng" : selected_tag.text,
#                         "tag_ukr" : selected_tag.text_ukr
#                     }
                    
#                     list_of_tags.append(selected_tag.text)
#                     formatted_data.append(data)
        
#         return Response(formatted_data)

    
class InscriptionViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()#.order_by('title')
    serializer_class = serializers.InscriptionSerializer
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS)
    

class InscriptionTagsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all().order_by('id')
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('id')
        filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
        
        all_tags = models.Tag.objects.all()
        
        surface = self.request.query_params.get('surface')
        
        if surface:
            inscriptions = queryset.filter(panel__title__contains = surface)
        else:
            inscriptions = queryset
        
        serializer = serializers.InscriptionSerializer(inscriptions, many=True)
        
        formatted_data = []
        list_of_tags = []
        for inscription in serializer.data:
            
            tags = inscription.get('tags')
            
            for tag_id in tags:
                
                selected_tag = all_tags.get(pk=tag_id)
                
                if selected_tag.text not in list_of_tags:
                    data = {
                        "tag_eng" : selected_tag.text,
                        "tag_ukr" : selected_tag.text_ukr
                    }
                    
                    list_of_tags.append(selected_tag.text)
                    formatted_data.append(data)
        
        return Response(formatted_data)
    
def inscription_contains_str(string, inscription):
    denomination = f"{inscription.panel.title}:{inscription.id}"
    # print(denomination, denomination.startswith(string))
    
    return denomination.startswith(string)


class InscriptionStringViewSet(DynamicDepthViewSet):
    serializer_class = serializers.InscriptionSerializer
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS + ['pixels'])
    
    def get_queryset(self):
        queryset = models.Inscription.objects.all()
        
        str = self.request.query_params.get('str')
        
        if str:
            ids_containing_str = [inscription.id for inscription in queryset if inscription_contains_str(str, inscription)] 
            queryset = queryset.filter(Q(id__in=ids_containing_str) | Q(title__startswith=str))
            
        return queryset 
    
    
class AnnotationViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all().order_by('id')
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('id')
        filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
        
        surface = self.request.query_params.get('surface')
        
        if surface:
            annotations = queryset.filter(panel__title = surface)
        else:
            annotations = queryset
        
        serializer = serializers.InscriptionSerializer(annotations, many=True)
        
        list_to_return = []
        for annotation in serializer.data:
            pct_position = annotation.get('position_on_surface')
            if pct_position is not None:
                pct_to_percent_string = pct_position.replace("pct", "percent")
            else:
                pct_to_percent_string = ""
            data = {
                "type": "Annotation",
                "body": [
                    {"value": f"Inscription {annotation.get('panel')}:{annotation.get('id')}"} # 
                ],
                "target": {
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                        "value": f"xywh={pct_to_percent_string}"
                    }
                },
                "id": annotation.get('id')
            }
            list_to_return.append(data)
        
        return Response(list_to_return)

    
class IIIFImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    
    # queryset = models.Image.objects.all().order_by('id')
    serializer_class = serializers.TIFFImageSerializer
    filterset_fields = get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])
    
    def get_queryset(self):
        orthophotos = models.Image.objects.all().filter(type_of_image__text="Orthophoto")
        topography = models.Image.objects.all().filter(type_of_image__text="Topography")
        topography_blended = topography.filter(file__contains="blended_map")
        topography_texture = topography.filter(file__contains="texture_map")
        topography_normal = topography.filter(file__contains="normal_map")
        
        custom_order = Case(
            When(type_of_image__text="Orthophoto", then=Value(1)),
            When(file__contains="blended_map", then=Value(2)),
            When(file__contains="texture_map", then=Value(3)),
            When(file__contains="normal_map", then=Value(4))
        )
        
        queryset = (orthophotos | topography_blended | topography_texture | topography_normal).annotate(custom_order=custom_order).order_by('custom_order')
        
        return queryset
    
    
    
class ObjectRTIViewSet(DynamicDepthViewSet):
    queryset = models.ObjectRTI.objects.all().order_by('id')
    serializer_class = serializers.ObjectRTISerializer
    filterset_fields = get_fields(models.ObjectRTI, exclude=DEFAULT_FIELDS)
    
    
class ObjectRTIViewSet(DynamicDepthViewSet):
    queryset = models.ObjectMesh3D.objects.all().order_by('id')
    serializer_class = serializers.ObjectMesh3DSerializer
    filterset_fields = get_fields(models.ObjectMesh3D, exclude=DEFAULT_FIELDS)
    
   
# class TranslationViewSet(DynamicDepthViewSet):
#     queryset = models.Translation.objects.all().order_by('id')
#     serializer_class = serializers.TranslationSerializer
#     filterset_fields = get_fields(models.Translation, exclude=DEFAULT_FIELDS) 


# class DescriptionViewSet(DynamicDepthViewSet):
#     queryset = models.Description.objects.all().order_by('id')
#     serializer_class = serializers.DescriptionSerializer 
#     filterset_fields = get_fields(models.Description, exclude=DEFAULT_FIELDS) 