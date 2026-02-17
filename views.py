from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q, Value, Case, When, Count, F, IntegerField, Func, TextField
from django.db.models.functions import Cast
from saintsophia.abstract.views import DynamicDepthViewSet, GeoViewSet
from saintsophia.abstract.models import get_fields, DEFAULT_FIELDS
from django.http import HttpResponse
from django.utils.html import strip_tags
import html as html_module
import json
import django_filters
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class StripHTML(Func):
    """PostgreSQL function to strip HTML tags from a text field using REGEXP_REPLACE."""
    function = 'REGEXP_REPLACE'
    template = "%(function)s(COALESCE(%(expressions)s, ''), '<[^>]*>', '', 'g')"
    output_field = TextField()


# RichText fields on Inscription that are searched with free-text queries
_RICH_TEXT_FIELDS = [
    'transcription', 'interpretative_edition', 'romanisation',
    'translation_eng', 'translation_ukr',
]


def _annotate_clean_fields(queryset):
    """Annotate the queryset with HTML-stripped versions of RichText fields."""
    annotations = {f'clean_{f}': StripHTML(f) for f in _RICH_TEXT_FIELDS}
    return queryset.annotate(**annotations)


def _to_html_entities(text):
    """Convert a Unicode string to its HTML named-entity equivalent.
    
    CKEditor stores Greek / Cyrillic / other non-ASCII text as HTML named
    entities (e.g. &delta;&omicron;&upsilon;...).  To let users search in
    their native script we convert the search term to the same form so we
    can match against the raw DB content as well.
    """
    return ''.join(
        f'&{html_module.entities.codepoint2name[ord(ch)]};'
        if ord(ch) in html_module.entities.codepoint2name
        else ch
        for ch in text
    )


def _build_search_q(search_term):
    """Build a Q filter that searches plain-text fields normally and RichText
    fields via both the Unicode search term AND its HTML-entity equivalent
    so that Greek / Church Slavonic / etc. characters match the entity-encoded
    content stored by CKEditor."""
    entity_term = _to_html_entities(search_term)

    # For plain-text fields just use the original term
    q = (
        Q(title__icontains=search_term) |
        Q(panel__title__icontains=search_term) |
        Q(mentioned_person__name__icontains=search_term) |
        Q(korniienko_image__title__icontains=search_term)
    )

    # For RichText fields search both the Unicode term (against the
    # tag-stripped annotation) AND the entity-encoded term (against the raw
    # DB column) so we cover both storage styles.
    for field in _RICH_TEXT_FIELDS:
        q |= Q(**{f'clean_{field}__icontains': search_term})
        if entity_term != search_term:
            q |= Q(**{f'{field}__icontains': entity_term})

    return q


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
    filterset_fields = get_fields(models.Genre, exclude=DEFAULT_FIELDS)


class BibliographyItemViewSet(DynamicDepthViewSet):
    queryset = models.BibliographyItem.objects.all().order_by('year')
    serializer_class = serializers.BibliographyItemSerializer
    filterset_fields = get_fields(models.BibliographyItem, exclude=DEFAULT_FIELDS)


class ContributorsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()
    serializer_class = serializers.InscriptionSerializer
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
    queryset = models.Panel.objects.all()  
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
    # Custom filters for panel-related fields to allow simple parameter names
    medium = django_filters.NumberFilter(field_name='panel__medium__id', lookup_expr='exact')
    material = django_filters.NumberFilter(field_name='panel__material__id', lookup_expr='exact')
    panel_title_str = django_filters.CharFilter(field_name='panel__title', lookup_expr='startswith')
    inscription_title_str = django_filters.CharFilter(field_name='title', lookup_expr='startswith')

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


# Search by multiple text fields as well as  korniienko number and panel title
class SearchInscriptionViewSet(DynamicDepthViewSet):
    serializer_class = serializers.InscriptionSerializer

    def get_queryset(self):
        queryset = _annotate_clean_fields(models.Inscription.objects.all())
        search_term = self.request.query_params.get('q', None)
        
        if search_term:
            queryset = queryset.filter(
                _build_search_q(search_term)
            ).order_by('korniienko_image__title')

        return queryset.distinct()
    
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = InscriptionFilter

