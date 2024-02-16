from django.urls import path, include
from rest_framework import routers
from . import views
import saintsophia.utils as utils


router = routers.DefaultRouter()
endpoint = utils.build_app_endpoint("inscriptions")
documentation = utils.build_app_api_documentation("inscriptions", endpoint)

router.register(rf'{endpoint}/panel', views.PanelViewSet, basename='panels information')
router.register(rf'{endpoint}/image', views.IIIFImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),

    # Automatically generated views
    *utils.get_model_urls('inscriptions', endpoint, 
        exclude=['panel', 'image']),

    *utils.get_model_urls('inscriptions', f'{endpoint}', exclude=['place']),
    *documentation
]
