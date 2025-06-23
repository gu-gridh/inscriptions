from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q, Value, Case, When
from saintsophia.abstract.views import DynamicDepthViewSet, GeoViewSet
from saintsophia.abstract.models import get_fields, DEFAULT_FIELDS
from django.http import HttpResponse
import json
import django_filters
from rest_framework.response import Response


class TagViewSet(DynamicDepthViewSet):
    queryset = models.Tag.objects.all().order_by('text').distinct()
    serializer_class = serializers.InscriptionTagsSerializer
    filterset_fields = get_fields(models.Tag, exclude=DEFAULT_FIELDS)


class LanguageViewSet(DynamicDepthViewSet):
    queryset = models.Language.objects.all().order_by('text').distinct()
    serializer_class = serializers.LanguageSerializer
    filterset_fields = get_fields(models.Language, exclude=DEFAULT_FIELDS)


class LanguageWithDataViewSet(DynamicDepthViewSet):
    queryset = models.Language.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text').distinct()
    serializer_class = serializers.LanguageSerializer
    filterset_fields = get_fields(models.Language, exclude=DEFAULT_FIELDS)
    

class WritingSystemViewSet(DynamicDepthViewSet):
    queryset = models.WritingSystem.objects.all().order_by('text').distinct()
    serializer_class = serializers.WritingSystemSerializer
    filterset_fields = get_fields(models.WritingSystem, exclude=DEFAULT_FIELDS)


class WritingSystemWithDataViewSet(DynamicDepthViewSet):
    queryset = models.WritingSystem.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text').distinct()
    serializer_class = serializers.WritingSystemSerializer
    filterset_fields = get_fields(models.WritingSystem, exclude=DEFAULT_FIELDS)


class HistoricalPersonViewSet(DynamicDepthViewSet):
    queryset = models.HistoricalPerson.objects.all().order_by('name').distinct()
    serializer_class = serializers.HistoricalPersonSerializer
    filterset_fields = get_fields(models.HistoricalPerson, exclude=DEFAULT_FIELDS)


class TagsWithDataViewSet(DynamicDepthViewSet):
    queryset = models.Tag.objects.all().filter(Q(surfaces__isnull=False) and Q(inscriptions__isnull=False)).order_by('text').distinct()
    serializer_class = serializers.InscriptionTagsSerializer
    filterset_fields = get_fields(models.Tag, exclude=DEFAULT_FIELDS)


class GenreDataViewSet(DynamicDepthViewSet):
    queryset = models.Genre.objects.all().filter(Q(inscriptions__isnull=False)).order_by('text').distinct()
    serializer_class = serializers.GenreSerializer
    filterset_fields = get_fields(models.Tag, exclude=DEFAULT_FIELDS)


class ContributorsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS)
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('title')
        
        inscription_id = self.request.query_params.get('id')
        if inscription_id:
            inscriptions = queryset.filter(id=inscription_id)
        else:
            inscriptions = queryset

        inscription_serializer = serializers.InscriptionSerializer(inscriptions, many=True)
        
        formatted_data = []
        list_of_authors = []
        
        for inscription in inscription_serializer.data:    
            inscriptions_authors = inscription.get('author')
            for author_id in inscriptions_authors:
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
    queryset = models.Panel.objects.all().order_by('title')
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
        queryset = models.Panel.objects.all().order_by('title')
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
    filterset_fields = get_fields(models.Panel, exclude=DEFAULT_FIELDS + ['geometry', 'spatial_position', 'spatial_direction', 'published'])
    
    def get_queryset(self):
        queryset = models.Panel.objects.all().order_by('id')
        str = self.request.query_params.get('str')
        if str: 
            queryset = queryset.filter(title__startswith=str)
            
        return queryset


class InscriptionFilter(django_filters.FilterSet):
    # panel__title = django_filters.CharFilter()

    class Meta:
        model = models.Inscription
        fields = {
            'id': ['exact'],
            'title': ['exact', 'icontains', 'startswith'],
            'panel': ['exact'],
            'panel__title': ['exact', 'icontains', 'startswith'],
            'panel__material': ['exact'],
            'panel__medium': ['exact'],
            'type_of_inscription': ['exact'],
            'genre': ['exact'],
            'tags': ['exact'],
            'elevation': ['exact', 'gt', 'lt'],
            'height': ['exact', 'gt', 'lt'],
            'width': ['exact', 'gt', 'lt'],
            'language': ['exact'],
            'writing_system': ['exact'],
            'min_year': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'max_year': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'dating_criteria': ['exact'],
            'transcription': ['icontains'],
            'interpretative_edition': ['icontains'],
            'romanisation': ['icontains'],
            'mentioned_person': ['exact'],
            'inscriber': ['exact'],
            'condition': ['exact'],
            'alignment': ['exact'],
            'extra_alphabetical_sign': ['exact'],
            'author': ['exact'],
        }

    
class InscriptionViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()#.order_by('title')
    serializer_class = serializers.InscriptionSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = InscriptionFilter
    # filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS)
    

class InscriptionTagsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all().order_by('id')
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('id')
        filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
        
        all_tags = models.Tag.objects.all().order_by('title')
        
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