class AutoCompleteInscriptionViewSet(ViewSet):
    """
        Returns inscriptions that start with a given string based on search fields, 
        for autocomplete purposes.
        We also need to add ids to be able to link the suggestions to the actual inscription.
        """

    def list(self, request, *args, **kwargs):
        q = request.query_params.get('q')
        if not q:
            return Response([])

        q = q.strip().lower()
        if not q:
            return Response([])
    
        limit = 10  # Limit the number of results for autocomplete
        suggestions = {}  # (value, source) -> set(ids)
        entity_q = _to_html_entities(q)

        def add_suggestions(filtered_qs, label):
            seen = set()
            for row in filtered_qs:
                if not row:
                    continue
                value, inscription_id = row
                if value:
                    val_str = html_module.unescape(strip_tags(str(value))).strip()
                    val_key = val_str.lower()
                    if q in val_key and val_key not in seen:
                        key = (val_str, label)
                        suggestions.setdefault(key, set()).add(inscription_id)
                        seen.add(val_key)

        # Search in various fields, using both Unicode and HTML-entity forms for RichText fields
        inscriptions = _annotate_clean_fields(models.Inscription.objects.all())
        add_suggestions(
            inscriptions.filter(title__icontains=q).values_list('title', 'id').distinct()[:limit],
            'Title'
        )
        add_suggestions(
            inscriptions.filter(panel__title__icontains=q).values_list('panel__title', 'id').distinct()[:limit],
            'Panel Title'
        )

        # RichText fields: search with clean annotation (Unicode) OR raw field (entity-encoded)
        for field, label in [
            ('transcription', 'Transcription'),
            ('interpretative_edition', 'Interpretative Edition'),
            ('romanisation', 'Romanisation'),
            ('translation_eng', 'Translation (ENG)'),
            ('translation_ukr', 'Translation (UKR)'),
        ]:
            clean = f'clean_{field}'
            filt = Q(**{f'{clean}__icontains': q})
            if entity_q != q:
                filt |= Q(**{f'{field}__icontains': entity_q})
            add_suggestions(
                inscriptions.filter(filt).values_list(clean, 'id').distinct()[:limit],
                label,
            )

        add_suggestions(
            inscriptions.filter(mentioned_person__name__icontains=q).values_list('mentioned_person__name', 'id').distinct()[:limit],
            'Mentioned Person'
        )
        add_suggestions(
            inscriptions.filter(korniienko_image__title__icontains=q).values_list('korniienko_image__title', 'id').distinct()[:limit],
            'Korniienko Image Title'
        )   

        # Limit the total number of suggestions
                # duplicate and sort
        sorted_suggestions = sorted(
            [
                {
                    "value": value,
                    "source": source,
                    "ids": sorted(list(ids)),
                    # **({"id": next(iter(ids))} if len(ids) == 1 else {})
                }
                for (value, source), ids in suggestions.items()
            ],
            key=lambda x: x["value"]
        )[:20]

        return Response(sorted_suggestions)


class InscriptionTagsViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all().order_by('id')
    serializer_class = serializers.InscriptionSerializer  # Add this line
    filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
    
    def list(self, request):
        queryset = models.Inscription.objects.all().order_by('id')
        filterset_fields = get_fields(models.Inscription, exclude=DEFAULT_FIELDS+['pixels'])
        
        all_tags = models.Tag.objects.all().order_by('text')
        
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
    serializer_class = serializers.InscriptionSerializer
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
    

class KorniienkoImageViewSet(DynamicDepthViewSet):
    queryset = models.KorniienkoImage.objects.all().order_by('id')
    serializer_class = serializers.KorniienkoImageSerializer
    filterset_fields = get_fields(models.KorniienkoImage, exclude=DEFAULT_FIELDS)
    
    
class ObjectRTIViewSet(DynamicDepthViewSet):
    queryset = models.ObjectRTI.objects.all().order_by('id')
    serializer_class = serializers.ObjectRTISerializer
    filterset_fields = get_fields(models.ObjectRTI, exclude=DEFAULT_FIELDS)
    
    
