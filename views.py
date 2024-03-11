from unittest.mock import DEFAULT
from . import models, serializers
from django.db.models import Q, Value, Case, When
from saintsophia.abstract.views import DynamicDepthViewSet, GeoViewSet
from saintsophia.abstract.models import get_fields, DEFAULT_FIELDS
# from django.db.models import Q
from django.http import HttpResponse
import json
import django_filters


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
        # Query Parameters 
        # with_3D = self.request.query_params.get('with_3D')
        # with_plan = self.request.query_params.get('with_plan')
        # period = self.request.query_params.get('epoch')
        # necropolis = self.request.query_params.get('necropolis')
        # type_of_tomb = self.request.query_params.get('type')

        # Filtering places 
        number_of_panels = models.Panel.objects.all().filter(published=True).count()
        panels = models.Panel.objects.all()
            
        panels_shown = panels.filter(published=True).count()
        hidden_panels = number_of_panels - panels_shown

        # plans_count =  panels.filter(id__in=list(
        #                     models.Image.objects.filter(Q(type_of_image__text__icontains="floor plan") 
        #                                               | Q (type_of_image__text__icontains="section"))
        #                                                 .values_list('tomb', flat=True))).count()
        
        # photographs_count = places.filter(id__in=list(
        #                     models.Image.objects.filter(type_of_image__text__icontains="photograph").values_list('tomb', flat=True))
        #                     ).count()
        

        # threedhop_count = places.filter(id__in=list(models.Object3DHop.objects.all().values_list('tomb', flat=True))).count()
        # pointcloud_count = places.filter(id__in=list(models.ObjectPointCloud.objects.all().values_list('tomb', flat=True))).count()
        # objects_3d = threedhop_count + pointcloud_count
        
        data = {
            'all_panels': number_of_panels,
            'shown_panels': panels_shown,
            'hidden_panels': hidden_panels,
        }

        return HttpResponse(json.dumps(data))
    
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