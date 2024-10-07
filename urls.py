from django.urls import path, include
from rest_framework import routers
from . import views
import saintsophia.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("inscriptions")
documentation = utils.build_app_api_documentation("inscriptions", endpoint)

router.register(rf'{endpoint}/language', views.LanguageViewSet, basename='languages')
router.register(rf'{endpoint}/writing-system', views.WritingSystemViewSet, basename='writing systems')
router.register(rf'{endpoint}/geojson/panel', views.PanelGeoViewSet, basename='panel with geojson coordinates')
router.register(rf'{endpoint}/panel', views.PanelViewSet, basename='panels information')
router.register(rf'{endpoint}/panel-metadata', views.PanelMetadataViewSet, basename='panels metadata')
router.register(rf'{endpoint}/coordinates', views.PanelCoordinatesViewSet, basename='panels coordinates')
router.register(rf'{endpoint}/info/panels', views.PanelInfoViewSet, basename='panels info')
router.register(rf'{endpoint}/panel-string', views.PanelStringViewSet, basename='panels beginning by string')
router.register(rf'{endpoint}/image', views.IIIFImageViewSet, basename='image')
router.register(rf'{endpoint}/object-rti', views.ObjectRTIViewSet, basename='object RTI')
router.register(rf'{endpoint}/object-mesh-3d', views.ObjectRTIViewSet, basename='object Mesh 3D')
router.register(rf'{endpoint}/inscription', views.InscriptionViewSet, basename='inscription')
router.register(rf'{endpoint}/inscription-string', views.InscriptionStringViewSet, basename='inscriptions beginning by string')
router.register(rf'{endpoint}/inscription-contributors', views.ContributorsViewSet, basename='contributors to inscription')
# router.register(rf'{endpoint}/description', views.DescriptionViewSet, basename='description')
# router.register(rf'{endpoint}/translation', views.TranslationViewSet, basename='translation')
router.register(rf'{endpoint}/annotation', views.AnnotationViewSet, basename='annotations')
router.register(rf'{endpoint}/inscription-tags', views.InscriptionTagsViewSet, basename="tags for inscriptions")

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('inscriptions', endpoint, 
        exclude=['panel', 'image','inscription', 'translation', 'description', 'objectrti', 'objectmesh3d']),

    *utils.get_model_urls('inscriptions', f'{endpoint}', exclude=['panel', 'image', 'inscription', 'translation', 'description', 'objectrti', 'objectmesh3d']),
    *documentation
]