class ObjectMesh3DViewSet(DynamicDepthViewSet):
    queryset = models.ObjectMesh3D.objects.all().order_by('id')
    serializer_class = serializers.ObjectMesh3DSerializer
    filterset_fields = get_fields(models.ObjectMesh3D, exclude=DEFAULT_FIELDS)


class DataWidgetViewSet(DynamicDepthViewSet):
    queryset = models.Inscription.objects.all()
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
            inscriptions = inscriptions.filter(title__startswith=inscription_title_str)

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

        return HttpResponse(json.dumps(data), content_type='application/json')

class SearchDataWidgetViewSet(DynamicDepthViewSet):
    """ 
        Same as DataWidgetViewSet but includes search parameters including:
        transcription, interpretative edition, romanisation, translations, 
        mentioned person and korniienko image title. 
        This is to be used for the search widget
    """
    queryset = models.Inscription.objects.all()
    serializer_class = serializers.InscriptionSerializer

    def list(self, request, *args, **kwargs): 
        # Query Parameters
        q = (self.request.query_params.get('q') or '').strip()

        # Base filter widget parameters
        filter_mapping = {
            'type_of_inscription': 'type_of_inscription__id__exact',
            'writing_system': 'writing_system__id__exact',
            'genre': 'genre__id__exact',
            'tags': 'tags__id__exact',
            'language': 'language__id__exact',
            'panel': 'panel__id__exact',
            'id': 'id',
            'medium': 'panel__medium__id__exact',
            'material': 'panel__material__exact',
            'alignment': 'alignment__id__exact',
            'condition': 'condition__id__exact',
            'mentioned_person': 'mentioned_person__id__exact',
            'panel_title_str': 'panel__title__startswith',
            'inscription_title_str': 'title__startswith',
        }

        # Exact item selection parameters from autocomplete
        search_mapping = {
            'title': 'title__icontains',
            'panel': 'panel__title__icontains',
            'transcription': 'transcription__icontains',
            'interpretative_edition': 'interpretative_edition__icontains',
            'romanisation': 'romanisation__icontains',
            'translation_eng': 'translation_eng__icontains',
            'translation_ukr': 'translation_ukr__icontains',
            'mentioned_person_name': 'mentioned_person__name__icontains',
            'korniienko_image_title': 'korniienko_image__title__icontains',
        }

        count_all_inscriptions = models.Inscription.objects.count()
        inscriptions = _annotate_clean_fields(models.Inscription.objects.all())

        for param, lookup in filter_mapping.items():
            value = self.request.query_params.get(param)
            if value:
                inscriptions = inscriptions.filter(**{lookup: value})

        # Two autocomplete modes:
        # 1) q provided => partial text search across supported fields.
        # 2) no q => exact field matching for selected autocomplete item(s).
        if q:
            inscriptions = inscriptions.filter(_build_search_q(q))
        else:
            for param, lookup in search_mapping.items():
                value = self.request.query_params.get(param)
                if value:
                    inscriptions = inscriptions.filter(**{lookup: value})

        inscriptions = inscriptions.distinct()

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
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/json')

