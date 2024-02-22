from django.urls import path, include
from rest_framework import routers
from . import views
import saintsophia.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("inscriptions")
documentation = utils.build_app_api_documentation("inscriptions", endpoint)

router.register(rf'{endpoint}/geojson/panel', views.PanelGeoViewSet, basename='panel with geojson coordinates')
router.register(rf'{endpoint}/panel', views.PanelViewSet, basename='panels information')
router.register(rf'{endpoint}/panel-metadata', views.PanelMetadataViewSet, basename='panels metadata')
router.register(rf'{endpoint}/coordinates', views.PanelCoordinatesViewSet, basename='panels coordinates')
router.register(rf'{endpoint}/image', views.IIIFImageViewSet, basename='image')
router.register(rf'{endpoint}/object-rti', views.ObjectRTIViewSet, basename='object RTI')
router.register(rf'{endpoint}/object-mesh-3d', views.ObjectRTIViewSet, basename='object Mesh 3D')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('inscriptions', endpoint, 
        exclude=['panel', 'image', 'objectrti', 'objectmesh3d']),

    *utils.get_model_urls('inscriptions', f'{endpoint}', exclude=['panel', 'image', 'objectrti', 'objectmesh3d']),
    *documentation
]