class ImageFilter(django_filters.FilterSet):
    # panel__title = django_filters.CharFilter()

    class Meta:
        model = models.Image
        fields = {
            'id': ['exact'],
            'panel': ['exact'],
            'type_of_image': ['exact'],
            'panel__title': ['exact', 'icontains', 'startswith'],
            'panel__material': ['exact'],
            'panel__medium': ['exact'],
        }


class IIIFImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    
    serializer_class = serializers.TIFFImageSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ImageFilter
    # filterset_fields = get_fields(models.Image, exclude=DEFAULT_FIELDS + ['iiif_file', 'file']) + ['panel__medium', 'panel__material']
    
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
    

class GenericImageViewSet(DynamicDepthViewSet):
    """
    retrieve:
    Returns a single image instance.

    list:
    Returns a list of all the existing images in the database, paginated.

    count:
    Returns a count of the existing images after the application of any filter.
    """
    queryset = models.GenericImage.objects.all().order_by('id')
    serializer_class = serializers.TIFFImageSerializer
    filterset_fields = get_fields(models.GenericImage, exclude=DEFAULT_FIELDS + ['iiif_file', 'file'])
    
    
class ObjectRTIViewSet(DynamicDepthViewSet):
    queryset = models.ObjectRTI.objects.all().order_by('id')
    serializer_class = serializers.ObjectRTISerializer
    filterset_fields = get_fields(models.ObjectRTI, exclude=DEFAULT_FIELDS)
    
    
class ObjectMesh3DViewSet(DynamicDepthViewSet):
    queryset = models.ObjectMesh3D.objects.all().order_by('id')
    serializer_class = serializers.ObjectMesh3DSerializer
    filterset_fields = get_fields(models.ObjectMesh3D, exclude=DEFAULT_FIELDS)


class DataWidgetViewSet(DynamicDepthViewSet):

    serializer_class = serializers.InscriptionSerializer

    def list(self, request):
        # Query Parameters 
        type_of_inscription = self.request.query_params.get('type_of_inscription')
        writing_system = self.request.query_params.get('writing_system')
        textual_genre = self.request.query_params.get('genre')
        pictorial_description = self.request.query_params.get('tags')
        language = self.request.query_params.get('language')
        surface_id = self.request.query_params.get('panel')
        inscription_id = self.request.query_params.get('id')
        medium = self.request.query_params.get('medium')
        material = self.request.query_params.get('material')
        alignment = self.request.query_params.get('alignment')
        condition = self.request.query_params.get('condition')
        mentioned_person = self.request.query_params.get('mentioned_person')
        panel_title_str = self.request.query_params.get('panel_title_str')
        inscription_title_str = self.request.query_params.get('inscription_title_str')

        # Filtering places 
        count_all_inscriptions = models.Inscription.objects.all().count()
        inscriptions = models.Inscription.objects.all()
        
        if type_of_inscription:
            inscriptions = inscriptions.filter(Q(type_of_inscription__id__exact=type_of_inscription))
        
        if writing_system:
            inscriptions = inscriptions.filter(writing_system__id__exact=writing_system)
        
        if textual_genre:
            inscriptions = inscriptions.filter(genre__id__exact=textual_genre)

        if pictorial_description:
            inscriptions = inscriptions.filter(tags__id__exact=pictorial_description)

        if language:
            inscriptions = inscriptions.filter(language__id__exact=language)

        if surface_id:
            inscriptions = inscriptions.filter(panel__id__exact=surface_id)

        if inscription_id:
            inscriptions = inscriptions.filter(id=inscription_id)

        if medium:
            inscriptions = inscriptions.filter(panel__medium__id__exact=medium)
        
        if material:
            inscriptions = inscriptions.filter(panel__material__exact=material)

        if alignment:
            inscriptions = inscriptions.filter(alignment__id__exact=alignment)

        if condition:
            inscriptions = inscriptions.filter(condition__id__exact=condition)

        if mentioned_person:
            inscriptions = inscriptions.filter(mentioned_person__id__exact=mentioned_person)

        if panel_title_str:
            inscriptions = inscriptions.filter(panel__title__startswith=panel_title_str)

        if inscription_title_str:
            inscriptions = inscriptions.filter(title__startswith=inscription_contains_str)

        count_inscriptions_shown = inscriptions.all().count()
        count_hidden_inscriptions = count_all_inscriptions -  count_inscriptions_shown

        count_textual_inscriptions = inscriptions.filter(type_of_inscription__id__exact=1).count() # 1 is for textual inscriptions
        count_pictorial_inscriptions = inscriptions.filter(type_of_inscription__id__exact=2).count() # 2 is for textual inscriptions
        count_composite_inscriptions = inscriptions.filter(type_of_inscription__id__exact=3).count() # 3 is for textual inscriptions
        
        data = {
            'all_inscriptions': count_all_inscriptions,
            'shown_inscriptions': count_inscriptions_shown,
            'hidden_inscriptions': count_hidden_inscriptions,
            'textual_inscriptions': count_textual_inscriptions,
            'pictorial_inscriptions': count_pictorial_inscriptions,
            'composites_inscriptions': count_composite_inscriptions
        }

        return HttpResponse(json.dumps(data))