class SummaryViewSet(DynamicDepthViewSet):
    """A separate viewset to return summary data for inscriptions."""
    queryset = models.Inscription.objects.all()
    serializer_class = serializers.SummarySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = InscriptionFilter  # Use the same filter as InscriptionViewSet

    def list(self, request, *args, **kwargs):
        # Query Parameters (matching DataWidgetViewSet exactly)
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

        # Filtering inscriptions (matching DataWidgetViewSet exactly)
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
            inscriptions = inscriptions.filter(title__startswith=inscription_title_str)

        # Generate summary with filtered inscriptions
        summary_data = self.summarize_results(inscriptions)
        
        return Response(summary_data)
    

    def summarize_results(self, queryset):
        """Summarizes search results by creator and institution."""

        summary = {
            "type_of_inscription": [],
            "writing_system": [],
            "language": [],
            "textual_genre": [],
            "pictorial_description": [],
            "min_year": [],
            "max_year": [],
            "avg_year": [],
        }

        # Count images per creator
        type_of_inscription_counts = (
            queryset
            .values("type_of_inscription__text", "type_of_inscription__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        # Count images per institution
        writing_system_counts = (
            queryset
            .values("writing_system__text", "writing_system__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Count of documentation types by site
        language_counts = (
            queryset
            .values("language__text", "language__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Summarise search results by motif type
        textual_genre_counts = (
            queryset
            .values("genre__text", "genre__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Show number of images for each year 
        pictorial_description_counts = (
            queryset
            .values("tags__text", "tags__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        min_year_counts = (
            queryset
            .values("min_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        max_year_counts = (
            queryset
            .values("max_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        # Calculate average year and group by it
        avg_year_counts = (
            queryset
            .filter(min_year__isnull=False, max_year__isnull=False, max_year__lte=F('min_year') + 200)  # Only include records with both years
            .annotate(
                avg_year=Cast((F('min_year') + F('max_year')) / 2, IntegerField())
            )
            .values("avg_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("avg_year")
        )

        # Format summary
        summary["type_of_inscription"] = [
            {
                "type": entry["type_of_inscription__text"], 
                "type_ukr": entry["type_of_inscription__text_ukr"], 
                "count": entry["count"]}
            for entry in type_of_inscription_counts if entry["type_of_inscription__text"]
        ]

        summary["writing_system"] = [
            {
                "writing_system": entry["writing_system__text"], 
                "writing_system_ukr": entry["writing_system__text_ukr"],
                "count": entry["count"]}
            for entry in writing_system_counts if entry["writing_system__text"]
        ]   

        summary["language"] = [
            {
                "language": entry["language__text"], 
                "language_ukr": entry["language__text_ukr"],
                "count": entry["count"]}
            for entry in language_counts if entry["language__text"]
        ]

        summary["textual_genre"] = [
            {
                "textual_genre": entry["genre__text"], 
                "textual_genre_ukr": entry["genre__text_ukr"],
                "count": entry["count"]}
            for entry in textual_genre_counts if entry["genre__text"]
        ]

        summary["pictorial_description"] = [
            {
                "pictorial_description": entry["tags__text"], 
                "pictorial_description_ukr": entry["tags__text_ukr"],
                "count": entry["count"]}
            for entry in pictorial_description_counts if entry["tags__text"]
        ]

        summary["min_year"] = [
            {"min_year": entry["min_year"], "count": entry["count"]}
            for entry in min_year_counts if entry["min_year"]
        ]

        summary["max_year"] = [
            {"max_year": entry["max_year"], "count": entry["count"]}
            for entry in max_year_counts if entry["max_year"]
        ]

        summary["avg_year"] = [
            {"avg_year": entry["avg_year"], "count": entry["count"]}
            for entry in avg_year_counts if entry["avg_year"] is not None
        ]

        return summary
    

class DataSummaryViewSet(DynamicDepthViewSet):
    """A viewset to return summary data."""
    queryset = models.Inscription.objects.all()
    serializer_class = serializers.SummarySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = InscriptionFilter  # Use the same filter as InscriptionViewSet

    def list(self, request, *args, **kwargs): 
        # Query Parameters
        q = (self.request.query_params.get('q') or '').strip()

        # Base filter widget parameters
        filter_mapping = {
            'type_of_inscription': 'type_of_inscription__id__exact',
            'writing_system': 'writing_system__id__exact',
            'genre': 'genre__id__exact',
            'tags': 'tags__id__exact',
            'language': 'language__id__exact',
            'panel': 'panel__id__exact',
            'id': 'id',
            'medium': 'panel__medium__id__exact',
            'material': 'panel__material__exact',
            'alignment': 'alignment__id__exact',
            'condition': 'condition__id__exact',
            'mentioned_person': 'mentioned_person__id__exact',
            'panel_title_str': 'panel__title__startswith',
            'inscription_title_str': 'title__startswith',
        }

        # Exact item selection parameters from autocomplete
        search_mapping = {
            'title': 'title__icontains',
            'panel': 'panel__title__icontains',
            'transcription': 'transcription__icontains',
            'interpretative_edition': 'interpretative_edition__icontains',
            'romanisation': 'romanisation__icontains',
            'translation_eng': 'translation_eng__icontains',
            'translation_ukr': 'translation_ukr__icontains',
            'mentioned_person_name': 'mentioned_person__name__icontains',
            'korniienko_image_title': 'korniienko_image__title__icontains',
        }

        # Filtering inscriptions (matching DataWidgetViewSet exactly)
        inscriptions = _annotate_clean_fields(models.Inscription.objects.all())
        for param, lookup in filter_mapping.items():
            value = self.request.query_params.get(param)
            if value:
                inscriptions = inscriptions.filter(**{lookup: value})
        # Two autocomplete modes:
        # 1) q provided => partial text search across supported fields.
        # 2) no q => exact field matching for selected autocomplete item(s).
        if q:
            inscriptions = inscriptions.filter(_build_search_q(q))
        else:
            for param, lookup in search_mapping.items():
                value = self.request.query_params.get(param)
                if value:
                    inscriptions = inscriptions.filter(**{lookup: value})
        inscriptions = inscriptions.distinct()
        # Generate summary with filtered inscriptions
        summary_data = self.summarize_results(inscriptions)
        
        return Response(summary_data)
    
    def summarize_results(self, queryset):
        """Summarizes search results by creator and institution."""

        summary = {
            "type_of_inscription": [],
            "writing_system": [],
            "language": [],
            "textual_genre": [],
            "pictorial_description": [],
            "min_year": [],
            "max_year": [],
            "avg_year": [],
        }

        # Count images per creator
        type_of_inscription_counts = (
            queryset
            .values("type_of_inscription__text", "type_of_inscription__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        # Count images per institution
        writing_system_counts = (
            queryset
            .values("writing_system__text", "writing_system__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Count of documentation types by site
        language_counts = (
            queryset
            .values("language__text", "language__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Summarise search results by motif type
        textual_genre_counts = (
            queryset
            .values("genre__text", "genre__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        # Show number of images for each year 
        pictorial_description_counts = (
            queryset
            .values("tags__text", "tags__text_ukr")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        min_year_counts = (
            queryset
            .values("min_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )
        max_year_counts = (
            queryset
            .values("max_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("-count")
        )

        # Calculate average year and group by it
        avg_year_counts = (
            queryset
            .filter(min_year__isnull=False, max_year__isnull=False, max_year__lte=F('min_year') + 200)  # Only include records with both years
            .annotate(
                avg_year=Cast((F('min_year') + F('max_year')) / 2, IntegerField())
            )
            .values("avg_year")
            .annotate(count=Count("id", distinct=True))
            .order_by("avg_year")
        )   

        # Format summary
        summary["type_of_inscription"] = [
            {
                "type": entry["type_of_inscription__text"], 
                "type_ukr": entry["type_of_inscription__text_ukr"], 
                "count": entry["count"]}
            for entry in type_of_inscription_counts if entry["type_of_inscription__text"]
        ]   
        summary["writing_system"] = [
            {
                "writing_system": entry["writing_system__text"], 
                "writing_system_ukr": entry["writing_system__text_ukr"],
                "count": entry["count"]}
            for entry in writing_system_counts if entry["writing_system__text"]
        ]   
        summary["language"] = [
            {
                "language": entry["language__text"], 
                "language_ukr": entry["language__text_ukr"],
                "count": entry["count"]}
            for entry in language_counts if entry["language__text"]
        ]
        summary["textual_genre"] = [
            {
                "textual_genre": entry["genre__text"], 
                "textual_genre_ukr": entry["genre__text_ukr"],
                "count": entry["count"]}
            for entry in textual_genre_counts if entry["genre__text"]
        ]
        summary["pictorial_description"] = [
            {
                "pictorial_description": entry["tags__text"], 
                "pictorial_description_ukr": entry["tags__text_ukr"],
                "count": entry["count"]}
            for entry in pictorial_description_counts if entry["tags__text"]
        ]
        summary["min_year"] = [
            {"min_year": entry["min_year"], "count": entry["count"]}
            for entry in min_year_counts if entry["min_year"]
        ]
        summary["max_year"] = [
            {"max_year": entry["max_year"], "count": entry["count"]}
            for entry in max_year_counts if entry["max_year"]
        ]
        summary["avg_year"] = [
            {"avg_year": entry["avg_year"], "count": entry["count"]}
            for entry in avg_year_counts if entry["avg_year"] is not None
        ]       
        return summary